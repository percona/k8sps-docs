# Cross-site replication: setup and use

This guide walks you through creating a MySQL InnoDB ClusterSet, verifying replication, performing switchover and failover, and removing replica clusters or the entire ClusterSet.

In this setup both source and replica clusters run Percona Server for MySQL version 8.4 in Kubernetes. Refer to [Implementation specifics](replication.md#implementation-specifics) section for more information about running different Percona Server for MySQL versions and their compatibility for replication.

Before you start, read [Cross-site replication](replication.md) for architecture, requirements, and limitations.

## Prerequisites

* Percona Operator for MySQL **1.2.0** or later installed
* Network connectivity between all MySQL endpoints
* `mysqlsh` version for each cluster must match the MySQL major version it runs
* `yq` utility for parsing YAML or JSON outputs from Kubernetes commands

## Prepare your environment

1. Clone the repository with all manifests and source code by executing the following command:

    ```bash
    git clone -b v{{release}} https://github.com/percona/percona-server-mysql-operator
    ```

2. Export the namespaces of the source and replica clusters:

    ```bash
    export SOURCE_NS=source
    export REPLICA_NS=replica
    ```

3. Create namespaces:
    
    ```bash
    kubectl create namespace source
    kubectl create namespace replica
    ```

## Step 1. Deploy the primary cluster

1. Follow the [quickstart guide](kubectl.md) to install the Operator deployment, if you haven't done it, and deploy Percona Server for MySQL cluster with replication type `group replication`. Let's rename the cluster to `source-cluster` to differentiate them.

    Here's the example configuration:

    ```yaml
    apiVersion: ps.percona.com/v1
    kind: PerconaServerMySQL
    metadata:
      name: source-cluster
    spec:
      crVersion: {{ release }}
      secretsName: source-cluster-secrets
      mysql:
        clusterType: group-replication
        size: 3
        image: percona/percona-server:{{ ps84recommended }}
      proxy:
        haproxy:
          enabled: true
          size: 3
      # The rest of the configuration
    ```

2. Apply the configuration and wait until the cluster is ready:

    ```bash
    kubectl get ps source-cluster -n $SOURCE_NS
    ```

3. Note the InnoDB cluster name from status — you need it for the ClusterSet CR:

    ```bash
    kubectl get ps source-cluster -n $SOURCE_NS -o jsonpath='{.status.innodbClusterName}{"\n"}'
    ```

    ??? example "Sample output"

        ```text
        sourcecluster
        ```

4. Note a reachable endpoint for the primary cluster (Service DNS name, load balancer hostname, or external address). We will use the Primary service. 

    ```bash
    kubectl get services -n $SOURCE_NS
    ```

    ??? example "Sample output"

        ```text
        NAME                        TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                                           AGE
        source-cluster-haproxy         ClusterIP   34.118.234.124   <none>        3306/TCP,3307/TCP,3309/TCP,33060/TCP,33062/TCP    26m
        source-cluster-mysql           ClusterIP   None             <none>        3306/TCP,33062/TCP,33060/TCP,6450/TCP,33061/TCP   26m
        source-cluster-mysql-primary   ClusterIP   34.118.232.78    <none>        3306/TCP,33062/TCP,33060/TCP,6450/TCP,33061/TCP   26m
        source-cluster-mysql-proxy     ClusterIP   None             <none>        3306/TCP,33062/TCP,33060/TCP,6450/TCP,33061/TCP   26m
        source-cluster-mysql-unready   ClusterIP   None             <none>        3306/TCP,33062/TCP,33060/TCP,6450/TCP,33061/TCP   26m
        ```

5. All replica sites must have the same system user credentials as the primary site. To achieve this, export the Secrets object with the user credentials.
    
    * List the Secrets:

        ```bash
        kubectl get secrets -n $SOURCE_NS
        ```

        ??? example "Sample output"

            ```{.text .no-copy}
            internal-source-cluster      Opaque              8      25m
            source-cluster-psuser-root   Opaque              11     25m
            source-cluster-secrets       Opaque              8      25m
            source-cluster-ssl           kubernetes.io/tls   3      25m
            ```

        The Secret with user credentials is `<cluster-name>-secrets`

    * Export the Secret:

        ```bash
        kubectl get secret source-cluster-secrets -n $SOURCE_NS -o yaml > source-secret.yaml
        ```

    * Edit the file. Remove the `annotations`, `creationTimestamp`, `resourceVersion`, `selfLink`, and `uid` metadata fields from the resulting file to make it ready for the replica site. Also change the `namespace` to the namespace of your replica site.

        Use the following scripts:

        ```bash
        yq eval 'del(.metadata.ownerReferences, .metadata.annotations, .metadata.creationTimestamp, .metadata.resourceVersion, .metadata.selfLink, .metadata.uid)' source-secret.yaml > replica-secret.yaml
        yq eval '.metadata.namespace = "replica"' -i replica-secret.yaml
        sed -i '' 's/source-cluster/replica-cluster/g' replica-secret.yaml
        ```

## Step 2. Deploy the replica cluster

1. Follow the [quickstart guide](kubectl.md) to install the Operator deployment in the `replica` namespace. 
2. Create the Secret from the secret file you prepared from the primary cluster:
    
    ```bash
    kubectl apply -f replica-secret.yaml -n $REPLICA_NS
    ```

3. Prepare the Replica cluster configuration:
    
    * Set `spec.mysql.bootstrap.mode` to `manual` so Pod-0 does not form a Group Replication group until the ClusterSet adopts it
    * Reference the Secret you created in the `spec.secretsName` 

    Here's the example configuration:

    ```yaml title="cr-replica.yaml"
    apiVersion: ps.percona.com/v1
    kind: PerconaServerMySQL
    metadata:
      name: replica-cluster
    spec:
      crVersion: {{ release }}
      secretsName: replica-cluster-secrets
      mysql:
        clusterType: group-replication
        size: 3
        image: percona/percona-server:{{ ps84recommended }}
        bootstrap:
          mode: manual
    ```

4. Apply the configuration to create the replica cluster:
    
    ```bash
    kubectl apply -f deploy/cr-replica.yaml -n $REPLICA_NS
    ```
    
    After you apply the Custom Resource manifest, Pod-0 starts but stays **NotReady** — this is expected. The cluster reports the `Initializing` state and the `AwaitingExternalBootstrap` condition appears in its status. Pod-1 and Pod-2 do not start until Pod-0 joins a Group Replication group.

5. Verify the cluster status:

    ```bash
    kubectl get ps replica-cluster -n $REPLICA_NS
    kubectl get pods -l app.kubernetes.io/instance=replica-cluster -n $REPLICA_NS
    ```

6. Note the InnoDB cluster name from status — you need it for the ClusterSet CR:
  
    ```bash
    kubectl get ps replica-cluster -n $REPLICA_NS -o jsonpath='{.status.innodbClusterName}{"\n"}'
    ```

    ??? example "Sample output"
        
        ```text
        replicacluster
        ```

7. Note a reachable endpoint for the replica cluster. We will use the Primary service:

    ```bash
    kubectl get service -n $REPLICA_NS
    ```

    ??? example "Sample output"

        ```text
        NAME                            TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                                           AGE
        replica-cluster-mysql           ClusterIP   None             <none>        3306/TCP,33062/TCP,33060/TCP,6450/TCP,33061/TCP   5m31s
        ```

## Step 3. Restore the data on the replica cluster from source (optional)

By default, the replica cluster receives the data from source via the `clone` recovery method - the Operator uses `mysqlshell` to create a physical snapshot of the dataset from the source and transfer it to the replica. 

For large datasets, a full clone can last long, add load to the `Donor` node and be expensive to retry if something goes wrong. 

Instead of using the `clone` method, make a backup on the primary cluster and restore it on the replica. Then when the replica joins the ClusterSet, it already has the data and the GTID history from the source. So it only receives the binlog changes.

Refer to the [make a backup](backups-ondemand.md) and [restore from a backup on a new cluster](backups-restore-to-new-cluster.md) tutorials for step-by-step instructions.

## Step 4. Create the ClusterSet

Now it's time to link clusters. To do this, configure a `PerconaServerMySQLClusterSet` Custom Resource. 

1. Modify the  [deploy/clusterset.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/clusterset.yaml) template and specify the following:

    * `name` - the name of the ClusterSet
    * `primaryCluster` - the InnoDB name of the primary cluster
    * `credentialsSecret.name` - the name of the Secret with the `clusterset` user credentials
    * `createReplicaClusterOptions.recoveryMethod` — leave `clone` for clean replicas. Change to `incremental` if you [restored the data on the replica from the source](#step-3-restore-the-data-on-the-replica-cluster-from-source-optional).
    * `mysqlshellRunner` — defines the helper Pod image used by the Operator to run MySQL Shell operations. The version must be compatible with the MySQL version you run in your clusters.
    * `clusters` - the list of the ClusterSet members. For each cluster specify its InnoDBCluster name and the endpoint that the Operator will use to reach it. 

    Here's the example configuration:

    === "Clone recovery"  

        ```yaml
        apiVersion: ps.percona.com/v1
        kind: PerconaServerMySQLClusterSet
        metadata:
          name: my-cluster-set
          finalizers:
            - percona.com/clusterset-dissolve
        spec:
          primaryCluster: sourcecluster
          credentialsSecret:
            name: source-cluster-secrets
            key: clusterset
          sslMode: AUTO
          createReplicaClusterOptions:
            recoveryMethod: clone
          mysqlshellRunner:
            image: percona/percona-server:{{ ps84recommended }}
          clusters:
            - innodbClusterName: sourcecluster
              endpoints:
                - host: source-cluster-mysql-primary.source.svc.cluster.local
                  port: 3306
            - innodbClusterName: replicacluster
              endpoints:
                - host: replica-cluster-mysql-0.replica-cluster-mysql.replica.svc.cluster.local
                  port: 3306
        ```

    === "Incremental recovery"  

        ```yaml
        apiVersion: ps.percona.com/v1
        kind: PerconaServerMySQLClusterSet
        metadata:
          name: my-cluster-set
          finalizers:
            - percona.com/clusterset-dissolve
        spec:
          primaryCluster: sourcecluster
          credentialsSecret:
            name: source-cluster-secrets
            key: clusterset
          sslMode: AUTO
          createReplicaClusterOptions:
            recoveryMethod: incremental
          mysqlshellRunner:
            image: percona/percona-server:{{ ps84recommended }}
          clusters:
            - innodbClusterName: sourcecluster
              endpoints:
                - host: source-cluster-mysql-primary.source.svc.cluster.local
                  port: 3306
            - innodbClusterName: replicacluster
              endpoints:
                - host: replica-cluster-mysql-0.replica-cluster-mysql.replica.svc.cluster.local
                  port: 3306
        ```
        
2. Apply the manifest:

    ```bash
    kubectl apply -f clusterset.yaml -n $SOURCE_NS
    ```

    After you apply the manifest, the controller:

    1. Creates the `mysqlshell-runner` Pod
    2. Bootstraps the ClusterSet on the primary with `dba.getCluster().createClusterSet()`
    3. Starts a Job to run `createReplicaCluster()` for the replica with the specified recovery mode
    4. Updates status as replication becomes healthy

3. Monitor progress:

    ```bash
    kubectl get ps-clusterset my-cluster-set -n $SOURCE_NS
    kubectl get ps-clusterset my-cluster-set -n $SOURCE_NS -o yaml
    kubectl get jobs -n $SOURCE_NS | grep my-cluster-set
    kubectl logs -l job-name=<job-name> -n $SOURCE_NS
    ```

When the Job completes, Pod-0 on the replica cluster becomes Ready and Pod-1, Pod-2 join the local Group Replication group automatically.


## Step 5. Verify replication

### Check ClusterSet status

1. Check ClusterSet status:

    ```bash
    kubectl get ps-clusterset my-cluster-set -n $SOURCE_NS
    ```

    ??? example "Sample output"

        ```text
        NAME             PRIMARY     ENDPOINT                              READY   AGE
        my-cluster-set   sourcecluster  source-cluster-mysql-0:3306              True    15m
        ```

2. Inspect full status:

    ```bash
    kubectl describe ps-clusterset my-cluster-set -n $SOURCE_NS 
    ```

    Confirm that:

    * `status.conditions` includes `Ready: True` with reason `ClusterSetHealthy`
    * `status.clusters` shows each member with `clusterRole` (`PRIMARY` or `REPLICA`) and `globalStatus` (`OK` for healthy members)
    * `status.primaryCluster` matches your desired primary

### Check per-cluster status

Run on the replica cluster:

```bash
kubectl get ps replica-cluster -n $REPLICA_NS -o jsonpath='{range .status.conditions[*]}{.type}{": "}{.status}{"\n"}{end}'
```

??? example "Expected output"

    ```text
    Initializing: False
    Ready: True
    ClusterSetReplicationRunning: True
    InnoDBClusterBootstrapped: True
    ```

### Verify data replication

1. Connect to the primary cluster and insert some data:

    1. Identify the primary Pod:
        
        ```bash
        export PRIMARY=$(kubectl get pods -n $SOURCE_NS -l mysql.percona.com/primary=true -o jsonpath='{.items[0].metadata.name}')
        ```

    2. Connect to the primary Pod:

        ```bash
        kubectl exec -it $PRIMARY -n $SOURCE_NS -c mysql -- \
          mysql -uroot -p$(kubectl get secret source-cluster-secrets -n $SOURCE_NS -o jsonpath='{.data.root}' | base64 -d)
        ```
    
    3. Write some data:
        
        ```sql
        CREATE DATABASE IF NOT EXISTS test; 
        CREATE TABLE IF NOT EXISTS test.t1 (id INT PRIMARY KEY); INSERT INTO test.t1 VALUES (1);
        ```

 2. Connect to the replica cluster:

      ```bash 
      kubectl exec -it replica-cluster-mysql-0 -n $REPLICA_NS -c mysql -- \
        mysql -uroot -p$(kubectl get secret replica-cluster-secrets -n $REPLICA_NS -o jsonpath='{.data.root}' | base64 -d) 
      ```

3. Verify that the data is replicated by querying it:
  
    ```sql
    SELECT * FROM test.t1;
    ```

    You should see the same data that you inserted.

## Step 6. Planned switchover

To promote a replica cluster to primary, edit `spec.primaryCluster`:

```bash
kubectl patch ps-clusterset my-cluster-set -n $SOURCE_NS \
  --type=merge -p '{"spec":{"primaryCluster":"replicacluster"}}'
```

The controller:

1. Verifies both clusters are reachable
2. Runs `setPrimaryCluster('replicacluster')` via a Job
3. Sets `SwitchoverInProgress` condition while the Job runs
4. Updates `status.primaryCluster` when complete

To monitor the progress, run:

```bash
kubectl get ps-clusterset my-cluster-set -n $SOURCE_NS -w
kubectl get jobs -n $SOURCE_NS | grep switchover
```

After switchover, writes go to the new primary cluster. The former primary becomes a replica.

## Step 7. Forced failover

Use forced failover only when the current primary cluster is **unreachable** and you accept the risk of split-brain or lost transactions if the old primary is still alive.

1. Confirm the primary is unreachable from the controller's perspective (the `ErrorReconcile: True` condition with the reason `PrimaryUnreachable` may be set).
2. Enable forced failover and change the primary:

```bash
kubectl patch ps-clusterset my-cluster-set -n $SOURCE_NS --type=merge -p '{
  "spec": {
    "primaryCluster": "replicacluster",
    "unsafeFlags": {
      "forcedFailover": true
    }
  }
}'
```

The controller runs `forcePrimaryCluster()`. The old primary cluster is marked **INVALIDATED** in ClusterSet metadata if it comes back online.

!!! warning

    Set `unsafeFlags.forcedFailover` to `true` only when you are certain the old primary cannot recover or accept writes.

To recover an invalidated cluster later, either use MySQL Shell `rejoinCluster()` manually, or remove and recreate the cluster in the ClusterSet.

## Step 8. Remove a replica cluster

Remove a replica by deleting its entry from `spec.clusters[]`.

Removal is **one-way**. You cannot add the same cluster back to the same ClusterSet after removal.

Run the following command to remove a cluster

```bash
kubectl patch ps-clusterset my-cluster-set -n $SOURCE_NS --type=json \
  -p='[{"op": "remove", "path": "/spec/clusters/1"}]'
```

Adjust the index to match the cluster you remove.

The controller:

1. Runs `removeCluster()` for the removed member
2. Dissolves Group Replication on that cluster
3. Lets the per-site Operator re-bootstrap it as a standalone InnoDB Cluster

If the replica is **unreachable**, the removal Job fails unless you opt in to forced removal:

```yaml
spec:
  unsafeFlags:
    forcedClusterRemoval: true
```

!!! warning

    Forced cluster removal abandons any unreplicated transactions on the removed cluster. The cluster may require manual cleanup or a full rebuild.


## Step 9. Delete the ClusterSet

Delete the ClusterSet Custom Resource to stop cross-site replication and dissolve ClusterSet metadata:

```bash
kubectl delete ps-clusterset my-cluster-set -n $SOURCE_NS
```

The `percona.com/clusterset-dissolve` finalizer:

1. Waits for any in-flight `createReplicaCluster` Job to finish
2. Runs `.dissolve()` on the InnoDB ClusterSet 
3. Removes the Custom Resource
4. Updates the `spec.bootstrap.mode` on the replica cluster to `auto`. 

Underlying `PerconaServerMySQL` clusters **continue running** as standalone InnoDB Clusters. The per-site Operator keeps managing them.

If dissolve fails (for example, because the primary is permanently unreachable), the Custom Resource stays with `deletionTimestamp` set. Fix connectivity or resolve the MySQL-side issue, then the finalizer retries automatically.

To delete replica and primary clusters themselves, delete their `PerconaServerMySQL` Custom Resources separately after the ClusterSet is gone.

## Troubleshooting

| Symptom | What to check |
| ------- | ------------- |
| `ClusterSetBootstrapped: False` | Primary endpoint unreachable; verify DNS, firewall, and TLS |
| `ReplicaManagementFailure: True` | Inspect the Job logs: `kubectl logs job/<job-name>` |
| Replica Pod-0 stays NotReady | ClusterSet Job still running, or `createReplicaCluster` failed |
| `Ready: False`, reason `ReplicaNotStandalone` | Target cluster is already in another InnoDB Cluster or ClusterSet |
| Switchover stuck | Check `SwitchoverInProgress` condition and switchover Job status |
| `ErrorReconcile: True`, reason `AccessDenied` | Incorrect password configured on the replica site |
| `ErrorReconcile: True`, reason `PrimaryUnreachable` | Primary cluster is not reachable |
| `ReplicaManagementFailure` | One or more replicas could not be added or removed. See the condition message for exact details. Make sure that your replicas are reachable before removing them. |


For status field reference, see [Custom resource statuses](cr-statuses.md).

