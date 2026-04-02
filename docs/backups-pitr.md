# Point in time recovery

!!! admonition ""

    This feature is in the tech preview stage. The behavior can change in future releases.

A base backup captures your data at a single moment in time. Restoring from such a backup is enough in many cases. However, if you need to undo a bad migration, recover right before someone dropped the wrong table, or meet a tighter recovery point, a base backup alone won't give you that level of precision.

To address these use cases, you must be able to restore the database to a specific moment or to a specific transaction. To do that means to apply the binary logs generated after the backup on top of it, because they contain all subsequent changes. This process is called point-in-time recovery and is available in the Operator starting with v 1.1.0.

This feature is in the tech preview stage. We don't recommend using it in production yet, but we encourage you to try it out and share your feedback.

## How the Operator performs point‑in‑time recovery

The Operator implements point-in-time recovery in two stages:

* Restores a base physical backup taken with `PerconaXtraBackup`
* Replays binary log on top of the base backup to bring the database to the desired moment or transaction. A binary log records all changes made to the database, such as updates, inserts, and deletes.
  
To speed up recovery, the Operator converts binary logs into relay logs and applies them concurrently using MySQL's SQL replication thread. This approach reuses MySQL replication capabilities and significantly improves performance.

## Recovery modes

You can restore the database up to a specific moment in time or up to a specific transaction. You specify the desired mode in the `PerconaServerMySQLRestore` object:

| Mode | What you specify | How it works| Typical use case |
| ---- | ----------------- | ----------- |----------------|
| **GTID** | A GTID set | The Operator restores the database **just before** that transaction. The specified transaction is not included.| Precise, replication-friendly recovery when you know the GTID to stop before|
| **Date / time** | A timestamp | The Operator restores the database **just before** the last transaction that was written before specified timestamp | Use when wall-clock time is easier than GTIDs |

## Binary log collection

The Operator requires binary logs (binlogs) for point-in-time recovery. The Operator collects them using the [Percona Binarylog Server :octicons-link-external-16:](https://github.com/Percona-Lab/percona-binlog-server) command‑line utility. The Binarylog Server connects to MySQL as a replication client and streams binlogs either to a cloud storage or to the filesystem. It can resume collection automatically after being interrupted or stopped.

```mermaid
flowchart LR
        PS["Percona Server<br/>primary"]
        BS["Binlog server <br/> replication client <br/> GTID mode"]
        S3["S3-compatible<br/>storage"]
        PS -->|"binary logs"| BS
        BS -->|"archived binlogs"| S3
```

To enable binlog collection, configure the `spec.backup.pitr` section in your Custom Resource:

```
spec:
  backup:
    pitr:
      enabled: true
      binlogServer:
        storage:
          s3:
            bucket: my-binlogs
            credentialsSecret: my-s3-secret
            region: us-east-1
            endpointURL: https://s3.amazonaws.com
```

After you apply the changes, the Operator starts Percona Binary log Server Pod and enforces GTID mode on the cluster. The Pod continuously collects binlogs and stores them in the configured location.

## Point-in-time recovery workflow

Let's have a closer look at how point-in-time recovery works:

When you trigger a restore with a point-in-time recovery target, the Operator does the following:

1. Execs into the Binlog server Pod and searches for required binlogs
2. Pauses the cluster
3. Restores the base backup
4. Runs the point-in-time recovery Job that:
   
    * Starts a temporary `mysql` instance
    * Copies binlogs from the storage and converts them to relay logs
    * Configures MySQL to read and operate only with the downloaded relay logs using the `CHANGE REPLICATION SOURCE TO RELAY_LOG_FILE=..., SOURCE_HOST='dummy'` statement
    * Starts the SQL thread and applies relay logs until the GTID or position. The SQL thread uses the default number of `replica_parallel_workers` for concurrent processing
    * Stops the replication thread and resets the replica information
    * Shuts down the temporary `mysql` instance
  
5. Unpauses the cluster.

For how to configure and start a point-in-time recovery, refer to the [Make a restore with point-in-time recovery on the same cluster](backups-restore.md#restore-with-point-in-time-recovery) and [Make a restore with point-in-time recovery on the new cluster](backups-restore-to-new-cluster.md#restore-with-point-in-time-recovery) tutorials.

With point-in-time recovery, you get finer control over when you come back online, which improves recovery point objective (RPO)

## Implementation specifics

1. Point-in-time recovery is supported for both asynchronous and group replication types.
2. The Binarylog server is deployed with the number of Pods restricted to 1. This is because it connects to MySQL as a replication client with a specific server ID and only one instance can connect to the database with the same ID. Any number you set for the `size` in the Custom Resource will be ignored.
3. Enabling the Binarylog Server enforces GTID mode on the cluster, which is required for replaying relay logs.
4. The cluster is paused during point-in-time recovery. The Operator starts a temporary `mysql` which that operates on the data PVC.
5. For the restore up to a specific transaction, the Operator restores all transactions except the last one that was written before the specified timestamp. that last transaction is not included.
6. The Binarylog Server must be running before the restore begins. The reconciler locates the required binlogs before pausing the cluster.
7. When the cluster is **paused**, point-in-time-related behavior is effectively **disabled** so the Operator does not leave binlog infrastructure running in a way that contradicts the paused state.

## Known limitations

The Binarylog server supports only AWS S3 and S3-compatible storage services for streaming binlogs to. Use the same operational practices as for backup buckets: credentials via Secrets, correct endpoint URL (including scheme where required), region, and TLS options consistent with your environment.

1. If something fails mid-restore, use the same discipline as with any restore: inspect **`PerconaServerMySQLRestore` status**, the **restore and PITR Jobs**, and [Troubleshoot backups and restores](debug-backup-restore.md).
2. You can only perform point-in-time recovery from a backup specified using the `backupName` field. Point-in-time recovery is currently not supported when restoring from a backup specified via `dataSource`. This improvement is planned for future releases.
