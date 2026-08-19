# Custom resource statuses

Status fields show the current state of a Custom Resource (CR). The Operator sets these fields in the `.status` section of a Custom Resource. You do not edit the status.

Use `.status` values to confirm progress, detect failures, and decide when it is safe to run the next action. For example, start a restore after a backup succeeds, or perform switchover after the ClusterSet is `Ready`.

## How to view Custom Resource statuses

To check the status of your Percona Custom Resources, use the `kubectl get <resource-type>` or `kubectl describe <resource-type>` commands. See how to use them to get the quick overview, in-depth details, and targeted queries.

### Get a quick overview

List your resources and check their high-level status:

```bash
kubectl get ps -n <namespace>
kubectl get ps-clusterset -n <namespace>
kubectl get ps-backup -n <namespace>
kubectl get ps-restore -n <namespace>
```

??? example "Sample output for PerconaServerMySQL"

    ```{.text .no-copy}
    NAME          REPLICATION          ENDPOINT                              STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
    ps-cluster1   group-replication    ps-cluster1-haproxy.default           ready   3                      3                 27m
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

    ```{.text .no-copy}
    pscluster1
    ```

**Example 2. Check whether the ClusterSet is ready:**

```bash
kubectl get ps-clusterset <clusterset-name> -n <namespace> \
  -o jsonpath='{range .status.conditions[?(@.type=="Ready")]}{.status}{": "}{.reason}{"\n"}{end}'
```

??? example "Sample output"

    ```{.text .no-copy}
    True: ClusterSetHealthy
    ```

**Example 3. Get the backup destination path:**

```bash
kubectl get ps-backup <backup-name> -n <namespace> \
  -o jsonpath='{.status.destination}{"\n"}'
```

??? example "Sample output"

    ```{.text .no-copy}
    s3://<my-bucket>/ps-cluster1-2026-06-29-08:06:10-full
    ```

## PerconaServerMySQL status

The main cluster state is recorded in `status.state`. Component-level states are recorded in the `status.mysql`, `status.haproxy`, `status.router`, `status.orchestrator`, and `status.binlogserver` sections. A component subsection is populated only when that component is enabled.

Common fields:

* `status.state` — overall cluster state
* `status.host` — connection endpoint (proxy Service, LoadBalancer address, or MySQL Service)
* `status.innodbClusterName` — InnoDB cluster name derived from the Custom Resource name (non-alphanumeric characters stripped). Use this value in the [ClusterSet Custom Resource](clusterset-cr.md#specclustersinnodbclustername)
* `status.mysql.ready` / `status.mysql.size` — number of ready MySQL Pods and the desired size
* `status.mysql.state` — MySQL component state
* `status.haproxy` / `status.router` / `status.orchestrator` / `status.binlogserver` — the same `ready`, `size`, `state`, and `version` fields for each component
* `status.storageAutoscaling` — per-PVC autoscaling progress when [automatic storage scaling](scaling.md#scale-storage) is enabled
* `status.conditions` — detailed condition list with reason and message. See [Conditions](#conditions)

The overall `status.state` stays `initializing` until:

* every enabled component is ready, 
* Group Replication members are `ONLINE` (for `group-replication` clusters) or asynchronous replication has no Orchestrator problems (for `async` clusters), 
* point-in-time recovery's binlog server is ready when enabled, 
* any LoadBalancer Services have an assigned address.

### Cluster state values

`status.state` values are:

| Value | Meaning |
| --- | --- |
| `""` | The Operator has not set a state yet. |
| `initializing` | The Operator is creating or reconciling the cluster. |
| `stopping` | The Operator is stopping or scaling down cluster components (`spec.pause: true` and some Pods are still ready). |
| `paused` | The cluster is paused and no component Pods are ready. |
| `ready` | The cluster is up and healthy. |
| `error` | The Operator detected an error; check conditions and events. |

The same state values apply to each component subsection (`status.mysql.state`, `status.haproxy.state`, and so on).

### Conditions

Conditions show more detail about cluster state changes. You can see them in `status.conditions[]`.

Common condition fields:

* `type` — condition type
* `status` — condition status
* `reason` — short reason string
* `message` — human-readable details

`status.conditions[].type` values:

| Value | Meaning |
| --- | --- |
| `Initializing` | The cluster or a component is starting up. |
| `Ready` | The cluster or a component is ready. |
| `Error` | The Operator detected an error (for example, a reconcile failure or a full cluster crash). |
| `InnoDBClusterBootstrapped` | The InnoDB Cluster metadata exists and Group Replication is formed. |
| `AwaitingExternalBootstrap` | The cluster is configured with `spec.mysql.bootstrap.mode: manual` and waits for an external actor (typically the ClusterSet controller) to bootstrap Group Replication. |
| `ClusterSetReplicationRunning` | The cluster is a `REPLICA` member of an InnoDB ClusterSet and async replication from the primary cluster is active. |

`status.conditions[].status` values:

| Value | Meaning |
| --- | --- |
| `True` | The condition is currently true. |
| `False` | The condition is currently false. |
| `Unknown` | The Operator has not determined the condition yet. |

The Operator sets `reason` and `message` as free-form strings. Common reasons include:

* `Initializing`, `Ready` (matching the cluster state)
* `ErrorReconcile` — cluster reconciliation failed; see the condition message
* `FullClusterCrashDetected` — all Group Replication members have crash recovery files
* `ManualBootstrapRequested` — the cluster is waiting for external bootstrap
* `ClusterSetReplicationRunning` — ClusterSet replica replication is active
* `InnoDBClusterBootstrapped` — InnoDB Cluster metadata exists

### Storage autoscaling status

When you enable [storage autoscaling](scaling.md#scale-storage), the Operator records per-PVC progress in `status.storageAutoscaling.<pvc-name>`:

| Field | Meaning |
| --- | --- |
| `currentSize` | Observed PVC size |
| `lastResizeTime` | Timestamp of the last expansion |
| `resizeCount` | Number of expansions |
| `lastError` | Last autoscaling error, if any |

### Events

The cluster controller emits Kubernetes events you can view with `kubectl describe ps`:

| Event reason | Meaning |
| --- | --- |
| `ClusterStateChanged` | `status.state` changed (for example, `initializing` → `ready`). |
| `ReconcileError` | Cluster reconciliation failed. |
| `FullClusterCrashDetected` | A full Group Replication cluster crash was detected. |
| `AsyncReplicationNotReady` | Orchestrator reported replication problems on one or more instances. |
| `StorageAutoscalingTriggered` | Storage autoscaling started a PVC resize. |

## PerconaServerMySQLClusterSet status

ClusterSet progress and topology are reflected in `status.primaryCluster`, `status.clusters`, and `status.conditions`. For configuration options, see [ClusterSet Resource options](clusterset-cr.md). For setup, see [Set up cross-site replication](replication-setup.md).

Common fields:

* `status.primaryCluster` — the cluster currently serving as the ClusterSet primary (observed; may lag `spec.primaryCluster` briefly during switchover)
* `status.primaryClusterEndpoint` — `host:port` of the global primary instance
* `status.clusters` — map of member clusters keyed by `innodbClusterName`, mirroring MySQL Shell `.status()` output
* `status.conditions` — ClusterSet-level conditions
* `status.lastObservedAt` — timestamp of the last successful status refresh
* `status.lastObservedGeneration` — generation last reconciled

### Per-member cluster status

Each entry in `status.clusters[<innodbClusterName>]` contains:

| Field | Meaning |
| --- | --- |
| `clusterRole` | `PRIMARY` or `REPLICA` as observed by MySQL Shell |
| `globalStatus` | Member health in the ClusterSet |
| `primary` | Host:port of the cluster's local Group Replication primary |

`globalStatus` values (from MySQL Shell):

| Value | Meaning |
| --- | --- |
| `OK` | Cluster is healthy and replicating as expected. |
| `OK_NOT_REPLICATING` | Cluster is reachable but not currently replicating (transitional or misconfigured). |
| `NOT_OK` | Cluster has a problem; check MySQL Shell status and events. |
| `INVALIDATED` | Cluster was fenced off after forced failover; it may have divergent GTIDs. Rejoin it with `rejoinCluster()` if GTIDs are compatible. Otherwise remove and recreate the cluster to rejoin the ClusterSet. |
| `UNKNOWN` | Status could not be determined (for example, the primary is unreachable). |

### Conditions

`status.conditions[].type` values:

| Value | Meaning |
| --- | --- |
| `Ready` | ClusterSet is formed and replicas are replicating from the specified primary. |
| `ClusterSetBootstrapped` | The primary cluster is configured as a ClusterSet. |
| `MySQLShellRunnerReady` | The `mysqlshell-runner` Pod is running and ready. |
| `SwitchoverInProgress` | `spec.primaryCluster` differs from the observed primary and a switchover Job is running, pending, or failed. |
| `ErrorReconcile` | An error occurred during reconciliation. |
| `ReplicaManagementFailure` | A replica add or remove Job failed; see the Job logs. |
| `ClusterSetDissolving` | The Custom Resource is being deleted and the dissolve finalizer is running. |

Common `Ready` condition reasons:

| Reason | Meaning |
| --- | --- |
| `ClusterSetHealthy` | MySQL Shell reports overall ClusterSet status as healthy. |
| `ClusterSetNotHealthy` | One or more members are not healthy; see `status.clusters` and the condition message. |
| `PrimaryUnreachable` | Primary cluster is not reachable. `Ready` is `Unknown`. |
| `AccessDenied` | Incorrect password configured on the replica site. `Ready` is `Unknown`. |

Common `MySQLShellRunnerReady` reasons:

| Reason | Meaning |
| --- | --- |
| `DeploymentReady` | The `mysqlshell-runner` Deployment is current and ready. |
| `DeploymentNotReady` | The Deployment is still rolling out. |
| `DeploymentFailed` | The Deployment failed. |
| `DeploymentNotObserved` | The Operator has not observed Deployment status yet. |

Common `SwitchoverInProgress` reasons:

| Reason | Meaning |
| --- | --- |
| `SwitchoverInProgress` | A switchover Job is running. Condition status is `True`. |
| `SwitchoverFailed` | The switchover Job failed. Condition status is `False`. |

`ErrorReconcile` uses the reason `ErrorReconcile` for general failures, or `AccessDenied` / `PrimaryUnreachable` when the ClusterSet manager cannot reach or authenticate to the primary.

### Events

The ClusterSet controller emits Kubernetes events you can view with `kubectl describe ps-clusterset`:

| Event reason | Meaning |
| --- | --- |
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
* `status.destination` — backup path or URL (`s3://`, `gs://`, or Azure container path)
* `status.completed` — completion timestamp
* `status.stateDescription` — error details when the backup fails
* `status.backupSource` — source Pod used for the backup
* `status.storage` — copy of the storage configuration used for this backup
* `status.image` — Percona XtraBackup image used for the Job
* `status.compressed` — whether the backup was compressed
* `status.conditions` — additional conditions

### Backup state values

`status.state` values are:

| Value | Meaning |
| --- | --- |
| `""` | Backup is created but not processed yet. |
| `Starting` | Backup is starting. |
| `Running` | Backup is in progress. |
| `Succeeded` | Backup completed successfully. |
| `Error` | Backup failed to start (for example, the cluster is not ready, backups are disabled, or the storage name is missing). Check `status.stateDescription`. This state is terminal; fix the cause and create a new backup. |
| `Failed` | Backup started but failed during execution. Check `status.stateDescription` and the backup Job logs. |

For troubleshooting steps, see [Troubleshoot backups and restores](debug-backup-restore.md).

### Backup conditions

`PerconaServerMySQLBackup` may include the following condition:

| Value | Meaning |
| --- | --- |
| `BackupLeaseAcquired` | The backup Job holds the cluster backup lease and is authorized to run. When `False` with reason `LeaseAlreadyHeld`, another backup still holds the lease. |

## PerconaServerMySQLRestore status

Restore progress and results are in `status.state`. Use these fields to confirm when a restore starts, finishes, or fails.

Common fields:

* `status.state` — restore job state
* `status.stateDescription` — error details when the restore cannot proceed or fails
* `status.completed` — completion timestamp

### Restore state values

`status.state` values are:

| Value | Meaning |
| --- | --- |
| `""` | Restore is created but not processed yet. |
| `Starting` | Restore is starting. |
| `Running` | Restore is in progress, including waiting for the cluster to become ready after the restore Job completes. |
| `Succeeded` | Restore completed successfully. |
| `Error` | Restore cannot start yet. Typical causes: the cluster is not found, `backupName` and `backupSource` are empty, `backupSource` is incomplete, the storage name is missing from the cluster Custom Resource, or point-in-time recovery is requested but the binlog server is not enabled. Check `status.stateDescription`. The Operator retries on the next reconcile. |
| `Failed` | The restore Job, prepare Job, or point-in-time recovery Job failed. Check the Job logs. |

If another restore holds the cluster lease, or a backup is still running, `status.state` stays empty (`""`) and `status.stateDescription` explains the wait. That is not the `Error` state.

### `Error` vs `Failed`

* **`Error`** — Recoverable. The Operator sets this state when validation fails or a prerequisite is missing. It resets the state on the next reconcile, so you can fix the Restore object configuration and unblock the restore process without creating a new Restore object.
* **`Failed`** — Terminal. The restore, prepare, or point-in-time recovery Job failed. Inspect the Job logs, fix the cause, and create a new Restore Custom Resource.

When a restore is in `Error`, inspect the message:

```bash
kubectl get ps-restore <restore-name> -n <namespace> \
  -o jsonpath='{.status.state}{"\n"}{.status.stateDescription}{"\n"}'
```

