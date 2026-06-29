# ClusterSet Resource options

The `PerconaServerMySQLClusterSet` Custom Resource defines cross-site replication between Group Replication clusters as a MySQL InnoDB ClusterSet. Use the short name `ps-clusterset`.

This document describes all available options. For status fields and conditions, see [Custom resource statuses](cr-statuses.md). 

## `apiVersion`

Specifies the API version of the Custom Resource.

| Value type | Example |
| ---------- | ------- |
| :material-code-string: string | `ps.percona.com/v1` |

## `kind`

Defines the type of resource: `PerconaServerMySQLClusterSet`.

## `metadata`

The metadata section identifies the ClusterSet object. It includes the following keys:

* `name` — Name of the ClusterSet resource. 
* `namespace` — Namespace where the ClusterSet Custom Resource and the `mysqlshell-runner` Pod run.
* `finalizers` — ensure safe deletion of resources in Kubernetes under certain conditions. This subsection includes the following finalizers:
  
  * `percona.com/clusterset-dissolve` — Runs `.dissolve()` on the InnoDB ClusterSet before the Custom Resource is deleted. Underlying clusters continue as standalone InnoDB Clusters.

## `spec`

This section contains the ClusterSet configuration.

### `spec.primaryCluster`

Name of the InnoDB cluster that should serve writes. Must match exactly one `spec.clusters[].innodbClusterName`. Must contain only alphanumeric characters (max 63).

Editing this field triggers a **planned switchover** when the current primary is reachable. For a **forced failover** when the current primary is unreachable, you must also set the [`spec.unsafeFlags.forcedFailover`](#specunsafeflagsforcedfailover) to `true`.

| Value type | Example |
| ---------- | ------- |
| :material-code-string: string | `pscluster1` |

### The `spec.unsafeFlags` subsection

Groups opt-in flags for destructive ClusterSet operations. Both default to `false`.

#### `spec.unsafeFlags.forcedFailover`

When `true`, permits `forcePrimaryCluster()` if you change `spec.primaryCluster` while the current primary is unreachable.

| Value type | Example |
| ---------- | ------- |
| :material-toggle-switch-outline: boolean | `false` |

!!! warning

    Forced failover can promote a replica while the old primary may still accept writes, causing split-brain and lost transactions. Set this only when you are certain the old primary cannot recover.

#### `spec.unsafeFlags.forcedClusterRemoval`

When `true`, permits `removeCluster(..., {force: true})` for an unreachable replica removed from `spec.clusters[]`.

| Value type | Example |
| ---------- | ------- |
| :material-toggle-switch-outline: boolean | `false` |

!!! warning

    Forced removal abandons unreplicated transactions on the removed cluster. The cluster may require manual cleanup or a full rebuild.

### `spec.sslMode`

SSL mode for ClusterSet async replication channels between primary and replica clusters.

| Value | Meaning |
| ----- | ------- |
| `AUTO` | TLS is enabled if the instance supports it; otherwise disabled. **Default.** |
| `DISABLED` | TLS is disabled for replication channels. |
| `REQUIRED` | TLS is required for replication channels. |
| `VERIFY_CA` | Like `REQUIRED`, plus verify the peer certificate against configured CA certificates. Primary and replica certificates must be signed by the same CA. |
| `VERIFY_IDENTITY` | Like `VERIFY_CA`, plus verify the peer certificate matches the connection host (SAN must match `spec.clusters[].endpoints[].host`). |

| Value type | Example |
| ---------- | ------- |
| :material-code-string: string | `AUTO` |

### `spec.credentialsSecret.name`

The name of a Secret in the same namespace that holds the `clusterset` user password. 

| Value type | Example |
| ---------- | ------- |
| :material-code-string: string | `ps-cluster1-secrets` |

### `spec.credentialsSecret.key`

The field in the Secret that holds the `clusterset` user password value. This password must match on every participating cluster. Defaults to `clusterset`.

| Value type | Example |
| ---------- | ------- |
| :material-code-string: string | `clusterset` |

### The `spec.clusters` subsection

List of InnoDB clusters that participate in the ClusterSet. Minimum 1 entry (primary only at bootstrap); maximum 10. Each cluster name must be unique.

#### `spec.clusters[].innodbClusterName`

Logical name of the InnoDB cluster within the ClusterSet. Used in `spec.primaryCluster`, status, and MySQL Shell AdminAPI calls. The name must match the value from `status.innodbClusterName` of a corresponding `PerconaServerMySQL` Custom Resource. 

Alphanumeric only, max 63 characters. Immutable in practice — rename by remove and re-add.

| Value type | Example |
| ---------- | ------- |
| :material-code-string: string | `pscluster1` |

#### `spec.clusters[].endpoints`

List of `host:port` pairs the controller uses to reach MySQL members of this cluster. Minimum 1, maximum 9 per cluster. The controller uses the first reachable endpoint. Multiple entries improve resilience to single-member failures.

Each `host` must be unique across **all** clusters in the ClusterSet. It can be the IP address or a DNS name reachable from the `mysqlshell-runner` Pod.

The `port` is MySQL port. Defaults to `3306`.


| Value type | Example |
| ---------- | ------- |
| :material-text-long: subdoc | <pre>- host: ps-cluster1-mysql-primary.default.svc.cluster.local<br>  port: 3306</pre> |

### `spec.createReplicaClusterOptions.recoveryMethod`

Preferred method for seeding the first member of a new replica cluster when it joins the ClusterSet.

Supported values:

* `clone` — Physical snapshot via MySQL CLONE plugin. **Default.** Best for small datasets and low-latency networks.
* `incremental` — Apply GTID delta only. Use after restoring a backup from the primary into the replica. Best for large datasets or WAN links.

When you omit this field, the Operator uses `clone`.

| Value type | Example |
| ---------- | ------- |
| :material-code-string: string | `clone` |


### `spec.mysqlshellRunner.image`

Container image for the `mysqlshell-runner` Pod and ClusterSet Jobs. Must contain `mysqlsh` on `PATH`. The mysqlsh major version must match the MySQL endpoints (8.0 endpoints → 8.0 image, 8.4 endpoints → 8.4 image).

| Value type | Example |
| ---------- | ------- |
| :material-code-string: string | `percona/percona-server:{{ ps84recommended }}` |
