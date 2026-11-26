> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Backup compression support in Percona Operator for MySQL

Percona Operator for MySQL uses Percona XtraBackup (PXB) to create backups. The Operator exposes this capability too, supporting compression using the `zstd` compression algorithm.

Compression works for both full and [incremental](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-incremental.md) backups. You can configure it for [scheduled](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-scheduled.md) and [on‑demand](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-ondemand.md) backups.

With this ability to compress backups, you can reduce the size of your backups, and lower storage and data‑transfer costs.

## Configure global compression

You can configure compression using the MySQL configuration file. This setting applies to both scheduled and on-demand backups for all backup storages that you use.

```yaml
spec:
  mysql:
    image: percona/percona-server:8.4.11-11.1
    configuration: |
      ...
      [xtrabackup]
      compress=zstd
      ...
```

You can override the compression [for scheduled backups per specific storage](#configure-compression-for-scheduled-backups) or for a particular [on-demand backup](#configure-compression-for-ondemand-backups).

## Configure compression for scheduled backups

In the cluster Custom Resource, add compression flags under the storage entry your schedules use:

```yaml
spec:
  backup:
    storages:
      <storage-name>:
        containerOptions:
          args:
            xtrabackup: 
              - "--compress"
```

## Configure compression for on‑demand backups

For on‑demand backups, define the compression settings directly in the configuration file for the `PerconaServerMySQLBackup` object:

```yaml
apiVersion: ps.percona.com/v1
kind: PerconaServerMySQLBackup
metadata:
  name: backup1-compressed
  finalizers:
    - percona.com/delete-backup
spec:
  clusterName: ps-cluster1
  storageName: s3-us-west
  containerOptions:
    args:
      xtrabackup:
        - "--compress"
```

It’s important to understand how the Operator prioritizes compression and other backup tool settings when they’re defined both globally in your cluster’s Custom Resource (CR) and individually for a specific backup or restore job. Percona Operator gives precedence to the settings in an individual `PerconaServerMySQLBackup` or `PerconaServerMySQLRestore` object, allowing you to override cluster-wide defaults on a per-job basis. For a detailed explanation of how these options apply, see [Fine-tuning backup and restore operations](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-fine-tune.md).

## Compare compressed and uncompressed size

After a compressed backup succeeds, compare `status.size` and `status.uncompressedSize` on the Backup object. The gap between them is how much compression saved in object storage.

- `status.size` is the compressed object in storage.
- `status.uncompressedSize` is the size before compression. For uncompressed backups the two values are the same.

Run this command to compare the sizes:

```bash
kubectl get ps-backup backup1-compressed -n <namespace> \
  -o jsonpath='{.status.size}{" / uncompressed "}{.status.uncompressedSize}{"\n"}'
```

See [Backup status](https://docs.percona.com/percona-operator-for-mysql/1.3.0/cr-statuses.md#perconaservermysqlbackup-status) for the full field list.

## Restore from a compressed backup

You can make a restore either using the [`backupName`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/restore-cr.md#backupname) or the [`backupSource`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/restore-cr.md#the-backupsource-subsection) options.

The Operator detects if this backup is compressed and automatically decompresses during the preparation stage for the restore.
