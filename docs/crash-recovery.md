# Recover from a full cluster crash

A full cluster crash happens when the majority of members in a cluster with [Group Replication](architecture.md#group-replication) (GR) are down and the group loses quorum. Even if the primary is among the survivors, the group can't vote, so after a short timeout, the primary enters the error state too. A power loss in the data center, deletion of MySQL Pods, or an out-of-memory kill can take down enough members to cause this. After the Pods restart, no member can form the group on its own, because none of them knows if it has the most recent data.

The Operator detects this situation and recovers the cluster automatically if the `spec.mysql.autoRecovery` is set to `true`. This page explains how to recognize a full cluster crash, how to track the recovery, what to do when you disable automatic recovery or when it doesn't succeed, and how the recovery works.

This page applies to clusters with Group Replication, the default replication type. Clusters with [asynchronous replication](architecture.md#asynchronous-replication-tech-preview) don't use this mechanism, and the `mysql.autoRecovery` option has no effect on them. After all MySQL Pods restart, Orchestrator restores the replication topology without manual steps. For details, see [Zero data loss failover in async clusters](failover-async.md). 

!!! note

    Pausing a cluster with Group Replication and starting it again goes through the same recovery, because all members stop at the same time. See [Pause/resume the cluster](pause.md). Keep automatic recovery enabled, or be ready to follow the [manual steps](#recover-the-cluster-manually) after every resume.

## Symptoms

A cluster is in a full cluster crash when you see the following:

* `kubectl get ps <cluster-name> -n <namespace>` shows the `error` state, and the cluster condition has the `FullClusterCrashDetected` reason.
* `kubectl describe ps <cluster-name> -n <namespace>` shows the `FullClusterCrashDetected` warning event (`Full cluster crash detected`).
* The log of the `mysql` container in the MySQL Pods contains a message between two `######FULL_CLUSTER_CRASH:<Pod FQDN>######` lines.
* The MySQL Pods are `Ready`, but your applications can't write to the database, because the cluster has no primary.

## Choose what to do

Check whether automatic recovery is enabled:

```bash
kubectl get ps <cluster-name> -n <namespace> -o jsonpath='{.spec.mysql.autoRecovery}'
```

An empty output means that the option isn't set, and the Operator treats it as `false`.

| Situation | What to do |
| --- | --- |
| `mysql.autoRecovery` is `true` | The Operator recovers the cluster. [Track the recovery](#track-the-recovery). |
| `mysql.autoRecovery` is `false` or not set | [Recover the cluster manually](#recover-the-cluster-manually). |
| The recovery doesn't start or keeps failing | [Troubleshoot the recovery](#troubleshoot-the-recovery). |

## Recover the cluster automatically

The `mysql.autoRecovery` option in the Custom Resource controls the automatic recovery. The `deploy/cr.yaml` and `deploy/cr-minimal.yaml` files set it to `true`. If you omit the option in your own Custom Resource, the Operator treats it as `false`, so set it explicitly:

```yaml
spec:
  mysql:
    clusterType: group-replication
    autoRecovery: true
```

The Operator starts the recovery only when all MySQL Pods exist and are `Ready`. Make sure that all Pods are scheduled and running. Because the Pods start one after another and each one restarts once before it becomes `Ready`, the recovery takes several minutes even for a small cluster. Recovery time also depends on the cluster size and the amount of data the members must catch up on.

For the steps that the Operator takes, see [What the Operator does during the automatic recovery](#what-the-operator-does-during-the-automatic-recovery).

### Track the recovery

1. Check the cluster state and conditions:

    ```bash
    kubectl get ps <cluster-name> -n <namespace>
    kubectl get ps <cluster-name> -n <namespace> -o jsonpath='{.status.conditions}'
    ```

    The state is `error` with the reason `FullClusterCrashDetected` while the crash is detected. After the reboot, the state changes to `initializing` while the secondary members restart and rejoin, and then to `ready`.

2. List the events of the cluster:

    ```bash
    kubectl describe ps <cluster-name> -n <namespace>
    ```

    Look for the `FullClusterCrashDetected` warning event (`Full cluster crash detected`) and the `FullClusterCrashRecovered` normal event (`Cluster recovered from full cluster crash`). See [Events](cr-statuses.md#events) for all events.

3. Check the Operator logs. The following messages show the progress:

    ```bash
    kubectl logs deploy/percona-server-mysql-operator -n <namespace> | grep -i "crash recovery"
    ```

    * `Pod is waiting for recovery` - the Operator found the `full-cluster-crash` file in the Pod. The message includes the Pod name and its `GTID_EXECUTED` value.
    * `Cluster is online, restarting crashed members` - the cluster was already online. The Operator then logs `Deleting pod with stale full cluster crash marker` for each Pod that it restarts.
    * `Attempting to reboot cluster from complete outage` - the Operator runs the reboot command on the Pod.
    * `failed to reboot cluster from complete outage` - the reboot failed on this Pod. The Operator tries the next one.
    * `Cluster was successfully rebooted` - the reboot succeeded.
    * `Primary pod detected` and `Deleting secondary pod` - the Operator restarts the secondary members so that they rejoin the cluster.

## Recover the cluster manually

Recover the cluster manually when `mysql.autoRecovery` is `false`, or when the automatic recovery doesn't succeed. In the `false` case, the Operator only writes the following error to its log on every reconciliation:

```{.text .no-copy}
Full cluster crash detected but auto recovery is not enabled.
Enable .spec.mysql.autoRecovery or recover cluster manually
(connect to one of the pods using mysql-shell and run 'dba.rebootClusterFromCompleteOutage() and delete /var/lib/mysql/full-cluster-crash in each pod.').
```

To recover the cluster, do the following:

1. Make sure that all MySQL Pods are running and are `Ready`:

    ```bash
    kubectl get pods -n <namespace> -l app.kubernetes.io/component=database
    ```

2. Optionally, check the `GTID_EXECUTED` value saved in each Pod. The Pod with the most transactions has the most recent data:

    ```bash
    kubectl exec <cluster-name>-mysql-0 -n <namespace> -c mysql -- cat /var/lib/mysql/full-cluster-crash
    kubectl exec <cluster-name>-mysql-1 -n <namespace> -c mysql -- cat /var/lib/mysql/full-cluster-crash
    kubectl exec <cluster-name>-mysql-2 -n <namespace> -c mysql -- cat /var/lib/mysql/full-cluster-crash
    ```

    You can run the reboot on any Pod. MySQL Shell checks all members and starts the group from the one with the most transactions.

3. Get the password of the `root` user from the Secret that you set in the `spec.secretsName` option (`<cluster-name>-secrets` by default):

    ```bash
    kubectl get secret <cluster-name>-secrets -n <namespace> -o jsonpath='{.data.root}' | base64 --decode
    ```

4. Connect to a MySQL Pod using MySQL Shell in JavaScript mode:

    ```bash
    kubectl exec -it <cluster-name>-mysql-0 -n <namespace> -c mysql -- mysqlsh --js -u root -p
    ```

    Enter the password from the previous step when MySQL Shell asks for it. The `--js` flag is required, because MySQL Shell in the container starts in SQL mode by default. Don't pass the password in a `root:<password>@localhost` URI: the generated passwords contain special characters that MySQL Shell rejects in a URI.

5. Reboot the cluster:

    ```javascript
    dba.rebootClusterFromCompleteOutage()
    ```

    MySQL Shell prints `The Cluster was successfully rebooted.` when it finishes. If you run the command on a Pod that doesn't have the most transactions, MySQL Shell reports that it switches over to the instance with the highest GTID set and uses it to start the group. If the command fails with an error, exit and repeat steps 4 and 5 on another Pod.

6. Check that all members are `ONLINE`:

    ```javascript
    dba.getCluster().status()
    ```

    Then exit MySQL Shell with `\quit`.

7. Delete the `full-cluster-crash` file in every Pod. The cluster stays in the `error` state until the file is gone:

    ```bash
    kubectl exec <cluster-name>-mysql-0 -n <namespace> -c mysql -- rm /var/lib/mysql/full-cluster-crash
    kubectl exec <cluster-name>-mysql-1 -n <namespace> -c mysql -- rm /var/lib/mysql/full-cluster-crash
    kubectl exec <cluster-name>-mysql-2 -n <namespace> -c mysql -- rm /var/lib/mysql/full-cluster-crash
    ```

    Delete the file only after the reboot succeeds. If you delete it earlier, the `mysql` containers restart and create the file again.

8. Wait until the cluster reaches the `ready` state:

    ```bash
    kubectl get ps <cluster-name> -n <namespace>
    ```

You don't need to delete the secondary Pods after a manual recovery. MySQL Shell rejoins them to the cluster during the reboot.

## Troubleshoot the recovery

The recovery doesn't start:

* Check that all MySQL Pods exist and are `Ready`. The Operator doesn't act on a partially started cluster and doesn't log anything about the recovery while a Pod is missing. Because Pods start one at a time, a single Pod that can't start blocks all Pods after it. If a Pod is missing, check the events of the StatefulSet:

    ```bash
    kubectl describe statefulset <cluster-name>-mysql -n <namespace>
    ```

* Check the Operator logs for the `Full cluster crash detected but auto recovery is not enabled` error. If you see it, either enable `mysql.autoRecovery` or recover the cluster [manually](#recover-the-cluster-manually).
* Check that the Operator Pod is running. While the Operator is down, `kubectl get ps` shows the last state that the Operator reported, which can be `ready`. The recovery starts after the Operator is back.

The recovery keeps failing:

* Look for the `failed to reboot cluster from complete outage` messages in the Operator logs. They contain the error returned by MySQL Shell.
* Check the log of the `mysql` containers for the reason that the member can't join the group.
* [Recover the cluster manually](#recover-the-cluster-manually) and use the error from MySQL Shell to choose the Pod to run the reboot on.

## How full cluster crash recovery works

### How the Operator detects a full cluster crash

1. MySQL Pods start one at a time: Kubernetes creates the next Pod only after the previous one is `Ready`. Every MySQL Pod tries to find a member of the cluster to join. When it can't reach any peer, the Pod reads its `GTID_EXECUTED` value (the set of global transaction identifiers it has applied) and saves it to the `/var/lib/mysql/full-cluster-crash` file. Then the `mysql` container restarts.
2. The container sees the file at startup and keeps `mysqld` running in read-only mode. It prints a message between two `######FULL_CLUSTER_CRASH:<Pod FQDN>######` lines to its log, where `<Pod FQDN>` is the fully qualified domain name of the Pod, for example, `ps-cluster1-mysql-0.ps-cluster1-mysql.<namespace>.svc.cluster.local`. The message contains the last `GTID_EXECUTED` value of that Pod. The Pods report the `Ready` state in this mode, so that you and the Operator can connect to them.
3. As soon as a `Ready` MySQL Pod has the file, the Operator sets the cluster `status.state` to `error`, adds a condition with the `FullClusterCrashDetected` reason, and records the `FullClusterCrashDetected` warning event. The Operator records this event again on every reconciliation until the crash is resolved.

### What the Operator does during the automatic recovery

When automatic recovery is enabled and all MySQL Pods are `Ready`, the Operator does the following:

1. Asks the Pods that don't have the `full-cluster-crash` file whether the cluster is online. Starting with version 1.3.0, if the cluster is online, the Operator removes the file from the other Pods and restarts these Pods so that they rejoin the cluster. No further steps are needed.
2. If the cluster is not online, picks a Pod with the `full-cluster-crash` file and runs the `dba.rebootClusterFromCompleteOutage()` command from [MySQL Shell :octicons-link-external-16:](https://dev.mysql.com/doc/mysql-shell/8.4/en/) on it. The Operator doesn't compare the `GTID_EXECUTED` values to choose the Pod: MySQL Shell finds the member with the most transactions and uses it to start the group. If the command fails on this Pod, the Operator logs the error and tries the next Pod.
3. After the reboot succeeds, records the `FullClusterCrashRecovered` event and removes the `full-cluster-crash` file from every Pod.
4. Waits for the cluster to elect the primary Pod and deletes all other MySQL Pods. Kubernetes recreates them, and they rejoin the cluster as secondary members.

## Related options and events

* [`mysql.autoRecovery`](operator.md#mysqlautorecovery) - enables or disables the automatic recovery.
* [`FullClusterCrashDetected` condition reason and event](cr-statuses.md#conditions)
* [`FullClusterCrashRecovered` event](cr-statuses.md#events)
* [The `full-cluster-crash` file](datadir-special-files.md#full-cluster-crash) and other special files in the data directory
