# Change replication type

The Operator deploys Percona Server for MySQL with [group-replication](architecture.md#group-replication) and HAProxy by default.

Starting with Operator 1.3.0, you can change the replication type on a running cluster. The Operator tears down the current topology, recreates the MySQL and proxy workloads, and bootstraps the new type on the existing PersistentVolumeClaims. Users, Secrets, and the HAProxy Service stay in place, so applications keep the same endpoint if they already use HAProxy.

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

When you change `mysql.clusterType` and apply the Custom Resource, the Operator:

1. Detects that the desired type differs from the type on the MySQL StatefulSet.
2. Tears down the current topology:

    * **From Group Replication** — Dissolves the InnoDB Cluster and clears persisted `group_replication_*` variables so nodes do not rejoin the old group.
    * **From async** — Stops and resets replication channels. This step fails if Orchestrator is still enabled.

3. Deletes the MySQL StatefulSet. If HAProxy StatefulSet and
MySQL Router Deployment are enabled, the Operator deletes them
too.
4. Recreates those workloads and bootstraps the new replication type on the existing PVCs.

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

3. Take an [on-demand backup](backups-ondemand.md) so you can restore if the switch does not complete.

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

Wait until the cluster is `ready`. The `REPLICATION` column shows `async`. Orchestrator and HAProxy report ready replicas.

```bash
kubectl get ps $CLUSTER_NAME -n $NAMESPACE
```

### Switch from async to group replication

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

Wait until the cluster is `ready`. The `REPLICATION` column shows `group-replication`. The Orchestrator column is empty.

```bash
kubectl get ps $CLUSTER_NAME -n $NAMESPACE
```

### Verify the switch

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

## Operator 1.2.0 and earlier

Do not use this procedure with Operator 1.3.0 or later. Those versions require the cluster to stay `ready`.

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
