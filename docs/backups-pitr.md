# Point in time recovery

!!! admonition ""

    This feature is in the tech preview stage. The behavior can change in future releases.

A base backup captures your data at a single moment in time. Restoring from such a backup is enough in many cases. However, if you need to undo a bad migration, recover right before someone dropped the wrong table, or meet a tighter recovery point, a base backup alone won't give you that level of precision.

To address these use cases, you must be able to restore the database to a specific point in time or to a specific transaction. To do that means to apply the binary logs generated after the backup up to that particular point/transaction target, as they contain all subsequent database changes leading to it. This process is called point-in-time recovery and is available in the Operator starting with v1.1.0.

This feature is in the tech preview stage. We don't recommend using it in production yet, but we encourage you to try it out and share your feedback.

## How the Operator performs point‑in‑time recovery

The Operator implements point-in-time recovery in two stages:

1. Restores a base physical backup taken with `PerconaXtraBackup`
2. Replays binary logs on top of the base backup to bring the database to the desired point in time or transaction. A binary log records all changes made to the database, such as updates, inserts, and deletes.
  
The Operator decodes binary logs using the `mysqlbinlog` client and applies them sequentially.

## Recovery modes

You can restore the database up to a specific moment in time or up to a specific transaction. You specify the desired mode in the `PerconaServerMySQLRestore` object:

| Mode | What you specify | How it works| Typical use case |
| ---- | ----------------- | ----------- |----------------|
| **GTID** | A GTID set | The Operator restores the database up to that transaction. | Precise, replication-friendly recovery when you know the GTID to stop before|
| **Date / time** | A timestamp | The Operator restores the database up to the specified timestamp | Use when wall-clock time is easier than GTIDs |

## Binary log collection

The Operator requires binary logs (binlogs) for point-in-time recovery. The Operator collects them using the Percona Binlog Server command‑line utility. The Binlog Server connects to MySQL as a replication client and uploads binlogs to a dedicated object storage location. It can resume collection automatically after being interrupted or stopped.

```mermaid
flowchart LR
        PS["Percona Server<br/>primary"]
        BS["Binlog Server <br/> replication client <br/> GTID mode"]
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
            prefix: binlogs
            endpointURL: https://s3.amazonaws.com
```

After you apply the changes, the Operator starts the Percona Binary log Server Pod, which continuously collects binlogs and stores them in the configured location.

## Point-in-time recovery workflow

Let's have a closer look at how point-in-time recovery works:

When you trigger a restore with a point-in-time recovery target, the Operator does the following:

1. Execs into the Binlog Server Pod and searches for the required binlogs
2. Pauses the cluster
3. Identifies the closest base backup leading to that point and restores it
4. Runs the point-in-time recovery Job that:
   
    * Starts a temporary `mysqld` instance
    * Retrieves binlogs from the storage and applies them to the `mysql` client
    * Shuts down the temporary `mysqld` instance
  
5. Rebootstraps the cluster based on the restored dataset.

For how to configure and start a point-in-time recovery, refer to the [Make a restore with point-in-time recovery on the same cluster](backups-restore.md#restore-with-point-in-time-recovery) and [Make a restore with point-in-time recovery on the new cluster](backups-restore-to-new-cluster.md#restore-with-point-in-time-recovery) tutorials.

With point-in-time recovery, you get finer control over when you come back online, which improves recovery point objective (RPO)

## Implementation specifics

1. Point-in-time recovery is supported for both asynchronous and group replication topologies.
2. The Binlog Server is deployed with the number of Pods restricted to 1. This is because it connects to MySQL as a replication client with a specific server ID and only one instance can connect to the database with the same ID. Any number you set for the `size` in the Custom Resource will be ignored.
3. Enabling the Binlog Server requires the GTID mode to be enabled on the cluster for replaying binary logs. This mode is enabled by default.
4. The cluster is paused during point-in-time recovery. The Operator starts a temporary `mysqld` pod to perform the restore operation using the data PVC.
5. The Binlog Server must be running before the restore begins. The reconciler locates the required binlogs before pausing the cluster.
6. The Binlog Server stores binlogs in a dedicated folder. Therefore, you must specify the folder name (`prefix`) when configuring the storage for the Binlog Server.


## Known limitations

- The Binlog Server currently supports only AWS S3 and S3-compatible storage services for streaming binlogs. Use the same practices as backups: provide credentials via Kubernetes Secrets, set the endpoint URL (including scheme if required), region, and TLS options to match your environment.

* If the Operator user password is different from the password saved in the base backup, point-in-time recovery will fail. You must take a new full backup after changing the Operator user password to ensure point-in-time recovery works.

* During point-in-time recovery, updates made by `mysql-shell` can result in replication errors such as:
  
   ```
   2026-04-15T10:58:08.911878Z 11 [ERROR] [MY-010584] [Repl] Replica SQL: Could not execute Update_rows event on table mysql_innodb_cluster_metadata.instances; Can't find record in 'instances', Error_code: 1032; handler error HA_ERR_KEY_NOT_FOUND; the event's source log FIRST, end_log_pos 162397, Error_code: MY-001032
   ```
  
   If you want to ignore such errors, add `force: true` to the PITR section of your restore spec:
  
   ```yaml
   apiVersion: ps.percona.com/v1
   kind: PerconaServerMySQLRestore
   metadata:
     name: restore1
   spec:
     clusterName: cluster1
     backupName: backup1
     pitr:
       force: true
       type: date
       date: "2026-04-16 21:12:00"
   ```

  The `force: true` option enables the `--force` flag with the MySQL client and will silently ignore all SQL errors during binlog replay. **Warning:** This might result in data loss if underlying replication or data integrity errors are ignored.

* Point-in-time recovery job retries are not idempotent. If recovery fails after the base backup is restored, a retry will not restore the full backup again to reset the state. We recommend setting `spec.backup.backoffLimit=0` in your `cr.yaml` to prevent automatic job retries.

- If something fails mid-restore, use the same discipline as with any restore: inspect **`PerconaServerMySQLRestore` status**, the **restore and PITR jobs**, and refer to our [Restore troubleshooting guide](debug-backup-restore.md).
- Data at rest encryption is not supported with point-in-time recovery
- You cannot change the prefix for the Binlog Server.
* For point-in-time recovery you cannot use the backupSource.storage as the location for the binlogs. You must have the Binlog Server configured in the cluster's configuration.

* The Binlog Server may encounter issues if the number of objects in the point-in-time recovery bucket becomes too high. In such situations, the binlog server can get stuck and enter a CrashLoopBackOff state, unable to proceed with point-in-time recovery operations. This is due to how the Binlog Server processes or lists these objects internally. To recover from this state you need to delete old objects from the bucket manually. If the issue isn't caught within the binlog's expiration period, restoring the database becomes significantly more difficult. To reduce the risk of getting into this situation, monitor point-in-time recovery your bucket object count and clean up binlogs regularly.
