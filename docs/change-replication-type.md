# Change replication type

The Operator deploys Percona Server for MySQL with [group-replication](architecture.md#group-replication) and HAProxy by default.

Starting with Operator 1.3.0, you can change the replication type on a running cluster. The Operator tears down the current topology, recreates the MySQL and proxy workloads, and bootstraps the new type on the existing PersistentVolumeClaims. Users, Secrets, and the HAProxy Service stay in place, so applications keep the same endpoint if they already use HAProxy.

!!! admonition ""

    Changing the replication type on a running cluster is a tech preview. The behavior can change in future releases. Do not use it in production yet. Try it in a test or staging cluster first.

To compare the two types, see [Replication types](architecture.md#replication-types).

In Operator 1.2.0 and earlier, you cannot change the type on a running cluster. [Pause the cluster, change the type, then unpause it](#operator-120-and-earlier).

!!! important

    The switch causes downtime while Pods are deleted and the new topology comes up. It applies to the **entire** cluster. You cannot convert a single Group Replication member into a standalone async replica.


## Change the proxy

HAProxy works with either replication type and is recommended. MySQL Router works only with Group Replication.

You can change from one proxy to another. See [HAProxy](haproxy-conf.md) and [MySQL Router](router-conf.md) for the steps.

## Change the replication type

### Prerequisites

* Percona Operator for MySQL **1.3.0** or later
* The cluster is `ready` and is **not** a member of `PerconaServerMySQLClusterSet`. Dissolving Group Replication on
a ClusterSet member breaks cross-site replication.
* No backup, restore, upgrade, or PVC resize is in progress
* You can accept a maintenance window. Writes fail until the
cluster returns to `ready`.
* Orchestrator is required for async replication. Enable it
when you switch to `async` replication type. Disable it when you
switch to `group-replication`.

### How it works

When you change `mysql.clusterType` and apply the Custom Resource, the Operator compares the new value with the current cluster type in the [`status.clusterType`](cr-statuses.md#perconaservermysql-status) field. 

If the cluster is paused or not `ready`, the Operator waits. `status.clusterType` stays on the current type, and proxies and Orchestrator keep the existing topology.

When the cluster is `ready`, the Operator:

1. Tears down the current topology:

    * **From Group Replication** — Dissolves the InnoDB Cluster and clears persisted `group_replication_*` variables so nodes do not rejoin the old group.
    * **From async** — Stops and resets replication channels. This step fails if the Orchestrator is still enabled.

2. Deletes the MySQL StatefulSet. If the HAProxy StatefulSet and the MySQL Router Deployment are enabled, the Operator deletes them too.
3. Sets `status.clusterType` to the new type, recreates those workloads, and bootstraps the new replication type on the existing PVCs.

The switch is finished when the `status.state` is `ready` and the `status.clusterType` matches the `spec.mysql.clusterType` value in the Custom Resource. While the switch is in progress, the Operator emits the `ClusterTypeSwitchInProgress` condition. The Operator removes that condition when the cluster is `ready` under the new type.

During the switch, the cluster leaves `ready` and application connections drop until HAProxy (or Router) is ready. If you used MySQL Router and switch to async, update connection strings to the HAProxy Service.

After the switch, failover works through the new topology: group membership for
Group Replication, Orchestrator for async.

### Before you start

1. Export the namespace and cluster name:

    ```bash
    export NAMESPACE=<namespace>
    export CLUSTER_NAME=ps-cluster1
    ```

2. Confirm the cluster is `ready`:

    ```bash
    kubectl get ps $CLUSTER_NAME -n $NAMESPACE
    ```

    ??? example "Sample output"

        ```{.text .no-copy}
        NAME          REPLICATION          ENDPOINT                     STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
        ps-cluster1   group-replication    ps-cluster1-haproxy.default  ready   3                      3                 27m
        ```

3. Take an [on-demand backup](backups-ondemand.md) so you can restore if the switch does not complete. If you are switching from async replication, [take the backup from the primary](#take-a-backup-from-the-primary), not from a replica.

4. If you are switching to async and the cluster uses MySQL Router, [enable HAProxy and disable Router](haproxy-conf.md) first. Wait until the cluster is `ready` again.

### Switch from group replication to async

Enable Orchestrator in the same change. Keep HAProxy enabled and disable MySQL Router if it is on.

=== "kubectl patch"

    ```bash
    kubectl patch ps $CLUSTER_NAME -n $NAMESPACE --type=merge --patch '{
      "spec": {
        "mysql": {
          "clusterType": "async"
        },
        "orchestrator": {
          "enabled": true
        },
        "proxy": {
          "haproxy": {
            "enabled": true
          },
          "router": {
            "enabled": false
          }
        }
      }
    }'
    ```

=== "Edit the Custom Resource"

    1. Edit `deploy/cr.yaml`:

        ```yaml
        spec:
          mysql:
            clusterType: async
          orchestrator:
            enabled: true
          proxy:
            haproxy:
              enabled: true
            router:
              enabled: false
        ```

    2. Apply the change:

        ```bash
        kubectl apply -f deploy/cr.yaml -n $NAMESPACE
        ```

Wait until the cluster is `ready` and the `status.clusterType` is `async`. Orchestrator and HAProxy report ready replicas. 

```bash
kubectl get ps $CLUSTER_NAME -n $NAMESPACE
```

See [Verify the switch](#verify-the-switch).

### Switch from async to group replication

!!! warning "Risk of data loss when switching from asynchronous replication to Group Replication"

    Do not switch an asynchronous replication cluster to Group Replication unless every replica has applied all transactions from the primary.

    The Operator does not check replication lag or compare GTID sets before the switch. It creates the new Group Replication cluster on `mysql-0`. If another Pod, such as the asynchronous primary, holds transactions that `mysql-0` does not have, the Operator treats that Pod as diverged and re-creates its data with a clone from `mysql-0`. The clone overwrites the data on that Pod, and the transactions that existed only there are lost without an error.

    Before you switch, [verify that all replicas are caught up](#verify-that-all-replicas-are-caught-up) and [take a backup from the primary](#take-a-backup-from-the-primary). These checks protect the transactions that exist only on the asynchronous primary. If the primary is `mysql-0`, the Operator creates the Group Replication cluster from the primary and the risk does not apply, but run the checks anyway to confirm which Pod is the primary.

#### Verify that all replicas are caught up

1. Stop the applications from writing to the cluster. The GTID sets keep changing while writes continue, so the comparison in the next steps is not reliable.

2. Set the root password and find the primary. The primary Pod prints no replica status:

    ```bash
    export ROOT_PASSWORD=$(kubectl -n $NAMESPACE get secret $CLUSTER_NAME-psuser-root -o jsonpath='{.data.password}' | base64 -d)

    for i in 0 1 2; do
      echo "== $CLUSTER_NAME-mysql-$i"
      kubectl exec -n $NAMESPACE $CLUSTER_NAME-mysql-$i -c mysql -- \
        mysql -uroot -p"$ROOT_PASSWORD" -e "SHOW REPLICA STATUS\G" \
        | grep -E "Replica_IO_Running:|Replica_SQL_Running:|Seconds_Behind_Source:"
    done
    ```

    On each replica, the IO and SQL threads report `Yes`.

3. Read the executed GTID set of the primary. Replace `<primary-index>` with the ordinal of the primary Pod:

    ```bash
    export GTID_PRIMARY=$(kubectl exec -n $NAMESPACE $CLUSTER_NAME-mysql-<primary-index> -c mysql -- \
      mysql -uroot -p"$ROOT_PASSWORD" -N -B -e "SELECT REPLACE(@@GLOBAL.gtid_executed, '\n', '');")
    ```

4. Check that every Pod has applied all transactions of the primary:

    ```bash
    for i in 0 1 2; do
      echo -n "$CLUSTER_NAME-mysql-$i: "
      kubectl exec -n $NAMESPACE $CLUSTER_NAME-mysql-$i -c mysql -- \
        mysql -uroot -p"$ROOT_PASSWORD" -N -B -e "SELECT GTID_SUBSET('$GTID_PRIMARY', @@GLOBAL.gtid_executed);"
    done
    ```

    Every Pod must return `1`. A `0` means that Pod has not applied all transactions from the primary. Wait and repeat the check. If a Pod does not reach `1`, do not switch.

#### Take a backup from the primary

By default, the Operator takes a backup of an asynchronous cluster from a replica. A lagging replica does not contain the transactions that exist only on the primary, so such a backup does not protect them.

Set the `spec.sourcePod` option of the backup to the primary Pod:

```yaml
apiVersion: ps.percona.com/v1
kind: PerconaServerMySQLBackup
metadata:
  name: before-switch
spec:
  clusterName: ps-cluster1
  storageName: s3-us-west
  sourcePod: ps-cluster1-mysql-<primary-index>
```

For all backup options, see the [Backup resource reference](backup-cr.md). Wait until the backup reaches the `Succeeded` state before you continue.

#### Run the switch

Disable Orchestrator in the same change. The Operator refuses the switch while Orchestrator is enabled.

=== "kubectl patch"

    ```bash
    kubectl patch ps $CLUSTER_NAME -n $NAMESPACE --type=merge --patch '{
      "spec": {
        "mysql": {
          "clusterType": "group-replication"
        },
        "orchestrator": {
          "enabled": false
        }
      }
    }'
    ```

=== "Edit the Custom Resource"

    1. Edit `deploy/cr.yaml`:

        ```yaml
        spec:
          mysql:
            clusterType: group-replication
          orchestrator:
            enabled: false
        ```

    2. Apply the change:

        ```bash
        kubectl apply -f deploy/cr.yaml -n $NAMESPACE
        ```

Wait until the cluster is `ready` and the `status.clusterType` is `group-replication`. The Orchestrator column is empty. See [Verify the switch](#verify-the-switch).

### Verify the switch

Confirm the applied type and the cluster state:

```bash
kubectl get ps $CLUSTER_NAME -n $NAMESPACE \
  -o jsonpath='{.status.state}{" "}{.status.clusterType}{"\n"}'
```

The output is `ready` and the type you switched to (`async` or `group-replication`).

??? example "Sample output"

    ```{.text .no-copy}
    ready async
    ```

Check whether the switch is still in progress:

```bash
kubectl get ps $CLUSTER_NAME -n $NAMESPACE \
  -o jsonpath='{range .status.conditions[?(@.type=="ClusterTypeSwitchInProgress")]}{.type}{": "}{.status}{"\n"}{end}'
```

A finished switch returns no output.

Connect through HAProxy as described in [Connect to Percona Server for MySQL](connect.md) and query a known table.

Optional. Confirm the new topology from inside a MySQL Pod.

Inspect the connection secret and extract the password:

```bash
PWD=$(kubectl -n $NAMESPACE get secret $CLUSTER_NAME-psuser-root -o jsonpath='{.data.password}' | base64 -d)
```

=== "Group replication"

    ```bash
    kubectl exec -it -n $NAMESPACE $CLUSTER_NAME-mysql-0 -c mysql -- \
      mysql -uroot -p"$PWD" -e "SELECT member_host, member_state, member_role FROM performance_schema.replication_group_members;"
    ```

    ??? example "Sample output"

        ```{.text .no-copy}
        +-----------------------------------------------+--------------+-------------+
        | member_host                                   | member_state | member_role |
        +-----------------------------------------------+--------------+-------------+
        | ps-cluster1-mysql-1.ps-cluster1-mysql.psmysql | ONLINE       | SECONDARY   |
        | ps-cluster1-mysql-2.ps-cluster1-mysql.psmysql | ONLINE       | SECONDARY   |
        | ps-cluster1-mysql-0.ps-cluster1-mysql.psmysql | ONLINE       | PRIMARY     |
        +-----------------------------------------------+--------------+-------------+
        ```

=== "Asynchronous replication"

    ```bash
    kubectl exec -it -n $NAMESPACE $CLUSTER_NAME-mysql-0 -c mysql -- \
      mysql -uroot -p"$PWD" -e "SHOW REPLICA STATUS\G"
    ```

    On the primary, replica status is empty. On replicas, the IO and SQL threads should report `Yes`.

## Known limitations

1. When you switch from async replication to Group Replication, the Operator does not verify that the replicas are caught up. If another Pod holds transactions that `mysql-0` does not have, the Operator overwrites that Pod with a clone from `mysql-0`, and those transactions are lost. Until the Operator checks this itself, [verify the GTID sets](#verify-that-all-replicas-are-caught-up) and [take a backup from the primary](#take-a-backup-from-the-primary) before you switch.

2. If you switch from group replication to async and the Operator fails to bootstrap the new topology, you cannot switch the cluster back to group replication.

    The Operator sets `status.clusterType` to `async` when it deletes the old workloads, before it finishes that bootstrap. If the bootstrap fails, the MySQL Pods cannot accept the connections the Operator needs to tear the async setup down. Setting `mysql.clusterType` back to `group-replication` does not restore the previous topology, and the cluster stays out of `ready`.

    This limitation is known and will be fixed in a later release. [Restore the cluster](backups-restore.md) from the backup you took before the switch.

## Operator 1.2.0 and earlier

This procedure applies to Operator 1.2.0 or earlier. 

!!! warning

    The data loss risk described for [the switch from async to group replication](#switch-from-async-to-group-replication) applies to this procedure too. Complete the checks in [Verify that all replicas are caught up](#verify-that-all-replicas-are-caught-up) and [Take a backup from the primary](#take-a-backup-from-the-primary) before you pause the cluster. 

1. [Pause](pause.md) the cluster:

    ```bash
    kubectl patch ps $CLUSTER_NAME -n $NAMESPACE --type json -p='[{"op":"add","path":"/spec/pause","value":true}]'
    ```

2. Edit `deploy/cr.yaml` and set `mysql.clusterType` to `async`. Keep HAProxy enabled.

    ```yaml
    mysql:
      clusterType: async
      ...
    proxy:
      haproxy:
        enabled: true
        ...
    ```

3. Apply the configuration and unpause the cluster:

    ```bash
    kubectl apply -f deploy/cr.yaml -n $NAMESPACE
    kubectl patch ps $CLUSTER_NAME -n $NAMESPACE --type json -p='[{"op":"add","path":"/spec/pause","value":false}]'
    ```

4. Wait until the cluster is resumed:

    ```bash
    kubectl get ps -n $NAMESPACE
    ```
