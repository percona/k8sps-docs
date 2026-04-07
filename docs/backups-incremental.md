# Incremental backups

!!! admonition "Version added: [1.1.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.1.0.md)"

If your database grows quickly or sees heavy write traffic, you may want frequent backups. Taking a full backup every time costs more storage, takes longer to upload, and adds load to the cluster.

**Incremental** backups copy only what changed since the previous backup in the chain. They are usually smaller, faster to transfer, and cheaper to keep in the backup storage.

## What you need first

Every incremental backup belongs to a **chain** that starts with one **full** backup on the **same** storage. The Operator checks that a valid full backup exists before it starts an incremental one. Using the same storage for the whole chain enables the Operator to reuse the same credentials and paths, and simplifies restore.

You can use any [supported storage type](backups-storage.md).

## What the backup chain looks like

Incremental backups build on the full backup and on each other in order:

```mermaid
flowchart LR
    F["Full backup"] --> I1["Increment 1"]
    I1 --> I2["Increment 2"]
    I2 --> D["..."]
    D --> IN["Increment N"]
```

By default, the Operator uses the **latest full backup** as the base for both **scheduled** and **on-demand** incremental backups. If you want more control, you can explicitly specify the base backup in the configuration for on-demand backups. The Operator validates the specified backup and derives the incremental chain from it.

## How an incremental backup runs

1. You create a `PerconaServerMySQLBackup` object with type **incremental**. Or, you configure the **backup schedule** in the cluster Custom Resource that creates incremental backups.
2. The Operator confirms that a **full** backup exists on the same storage and is valid. Unless you specify another backup, it uses the **most recent** full backup.
3. If the backup is valid, the Operator sets the `percona.com/base-backup-name` annotation on it so that it serves as the base for the incremental backup chain.
4. If there are already incremental backups derived from the base, the Operator takes the `to_lsn` value from the previous increment and sets it as the `from_lsn` value for the new increment so the chain stays continuous.
5. The Operator streams the new incremental to the same storage.
6. The Operator records the backup type on the backup object.

!!! important

   The `percona.com/base-backup-name` annotation is internal and serves to correctly link incremental backups to the base one. Removing or editing it will lead to unpredictable results and data corruption. Don't remove or edit this annotation.

## How restore from an incremental backup works

The restore flow is unified for both full and incremental backups. The Operator identifies the backup type by name or destination. To identify the increments and reconstruct the chain, the backup destination has now the `.incr` path segment. The Operator downloads the full backup and all related increments and sorts them in the correct order. Then it restores the full backup first and applies each incremental backup. This provides a better restore performance.

Here's how it works in detail:

1. You create a `PerconaServerMySQLRestore` object and reference the incremental backup with `backupName` (same cluster) or `backupSource` (remote path / another environment).
2. The Operator detects that the target is incremental and resolves the chain.
3. It connects to the storage and lists full backup plus all increments up to and including the one you chose, using paths that include the `.incr` segment so increments are unambiguous.
4. The Operator sorts increments in the right order.
5. The Operator pauses the cluster for the restore.
6. The restore Job downloads and applies the full backup, then each incremental one in order.
7. The cluster is unpaused when the restore completes.

!!! admonition "Path layout"

    Incremental destinations use an `.incr` segment in the path so the Operator can tell full and incremental artifacts apart. A typical pattern resembles `prefix/<cluster>-<timestamp>-full.incr/<cluster>-<timestamp>-incr`; exact layout follows your `prefix` and storage settings.

## Why you need incremental backups

With incremental backups, you gain the following benefits:

* strengthen your backup strategy by creating multiple restore points
* improve backup and restore performance thanks to smaller backup sizes
* increase storage efficiency by avoiding duplication of unchanged data
* lower system load, since smaller backups require fewer compute resources and reduce impact on your cluster
* reduce both storage and data‑transfer costs

## Implementation specifics and rules

### Backup chain rules

1. A full backup is required to start the incremental chain. If none exists, the Operator does not start the incremental backup.
2. A base full backup and incremental backups derived from it must be **on the same storage**. 
3. By default, the Operator uses the most recent full backup to start the incremental chain. You can explicitly specify the base backup in the `spec.incrementalBaseBackupName` option in the backup configuration file. If the specified backup is valid, the Operator starts the incremental backup chain from it.
4. If the base backup already has the incremental backup chain, the Operator uses the most recent increment to continue the chain.
???5. Backups are **streamed** to storage; the Operator does not keep a separate local copy of the full chain on disk.
6. Retention applies to the chain as a unit: deleting the **base** full backup removes the **entire** incremental chain that depends on it, so you do not leave orphaned increments. Specifying the retention policy for increments is not supported.
7. You cannot delete an increment in the middle of a chain as it would break its continuity. You can delete only the **last** increment in the chain or the base backup, which removes the whole chain.
8.  The Operator blocks two concurrent incremental backups against the **same** chain to avoid ambiguous ordering.

### Restore rules

1. You can make either an in-place restore pointing at an incremental backup object in the `backupName` option, or make a cross-cluster restore specifying the incremental backup path for the `dataSource.destination` option.
2. Restores that use `backupSource` work across clusters and namespaces when the storage destination is reachable; incremental paths remain discoverable because of the `.incr` layout.
3. Restore always needs the full chain: full backup first, then increments in order, up to the backup you selected.
4. You can only restore from incremental backups to the state captured by the backup itself. Support for point-in-time recovery will be introduced in future releases.

