# Custom resource statuses

Status fields show the current state of a Custom Resource. The Operator sets these fields in the `.status` section of a Custom Resource. You do not edit the status.

Use status values to confirm progress, detect failures, and decide when it is safe to run the next action (for example, start a restore after a backup succeeds, or perform switchover after the ClusterSet is `Ready`).

## How to view custom resource statuses

To check the status of custom resources, use the `kubectl get` or `kubectl describe` commands. See how to use them to get the quick overview, in-depth details, and targeted queries.

### Get a quick overview

List your resources and check their high-level status:

```bash
kubectl get ps <cluster-name> -n <namespace>
kubectl get ps-clusterset <clusterset-name> -n <namespace>
kubectl get ps-backup <backup-name> -n <namespace>
kubectl get ps-restore <restore-name> -n <namespace>
```

??? example "Sample output for `PerconaServerMySQL`"

    ```text
    NAME          REPLICATION          ENDPOINT                              STATE   MYSQL   HAPROXY   AGE
    ps-cluster1   group-replication    ps-cluster1-haproxy.default:3306      ready   3       1         27m
    ```

### View full details

See all status details, conditions, and events:

```bash
kubectl get ps <cluster-name> -n <namespace> -o yaml
kubectl describe ps <cluster-name> -n <namespace>

kubectl get ps-clusterset <clusterset-name> -n <namespace> -o yaml
kubectl describe ps-clusterset <clusterset-name> -n <namespace>

kubectl get ps-backup <backup-name> -n <namespace> -o yaml
kubectl get ps-restore <restore-name> -n <namespace> -o yaml
```

Check for the `.status` field in the output to find the current state, readiness, messages, and conditions.

### Query a status field directly

You can extract specific status fields using `jsonpath`.

**Example 1. Get the InnoDB cluster name (for ClusterSet configuration):**

```bash
kubectl get ps <cluster-name> -n <namespace> \
  -o jsonpath='{.status.innodbClusterName}{"\n"}'
```
 
??? example "Sample output"
    
    ```text
    pscluster1
    ```

**Example 2. Check whether the ClusterSet is ready:**

```bash
kubectl get ps-clusterset <clusterset-name> -n <namespace> \
  -o jsonpath='{range .status.conditions[?(@.type=="Ready")]}{.status}{": "}{.reason}{"\n"}{end}'
```

??? example "Sample output"

    ```text
    True: ClusterSetHealthy
    ```

**Example 3. Get the backup destination path:**

```bash
kubectl get ps-backup <backup-name> -n <namespace> \
  -o jsonpath='{.status.destination}{"\n"}'
```

??? example "Sample output"
    
    ```text
    s3://<my-bucket>/ps-cluster1-2026-06-29-08:06:10-full
    ```

## PerconaServerMySQL status

The main cluster state is recorded in the `status.state` field. Component-level states are recorded in the `status.mysql`, `status.haproxy`, `status.router`, `status.orchestrator`, and `status.binlogserver` sections.

Common fields:

* `status.state` — overall cluster state
* `status.host` — connection endpoint
* `status.innodbClusterName` — InnoDB cluster name reported by MySQL Shell
* `status.mysql.ready` / `status.mysql.size` — number of ready MySQL Pods and the desired size of the database cluster
* `status.conditions` — detailed condition list with reason and message

### Cluster state values

`status.state` values are:

| Value | Meaning |
| ----- | ------- |
| `""` | The Operator has not set a state yet. |
| `initializing` | The Operator is creating or reconciling the cluster. |
| `stopping` | The Operator is stopping or scaling down cluster components. |
| `paused` | The cluster is paused. |
| `ready` | The cluster is up and healthy. |
| `error` | The Operator detected an error; check conditions and events. |

The same state values apply to each component subsection (`status.mysql.state`, `status.haproxy.state`, etc.).

### Conditions

Conditions show more detail about cluster state changes. You can see them in `status.conditions[]`.

Common condition fields:

* `type` — condition type
* `status` — condition status (`True`, `False`, or `Unknown`)
* `reason` — short reason string
* `message` — human-readable details

`status.conditions[].type` values:

| Value | Meaning |
| ----- | ------- |
| `Initializing` | The cluster or a component is starting up. |
| `Ready` | The cluster or a component is ready. |
| `Error` | The Operator detected an error (for example, full cluster crash). |
| `InnoDBClusterBootstrapped` | The InnoDB Cluster metadata exists and Group Replication is formed. |
| `AwaitingExternalBootstrap` | The cluster is configured with `spec.mysql.bootstrap.mode: manual` and waits for an external actor (typically the ClusterSet controller) to bootstrap Group Replication. |
| `ClusterSetReplicationRunning` | The cluster is a REPLICA member of an InnoDB ClusterSet and async replication from the primary cluster is active. |

`status.conditions[].status` values:

| Value | Meaning |
| ----- | ------- |
| `True` | The condition is currently true. |
| `False` | The condition is currently false. |
| `Unknown` | The Operator has not determined the condition yet. |

The Operator sets `reason` and `message` as free-form strings. Common reasons include `ManualBootstrapRequested`, `ClusterSetReplicationRunning`, `FullClusterCrashDetected`, and state names such as `Initializing` and `Ready`.

## PerconaServerMySQLClusterSet status

ClusterSet progress and topology are reflected in `status.primaryCluster`, `status.clusters`, and `status.conditions`.

Common fields are:

* `status.primaryCluster` — the cluster currently serving as the ClusterSet primary (observed; may lag `spec.primaryCluster` briefly during switchover)
* `status.primaryClusterEndpoint` — host:port of the global primary instance
* `status.clusters` — map of member clusters keyed by `innodbClusterName`, mirroring MySQL Shell `.status()` output
* `status.conditions` — ClusterSet-level conditions
* `status.lastObservedAt` — timestamp of the last successful status refresh
* `status.lastObservedGeneration` — generation last reconciled

### Per-member cluster status

Each entry in `status.clusters[<innodbClusterName>]` contains:

| Field | Meaning |
| ----- | ------- |
| `clusterRole` | `PRIMARY` or `REPLICA` as observed by MySQL Shell |
| `globalStatus` | Member health in the ClusterSet |
| `primary` | Host:port of the cluster's local group replication primary |

`globalStatus` values (from MySQL Shell):

| Value | Meaning |
| ----- | ------- |
| `OK` | Cluster is healthy and replicating as expected. |
| `OK_NOT_REPLICATING` | Cluster is reachable but not currently replicating (transitional or misconfigured). |
| `NOT_OK` | Cluster has a problem; check MySQL Shell status and events. |
| `INVALIDATED` | Cluster was fenced off after forced failover; may have divergent GTIDs. Requires running `rejoinCluster()` manually if GTIDs are compatible. Otherwise, the INVALIDATED cluster must be removed and recreated to rejoin the ClusterSet. |
| `UNKNOWN` | Status could not be determined. |

### Conditions

`status.conditions[].type` values:

| Value | Meaning |
| ----- | ------- |
| `Ready` | ClusterSet is formed and replicas are replicating from the specified primary. |
| `ClusterSetBootstrapped` | The primary cluster is configured as a ClusterSet. |
| `MySQLShellRunnerReady` | The `mysqlshell-runner` Pod is running and ready. |
| `SwitchoverInProgress` | `spec.primaryCluster` differs from the observed primary and a switchover Job is running or pending. |
| `ErrorReconcile | An error occurred during reconciliation |  
| `ReplicaManagementFailure` | A replica add/remove Job failed; see the Job logs. |
| `ClusterSetDissolving` | The Custom Resource is being deleted and the dissolve finalizer is running. |

Common `Ready` condition reasons:

| Reason | Meaning |
| ------ | ------- |
| `ClusterSetHealthy` | MySQL Shell reports overall ClusterSet status as healthy. |
| `ClusterSetNotHealthy` | One or more members are not healthy; see `status.clusters` and condition message. |
| `PrimaryUnreachable` | Primary cluster is not reachable |
| `AccessDenied` | Incorrect password configured on the replica site |

### Events

The ClusterSet controller emits Kubernetes events you can view with `kubectl describe ps-clusterset`:

| Event reason | Meaning |
| ------------ | ------- |
| `ClusterSetBootstrapped` | ClusterSet was created on the primary cluster. |
| `ClusterSetPrimarySwitched` | Planned switchover completed. |
| `ClusterSetPrimaryForcedSwitched` | Forced failover completed. |
| `ClusterSetMemberAdded` | A cluster was added to the ClusterSet. |
| `ClusterSetMemberRemoved` | A cluster was removed from the ClusterSet. |
| `ClusterSetHealthDegraded` | Overall ClusterSet health dropped from healthy to unhealthy. |

## PerconaServerMySQLBackup status

Backup progress and results are in `status.state`. You also get destination and timing details that help you validate backups and incremental chains.

Common fields:

* `status.state` — backup job state
* `status.type` — backup type (`full` or `incremental`)
* `status.destination` — backup path or URL
* `status.completed` — completion timestamp
* `status.stateDescription` — error details when the backup fails
* `status.backupSource` — source pod or path used for the backup
* `status.conditions` — additional conditions

### Backup state values

`status.state` values are:

| Value | Meaning |
| ----- | ------- |
| `""` | Backup is created but not processed yet. |
| `Starting` | Backup is starting. |
| `Running` | Backup is in progress. |
| `Succeeded` | Backup completed successfully. |
| `Error` | Backup failed to start. |
| `Failed` | Backup started but failed during execution. |

### Conditions

| Value | Meaning |
| ----- | ------- |
| `BackupLeaseAcquired` | The backup job holds the cluster backup lease and is authorized to run. |

## PerconaServerMySQLRestore status

Restore progress and results are in `status.state`. Use these fields to confirm when a restore starts, finishes, or fails.

Common fields:

* `status.state` — restore job state
* `status.stateDescription` — error details when the restore fails
* `status.completed` — completion timestamp
* `status.backupSource` — backup metadata used for the restore (when restoring from an existing backup object)

### Restore state values

`status.state` values are:

| Value | Meaning |
| ----- | ------- |
| `""` | Restore is created but not processed yet. |
| `Starting` | Restore is starting. |
| `Running` | Restore is in progress. |
| `Succeeded` | Restore completed successfully. |
| `Error` | Restore failed to start. |
| `Failed` | Restore started but failed during execution. |

