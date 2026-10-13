# Automatic configuration tuning

!!! note "Version added: [1.3.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.3.0.md)"

The Operator can calculate a full MySQL configuration in addition to `innodb_buffer_pool_size` and `max_connections`. The calculation is based on the CPU and memory you allocate to the MySQL container, the workload you run, and the MySQL version. You set those resources and the Operator sizes the database settings to match them. When the resources change, the Operator recalculates the settings accordingly.

This automatic configuration tuning gives you:

* Production-ready cluster tuned to its actual resources and workload out of the box
* Effective resource utilization – you pay only for what you use
* Updated settings when you change `mysql.resources` or the workload profile

The Operator uses the [mysqloperatorcalculator :octicons-link-external-16:](https://github.com/Tusamarco/mysqloperatorcalculator) library to calculate these settings. It sets `[mysqld]` variables only. Container resources, probe timings, and storage size stay under your control.

## Availability

* **New clusters**: enabled when you deploy with Operator 1.3.0+ and the `crVersion` is `1.3.0` or higher. 
* **Existing clusters**: upgrading the Operator does not turn automatic configuration tuning on for you. [Turn it on](#turn-on-automatic-configuration-tuning) yourself once you've upgraded.

### Supported Percona Server for MySQL versions

The Operator can calculate MySQL settings for these Percona Server for MySQL versions:

* 9.7.x
* 8.4.x (all patch releases)
* 8.0.46 and later

On 8.0.45 or older, the Operator falls back to [basic buffer-pool and `max_connections` tuning](options.md#auto-tuning-mysql-options). See [AutoConfigFallback warning](#autoconfigfallback-warning) if you weren't expecting it.

## Turn on automatic configuration tuning

!!! important

    If `spec.mysql.configuration` is set, or you have MySQL settings in your own ConfigMap or Secret, the Operator does not calculate the configuration even when automatic configuration tuning is turned on. See [Automatic vs user-provided MySQL configuration](#automatic-vs-user-provided-mysql-configuration) for details. Clear those settings first if you want the Operator to calculate the MySQL configuration for you.

Configure the `spec.mysql.autoConfig.` section in the Custom Resource.

* Set `enabled` to `true`.
* Specify the workload profile in the `loadType`. See [Choose a workload profile](#choose-a-workload-profile) to understand which one you need.
* When `enabled` is `true`, the following fields are required. The Custom Resource is rejected otherwise:

  * `mysql.resources` with both CPU and memory, set in `requests` or `limits`. CPU must be greater than 0 and memory must be at least 12Mi.
  * `mysql.autoConfig.version`, in the `<major>.<minor>.<patch>` format.

```yaml
spec:
  mysql:
    autoConfig:
      enabled: true
      loadType: someWrites  
      version: "8.4.8"       # the MySQL version to tune for
    resources:
      requests:
        cpu: "2"
        memory: 4Gi
      limits:
        cpu: "4"
        memory: 8Gi
```

See the [Custom Resource reference](operator.md#operator-mysql-section) for the full field list.

### Choose a workload profile

`loadType` tells the Operator how to balance read-oriented and write-oriented settings:

| `loadType` | Approximate read/write mix | Choose this when |
| --- | --- | --- |
| `mostlyReads` | ~95% reads | Reporting, blogs, or read-replica workloads rarely write |
| `someWrites` (default) | ~80% reads | A typical read-dominated application, such as e-commerce or light OLTP |
| `equalReadsWrites` | ~50/50 | Mixed analytics or heavy OLTP |
| `heavyWrites` | Write-dominated | Log ingestion, event streams, or high-frequency inserts |

## Understand how calculation works

When automatic configuration tuning is turned on, the Operator uses these inputs to calculate the configuration on every reconcile:

| Input | Source |
| --- | --- |
| CPU and memory | `mysql.resources`. When both `limits` and `requests` are set, the Operator uses `limits`. |
| Workload profile | `mysql.autoConfig.loadType`. See [Choose a workload profile](#choose-a-workload-profile) for available profiles and the default. |
| MySQL version | `mysql.autoConfig.version`. This selects the parameter set — see [Keep the MySQL version in sync](#keep-the-mysql-version-in-sync). |
| Replication type | `mysql.clusterType`. Group Replication and asynchronous replication receive different settings. |

The Operator writes the result to the `auto-<cluster-name>-mysql` ConfigMap. It updates that ConfigMap only when the result changes, so a cluster with unchanged inputs does not restart.

### Keep the MySQL version in sync

`mysql.autoConfig.version` tells the Operator which MySQL version to tune for. It does not change which image is deployed, and the Operator does not check that the two match. Update `mysql.autoConfig.version` whenever you change `mysql.image`. A mismatch can make the Operator emit a parameter the running server does not recognize, and that can prevent MySQL from starting.

### Automatic vs user-provided MySQL configuration

The Operator calculates the full configuration only when the `spec.mysql.configuration` in the Custom Resource is empty and you have not put MySQL settings in a ConfigMap or Secret of your own.

Any value in `spec.mysql.configuration` or any MySQL settings in a ConfigMap or Secret you create disable automatic configuration tuning. The Operator applies only your settings plus the  `innodb_buffer_pool_size`, `innodb_buffer_pool_chunk_size`, and `max_connections` values that it calculates from the container memory. It logs `a user configuration is set, skipping autoconfig` message and does not record a Kubernetes event for this skip.

The `auto-<cluster-name>-mysql` ConfigMap is the Operator's output. It does not count as configuration you supplied.

The Operator calculates the full configuration once you've [turned it on](#turn-on-automatic-configuration-tuning) and cleared `spec.mysql.configuration` and removed MySQL settings from your own ConfigMap or Secret.

### Full list of tunable variables

The Operator includes a variable only when `mysql.autoConfig.version` falls inside that variable's supported range. Read the ConfigMap to see the variables and values for your cluster:

```bash
kubectl get configmap auto-<cluster-name>-mysql -o jsonpath='{.data.my\.cnf}' -n <namespace>
```

??? note "InnoDB, connections, binlog, replication, and Group Replication variables"

    **InnoDB, on every cluster:**

    * `innodb_buffer_pool_size`, `innodb_buffer_pool_instances`, and `innodb_buffer_pool_chunk_size`
    * `innodb_redo_log_capacity`, or `innodb_log_file_size` and `innodb_log_files_in_group` on MySQL 8.0
    * `innodb_flush_method` and `innodb_flush_log_at_trx_commit`
    * `innodb_io_capacity_max`, `innodb_purge_threads`, and `innodb_parallel_read_threads`
    * `innodb_adaptive_hash_index`, `innodb_numa_interleave`, and `innodb_monitor_enable`

    **Connections and session buffers, on every cluster:**

    * `max_connections` and `thread_cache_size`
    * `join_buffer_size`, `sort_buffer_size`, and `read_rnd_buffer_size`
    * `tmp_table_size`, `max_heap_table_size`, and `sync_binlog`

    **Replication applier, on every cluster:**

    * `replica_parallel_workers` and `replica_parallel_type`
    * `replica_preserve_commit_order`, `replica_exec_mode`, and `replica_compressed_protocol`

    **Binary logging and asynchronous replication, on asynchronous replication clusters:**

    * `binlog_cache_size`, `binlog_stmt_cache_size`, `binlog_format`, `binlog_row_image`, and `binlog_expire_logs_seconds`
    * `gtid_mode` and `enforce_gtid_consistency`
    * `relay_log_space_limit`, `sync_relay_log`, `replica_net_timeout`, and `replica_checkpoint_period`

    **Group Replication, on Group Replication clusters:**

    * `group_replication_message_cache_size` and `group_replication_communication_max_message_size`
    * `group_replication_flow_control_period` and `group_replication_member_expel_timeout`
    * `group_replication_autorejoin_tries` and `group_replication_paxos_single_leader`
    * `binlog_transaction_dependency_tracking`

### How calculated settings are applied

The Operator applies calculated values after all MySQL Pods are ready:

* Variables that MySQL accepts at runtime are applied with `SET GLOBAL` on each Pod, with no restart.
* The buffer pool, redo log settings and variables that MySQL accepts only at startup cause a rolling restart of the MySQL StatefulSet. Removing a variable from the configuration also causes a rolling restart.

Changing `mysql.resources` changes the buffer pool and the redo log. This change usually restarts the MySQL Pods. Plan a resize of `mysql.resources` as a change-management event. See [Scale compute resources](scaling.md#scale-compute-resources).

Before the Operator writes the configuration, it checks the calculated redo log against the data volume. When the redo log would exceed 25% of that volume, reconciliation stops. See [AutoConfigInsufficientStorage warning](#autoconfiginsufficientstorage-warning).

## Troubleshoot automatic configuration tuning

Check the cluster events first. See [Check the Events](debug-events.md).

```bash
kubectl get events --field-selector involvedObject.name=<cluster-name>
```

### AutoConfigInsufficientStorage warning

**Symptom.** Reconciliation is stuck. `kubectl get events` shows a warning with reason `AutoConfigInsufficientStorage`. The message names the calculated redo log size, the data volume size, and the minimum volume size needed.

**Cause.** The redo log size follows the buffer pool, and the buffer pool follows the memory in `mysql.resources`. MySQL preallocates the full redo log on disk. The Operator refuses a configuration whose redo log would exceed 25% of the data volume, so a volume that is too small does not reach a server that fails to start or clone.

The Operator uses the capacity of the smallest existing MySQL data volume in the cluster. When no PersistentVolumeClaims exist yet, it uses the storage size in `mysql.volumeSpec`. When the size cannot be determined, for example with a `hostPath` volume or an `emptyDir` volume without `sizeLimit`, the Operator skips this check.

**Fix.** Do one of the following, then let the Operator reconcile again:

* [Increase the storage size](scaling.md#scale-storage) of the MySQL data volume.
* Lower the memory in `mysql.resources` so the Operator sizes a smaller buffer pool and redo log.

### AutoConfigFallback warning

**Symptom.** The cluster starts, and events include a warning with reason `AutoConfigFallback`.

**Cause.** The Operator could not calculate the full configuration. It uses the basic buffer pool and `max_connections` tuning instead. Typical causes are a missing CPU value, an unsupported MySQL version, or an internal calculation error.

A configuration you set yourself also skips automatic configuration tuning, and that skip is written to the Operator log only. See [Automatic vs user-provided MySQL configuration](#automatic-vs-user-provided-mysql-configuration).

### AutoConfigFailed warning

**Symptom.** Events include a warning with reason `AutoConfigFailed`.

**Cause.** The basic buffer pool and `max_connections` tuning also failed. MySQL starts with no calculated parameters.
