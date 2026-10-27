# Recover from a full cluster crash

A full cluster crash happens when all members of a cluster with [Group Replication](architecture.md#group-replication) (GR) go down at the same time. This can be a power loss in the data center, deletion of all MySQL Pods at once, or an out-of-memory kill that hits every node. After the Pods restart, no member can form the group on its own, because none of them knows if it has the most recent data.

The Operator detects this situation and, by default, recovers the cluster automatically. This page explains how the Operator does it, how to track the recovery, and what to do when you disable automatic recovery or when it doesn't succeed.

This page applies to clusters with Group Replication, the default replication type. Clusters with [asynchronous replication](architecture.md#asynchronous-replication-tech-preview) don't use this mechanism. For them, see [Zero data loss failover in async clusters](failover-async.md).

!!! note

    Pausing a cluster with Group Replication and starting it again goes through the same recovery, because all members stop at the same time. See [Pause/resume the cluster](pause.md). Keep automatic recovery enabled, or be ready to follow the [manual steps](#recover-the-cluster-manually) after every resume.

## How the Operator detects a full cluster crash

1. Every MySQL Pod starts and tries to find a member of the cluster to join. When it can't reach any peer, the Pod reads its `GTID_EXECUTED` value (the set of global transaction identifiers it has applied) and saves it to the `/var/lib/mysql/full-cluster-crash` file. Then the `mysql` container restarts.
2. The container sees the file at startup and keeps `mysqld` running in read-only mode. It prints a message between the `######FULL_CLUSTER_CRASH:<Pod name>######` lines to its log. The message contains the last `GTID_EXECUTED` value of that Pod. The Pods report the `Ready` state in this mode, so that you and the Operator can connect to them.
3. When all MySQL Pods exist and are `Ready`, the Operator looks for the file in each Pod. If the file exists, the Operator sets the cluster `status.state` to `error` with the `FullClusterCrashDetected` condition reason, and records the `FullClusterCrashDetected` warning event.

Until recovery completes, the cluster has no primary, and your applications can't write to the database. The Operator waits and doesn't start recovery while at least one Pod is missing or isn't `Ready`. Make sure that all Pods are scheduled and running.

## Recover the cluster automatically

The `mysql.autoRecovery` option in the Custom Resource controls the automatic recovery. The `deploy/cr.yaml` and `deploy/cr-minimal.yaml` files set it to `true`. If you omit the option in your own Custom Resource, the Operator treats it as `false`, so set it explicitly:

```yaml
spec:
  mysql:
    clusterType: group-replication
    autoRecovery: true
```

When automatic recovery is enabled, the Operator does the following:

1. Asks the Pods that don't have the `full-cluster-crash` file whether the cluster is online. Starting with version 1.3.0, if the cluster is online, the Operator removes the file from the other Pods and restarts these Pods so that they rejoin the cluster. No further steps are needed.
2. If the cluster is not online, picks a Pod with the `full-cluster-crash` file and runs the `dba.rebootClusterFromCompleteOutage()` command from [MySQL Shell :octicons-link-external-16:](https://dev.mysql.com/doc/mysql-shell/8.4/en/) on it. If this Pod can't be used to reboot the cluster, the Operator logs the error and tries the next Pod.
3. After the reboot succeeds, records the `FullClusterCrashRecovered` event and removes the `full-cluster-crash` file from every Pod.
4. Waits for the cluster to elect the primary Pod and deletes all other MySQL Pods. Kubernetes recreates them, and they rejoin the cluster as secondary members.

Recovery time depends on the cluster size, the amount of data the members must catch up on, and how fast Kubernetes restarts the Pods.

### Track the recovery

1. Check the cluster state and conditions:

    ```bash
    kubectl get ps <cluster-name> -n <namespace>
    kubectl get ps <cluster-name> -n <namespace> -o jsonpath='{.status.conditions}'
    ```

    The state is `error` with the reason `FullClusterCrashDetected` while the crash is detected, and `ready` after the recovery.

2. List the events of the cluster:

    ```bash
    kubectl describe ps <cluster-name> -n <namespace>
    ```

    Look for the `FullClusterCrashDetected` and `FullClusterCrashRecovered` events. See [Events](cr-statuses.md#events) for all events.

3. Check the Operator logs. The following messages show the progress:

    ```bash
    kubectl logs deploy/percona-server-mysql-operator -n <namespace> | grep -i "crash recovery"
    ```

    * `Pod is waiting for recovery` - the Operator found the `full-cluster-crash` file in the Pod. The message includes the `GTID_EXECUTED` value of that Pod.
    * `Attempting to reboot cluster from complete outage` - the Operator runs the reboot command on the Pod.
    * `Cluster was successfully rebooted` - the reboot succeeded.
    * `failed to reboot cluster from complete outage` - the reboot failed on this Pod. The Operator tries the next one.
    * `Cluster is online, restarting crashed members` - the cluster was already online, and the Operator restarts the Pods that have a stale `full-cluster-crash` file.

## Recover the cluster manually

Recover the cluster manually when `mysql.autoRecovery` is `false`, or when the automatic recovery doesn't succeed. In the `false` case, the Operator only writes an error to its log. The error says that automatic recovery is not enabled and lists the manual steps.

1. Make sure that all MySQL Pods are running and are `Ready`:

    ```bash
    kubectl get pods -n <namespace> -l app.kubernetes.io/component=mysql
    ```

2. Check the `GTID_EXECUTED` value saved in each Pod. The Pod with the most transactions has the most recent data:

    ```bash
    kubectl exec <cluster-name>-mysql-0 -n <namespace> -c mysql -- cat /var/lib/mysql/full-cluster-crash
    kubectl exec <cluster-name>-mysql-1 -n <namespace> -c mysql -- cat /var/lib/mysql/full-cluster-crash
    kubectl exec <cluster-name>-mysql-2 -n <namespace> -c mysql -- cat /var/lib/mysql/full-cluster-crash
    ```

3. Get the password of the `root` user from the Secret that you set in the `spec.secretsName` option (`<cluster-name>-secrets` by default):

    ```bash
    kubectl get secret <cluster-name>-secrets -n <namespace> -o jsonpath='{.data.root}' | base64 --decode
    ```

4. Connect to the Pod with the most recent data using MySQL Shell. Replace `<password>` with the value from the previous step:

    ```bash
    kubectl exec -it <cluster-name>-mysql-0 -n <namespace> -c mysql -- mysqlsh root:<password>@localhost
    ```

5. Reboot the cluster. MySQL Shell starts in JavaScript mode, so run the command as is:

    ```javascript
    dba.rebootClusterFromCompleteOutage()
    ```

    If MySQL Shell reports that this instance isn't suitable for the reboot, exit and repeat steps 4 and 5 on another Pod.

6. Exit MySQL Shell and delete the `full-cluster-crash` file in every Pod. The Pods stay in the read-only crash mode until the file is gone:

    ```bash
    kubectl exec <cluster-name>-mysql-0 -n <namespace> -c mysql -- rm /var/lib/mysql/full-cluster-crash
    kubectl exec <cluster-name>-mysql-1 -n <namespace> -c mysql -- rm /var/lib/mysql/full-cluster-crash
    kubectl exec <cluster-name>-mysql-2 -n <namespace> -c mysql -- rm /var/lib/mysql/full-cluster-crash
    ```

7. Delete the MySQL Pods that are not the primary, the same as the Operator does during the automatic recovery. Find the primary Pod first:

    ```bash
    kubectl exec <cluster-name>-mysql-0 -n <namespace> -c mysql -- mysqlsh root:<password>@localhost --js -e "print(dba.getCluster().status())"
    ```

    Then delete the other Pods, for example:

    ```bash
    kubectl delete pod <cluster-name>-mysql-1 <cluster-name>-mysql-2 -n <namespace>
    ```

8. Wait until all Pods are `Ready` and the cluster reaches the `ready` state:

    ```bash
    kubectl get ps <cluster-name> -n <namespace>
    ```

## Troubleshoot the recovery

The recovery doesn't start:

* Check that all MySQL Pods exist and are `Ready`. The Operator doesn't act on a partially started cluster.
* Check the Operator logs for the `Full cluster crash detected but auto recovery is not enabled` error. If you see it, either enable `mysql.autoRecovery` or recover the cluster [manually](#recover-the-cluster-manually).

The recovery keeps failing:

* Look for the `failed to reboot cluster from complete outage` messages in the Operator logs. They contain the error returned by MySQL Shell.
* Check the log of the `mysql` containers for the reason that the member can't join the group.
* [Recover the cluster manually](#recover-the-cluster-manually) and use the error from MySQL Shell to choose the Pod to run the reboot on.

## Related options and events

* [`mysql.autoRecovery`](operator.md#mysqlautorecovery) - enables or disables the automatic recovery.
* [`FullClusterCrashDetected` condition reason and event](cr-statuses.md#conditions)
* [`FullClusterCrashRecovered` event](cr-statuses.md#events)
* [The `full-cluster-crash` file](datadir-special-files.md#full-cluster-crash) and other special files in the data directory
