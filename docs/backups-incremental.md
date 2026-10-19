# Incremental backups

!!! admonition "Version added: [1.1.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.1.0.md)"

!!! admonition ""

    This feature is in the tech preview stage. The behavior can change in future releases.

**Incremental** backups copy only what changed since the previous backup in the chain. They are smaller, faster to transfer, and cheaper to keep than taking a full backup every time.

## Backup chain

Every incremental backup belongs to a **chain** that starts with one **full** backup on the **same** storage. The Operator checks that a valid full backup exists before it starts an incremental one.

```mermaid
flowchart LR
    F["Full backup"] --> I1["Increment 1"]
    I1 --> I2["Increment 2"]
    I2 --> D["..."]
    D --> IN["Increment N"]
```

By default, the Operator uses the **latest full backup** as the base. For on-demand backups, you can set a different base with `spec.incrementalBaseBackupName`.

You can use any [supported storage type](backups-storage.md).

## How an incremental backup runs

1. You [make an on-demand backup](backups-ondemand.md) with type **incremental**, or you [configure a schedule](backups-scheduled.md) that creates incremental backups.
2. The Operator confirms that a valid **full** backup exists on the same storage. Unless you specify another backup, it uses the most recent full backup.
3. The Operator marks that full backup as the chain base and streams the increment to the same storage.
4. Later increments use the previous increment’s `to_lsn` as `from_lsn` so the chain stays continuous.

!!! important

    The Operator sets the `percona.com/base-backup-name` annotation on the base backup to link the chain. Do not edit or remove it. Changing it can break the chain and lead to data corruption.

## Restore from an incremental backup

The restore flow is the same for full and incremental backups. Follow [Restore the cluster from a previously saved backup](backups-restore.md) or [Restore from a backup to a new Kubernetes-based environment](backups-restore-to-new-cluster.md).

The Operator identifies the backup type by name or destination. Incremental destinations use an `.incr` path segment so the Operator can reconstruct the chain. It downloads the full backup and all related increments, restores the full backup first, then applies each increment.

If you make a [point-in-time recovery](backups-pitr.md), the Operator applies binlogs after the chain. See [the point-in-time recovery workflow](backups-pitr.md#point-in-time-recovery-workflow).

Incremental objects in storage use an `.incr` path segment so the Operator can tell them apart from full backups:

```
s3://bucket/prefix/
my-cluster-2026-04-06-full/           # base full backup
my-cluster-2026-04-06-full.incr/      # incremental chain directory
    my-cluster-2026-04-07T000000-incr/
    my-cluster-2026-04-08T000000-incr/
    my-cluster-2026-04-09T000000-incr/
```

## Speed up incremental backups with page tracking

!!! admonition "Version added: [1.3.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.3.0.md)"

Page tracking lets Percona XtraBackup copy only the InnoDB pages that changed since the last backup, instead of scanning every data file. The Operator installs the `mysqlbackup` component that this feature needs. For details, see [Take an incremental backup using page tracking :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/latest/page-tracking.html).

Enable page tracking by passing the `--page-tracking` flag in the `xtrabackup` container options. Set it on the **storage** so the whole chain uses it:

```yaml title="deploy/cr.yaml"
spec:
  backup:
    storages:
      s3-us-west:
        containerOptions:
          args:
            xtrabackup:
              - "--page-tracking"
```

Override it for a single on-demand backup:

```yaml title="deploy/backup/backup.yaml"
spec:
  clusterName: ps-cluster1
  storageName: s3-us-west
  type: incremental
  containerOptions:
    args:
      xtrabackup:
        - "--page-tracking"
```

Pass the `--page-tracking` flag on the **base** backup to start tracking for the whole chain. The next incremental backup then copies only changed pages. Keep the flag on later increments so tracking continues.

If you set the `--page-tracking` flag only on an incremental job, that job still scans all pages because the previous full backup did not start tracking.

For how cluster-level and per-job options interact, see [Fine-tuning backup and restore operations](backups-fine-tune.md).

## Implementation specifics and rules

### Backup chain rules

1. A full backup is required to start the chain. If none exists, the incremental backup fails.
2. The base full backup and its increments must be on the **same** storage.
3. By default, the Operator uses the most recent full backup. You can set a different base with `spec.incrementalBaseBackupName`. If that backup is valid, the Operator starts the chain from it.
4. If the base backup already has increments, the Operator continues from the most recent increment.
5. Retention applies to the chain as a unit: deleting the **base** full backup removes the entire chain. You cannot set retention on increments alone.
6. You cannot delete an increment in the middle of a chain. You can delete only the **last** increment, or the base backup, which removes the whole chain.
7. The Operator does not run two incremental backups on the **same** chain at once. Increments run one by one.

### Restore rules

1. [Restore in place](backups-restore.md) with `backupName`, or [restore across clusters](backups-restore-to-new-cluster.md) with `backupSource.destination`.
2. `backupSource` restores work across clusters and namespaces when the storage path is reachable. The `.incr` layout keeps incremental paths discoverable.
3. Restore always needs the full chain: full backup first, then increments in order, up to the backup you selected.

## Known limitations

- If a backup in your chain fails but some data was already uploaded, restore still includes that failed backup and fails. Start a new chain.
- If the checkpoint file is missing from a backup directory, the next incremental backup can hang. Start a new chain.
