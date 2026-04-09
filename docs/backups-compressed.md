# Backup compression support in Percona Operator for MySQL

Percona Operator for MySQL uses Percona XtraBackup (PXB) to create backups.  PXB supports backup compression with [multiple algorithms](#choosing-a-compression-algorithm), and the Operator exposes this capability too. 

Compression works for both full and [incremental](backups-incremental.md) backups, and you can configure it for [scheduled](backups-scheduled.md) and [on‑demand](backups-ondemand.md) backups.

With this ability to compress backups, you can reduce the size of your backups, and lower storage and data‑transfer costs.

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
              - "--compress=lz4"
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
        - "--compress=lz4"
```

It's important to understand how the Operator prioritizes compression and other backup tool settings when they're defined both globally in your cluster's Custom Resource (CR) and individually for a specific backup or restore job. Percona Operator gives precedence to the settings in an individual `PerconaServerMySQLBackup` or `PerconaServerMySQLRestore` object, allowing you to override cluster-wide defaults on a per-job basis. For a detailed explanation of how these options apply, see [Fine-tuning backup and restore operations](backups-fine-tune.md).

## Choosing a compression algorithm

Percona XtraBackup supports multiple compression algorithms with different trade‑offs. Your choice depends on CPU capacity, how often you run backups, and how much you want to shrink data on disk or over the network.

| Algorithm | Best for | Pros | Cons | Why choose it |
|-----------|----------|------|------|---------------|
| **ZSTD** | Most production environments | Excellent compression ratio, modern algorithm, good balance of speed and size | Slightly higher CPU usage compared to LZ4 | When you want strong compression without significantly impacting backup time |
| **LZ4** | High‑throughput environments, frequent backups, or CPU‑constrained nodes | Very fast compression and decompression, low CPU overhead | Larger backup size compared to ZSTD | When speed matters more than maximum compression |
