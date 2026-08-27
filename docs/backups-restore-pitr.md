# Perform a point-in-time recovery

Use this guide to restore your database up to a specific moment or a transaction target. 

You can restore in place on the [same cluster](#restore-on-the-same-cluster) or onto a [new cluster](#restore-on-a-new-cluster). In both cases the Operator restores a base backup and then replays binary logs up to a timestamp or a GTID.

To restore from a base backup without replaying binlogs, see [Restore on the same cluster](backups-restore.md) or [Restore on a new cluster](backups-restore-to-new-cluster.md).

!!! warning 

    During point-in-time recovery, the Operator pauses the cluster, restores the base backup, applies binlogs up to your target, then brings the cluster back online. Binlog Server must be running so the Operator can find the required binlogs before it pauses. For more information about the workflow, see [How it works](backups-pitr.md#how-it-works).

## Before you begin

* [Enable binlog collection](backups-pitr.md#enable-binlog-collection) on the source cluster
* Make a base backup **before** the target time or transaction
* Choose a target timestamp (`type: date`) or a GTID set (`type: gtid`)
* Set the `spec.backup.backoffLimit=0` in the cluster Custom Resource so a failed PITR Job does not retry automatically ([known limitations](backups-pitr.md#known-limitations))
* If the source cluster encrypted binlogs, follow [Restore with encrypted binlogs](#restore-with-encrypted-binlogs)



## Restore on the same cluster

The Operator reads binlog storage from `spec.backup.pitr.binlogServer` on the cluster Custom Resource.

1. Confirm the cluster is running and list backups:

    ```bash
    kubectl get ps <cluster-name> -n <namespace>
    kubectl get ps-backup -n <namespace>
    ```

2. Edit the [deploy/backup/restore.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/restore.yaml) manifest. Set `spec.clusterName`, `spec.backupName`, and the `spec.pitr` target.

    === "Restore to a timestamp"

        Use `type: date` when you know the wall-clock time to restore to.

        ```yaml
        apiVersion: ps.percona.com/v1
        kind: PerconaServerMySQLRestore
        metadata:
          name: restore-pitr-date
        spec:
          clusterName: ps-cluster1
          backupName: backup1
          pitr:
            type: date
            date: "2026-03-20 09:15:00"
        ```

    === "Restore to a transaction"

        Use `type: gtid` when you know the GTID to stop before. The value has the format `source_id:transaction_id`.

        ```yaml
        apiVersion: ps.percona.com/v1
        kind: PerconaServerMySQLRestore
        metadata:
          name: restore-pitr-gtid
        spec:
          clusterName: ps-cluster1
          backupName: backup1
          pitr:
            type: gtid
            gtid: "cc5e06e7-241e-11f1-a165-522d36bd0c5e:225"
        ```

3. Apply the configuration:

    ```bash
    kubectl apply -f deploy/backup/restore.yaml -n <namespace>
    ```

Then [watch the restore](#view-restore-details).

## Restore on a new cluster

The Operator starts a temporary Binlog Server from `spec.pitr.backupSource.binlogServer`, fetches binlogs from the **source** storage, then removes that Pod. Binlog storage is S3 or S3-compatible only, even when the base backup is on GCS or Azure.

### Checklist

* Target cluster is running
* User password Secret matches the source cluster. Copy it as described in [Preconditions](backups-restore-to-new-cluster.md#preconditions)
* If the base backup was [encrypted](backups-encrypted.md), create the same encryption-key Secret on the target and set `spec.backupSource.storage.encryptionKeySecret`
* If source binlogs were encrypted, copy the keyring Secret and set `spec.pitr.keyringSecret`. See [Restore with encrypted binlogs](#restore-with-encrypted-binlogs)

Keep these three prefixes distinct:

| Prefix | Where you set it | Value |
| ------ | ---------------- | ----- |
| Backup | `spec.backupSource.storage` | Same folder as when the backup was taken |
| Source binlogs | `spec.pitr.backupSource.binlogServer.storage.s3.prefix` | Copy from the source cluster's Binlog Server |
| Target collection | cluster `spec.backup.pitr.binlogServer` **after** restore | New folder for binlogs this cluster will collect. Must differ from the source prefix if they share a bucket |

### Retrieve the backup destination

The Operator must know where to take the backup from. Run this command on the **source cluster**:

```bash
kubectl get ps-backup -n <source-namespace>
```

Look for the `destination` value. You will use it for the restore configuration.

### Create the restore object

Edit [deploy/backup/restore.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/restore.yaml). Set these keys:

* `clusterName` - the name of the **target cluster** 
* `backupSource` section:
  
    * `destination` - where the backup is located. See [Retrieve the backup destination](#retrieve-the-backup-destination) how to get the backup destination 
    * `storage` - configure the storage where the backup is stored. Specify the bucket, region, credentials Secret for the Operator to access the storage. If you specified a separate folder for backups on the bucket, specify it for the `prefix` option.

* `pitr` section:
  
    * `type` - Set `date` to restore to a time or `gtid` to restore to a transaction
    * `date` - Specify the time in the format `YYY-MM-DD hh:mm:ss`. Use if if `type=date`
    * `gtid` - Specify the GTID set in the format `source_id:transaction_id`
    * `backupSource.binlogServer` - configure access to the binlog storage on the source cluster. Use the same settings as in the source cluster’s `spec.backup.pitr.binlogServer`, including the `prefix` for the binlog folder.

```yaml
apiVersion: ps.percona.com/v1
kind: PerconaServerMySQLRestore
metadata:
  name: restore-pitr
spec:
  clusterName: ps-cluster1
  backupSource:
    destination: s3://S3-BUCKET-NAME/BACKUP-NAME
    storage:
      type: s3
      s3:
        bucket: S3-BUCKET-NAME
        credentialsSecret: ps-cluster1-s3-credentials
        region: us-west-2
        prefix: <BACKUP-PREFIX>
      # encryptionKeySecret:           # if the base backup was encrypted
      #   name: my-encryption-key
      #   key: encryptionKey
  pitr:
    type: date                         # or gtid
    date: "2026-03-20 09:15:00"        # or gtid: "uuid:1-100"
    backupSource:
      binlogServer:
        storage:
          s3:
            bucket: S3-BINLOG-BUCKET-NAME
            credentialsSecret: ps-cluster1-s3-credentials
            region: us-west-2
            prefix: binlogs            # source binlog folder
```

| If you need to… | Change |
| --------------- | ------ |
| Stop at a GTID | `pitr.type: gtid` and `pitr.gtid` instead of `date` |
| Restore a GCS base backup | `backupSource.destination` (`gs://…`), `storage.type: gcs`, and the `gcs` keys. Binlogs stay under `pitr.backupSource.binlogServer.storage.s3` |
| Decrypt an encrypted backup | Uncomment `encryptionKeySecret` |
| Decrypt encrypted binlogs | See [Restore with encrypted binlogs](#restore-with-encrypted-binlogs) |


Start the restore:

```bash
kubectl apply -f deploy/backup/restore.yaml -n <namespace>
```

### After the restore

* [Enable binlog collection](backups-pitr.md#enable-binlog-collection) on the restored cluster with a **new** prefix if you share the source bucket.
* Take a fresh base backup to start a new timeline.

## Restore with encrypted binlogs

Use this section when the source cluster [encrypted binlogs](backups-pitr.md#binlog-encryption) in object storage. The restore Job decrypts each file with the key encryption key (KEK) recorded in that file's metadata. Unencrypted binlogs in the same bucket are applied as-is.

You **must have every KEK** that wrapped the binlogs you are replaying. If a key is missing from the keyring, those files cannot be decrypted.

### On the same cluster

If `spec.backup.pitr.binlogServer.keyringSecret` is still set on the cluster and the Secret still holds every KEK, run the restore as in [Restore on the same cluster](#restore-on-the-same-cluster). The Operator mounts that keyring automatically. No extra fields are required.

Set `spec.pitr.keyringSecret` on the restore object when the keys you need live in a **different** Secret than the one on the cluster (for example after you rotated keys into a new Secret):

```yaml
apiVersion: ps.percona.com/v1
kind: PerconaServerMySQLRestore
metadata:
  name: restore-pitr-encrypted
spec:
  clusterName: ps-cluster1
  backupName: backup1
  pitr:
    type: date
    date: "2026-03-20 09:15:00"
    keyringSecret:
      name: ps-cluster1-binlog-server-keyring
      key: keyring.json
```

The `key` field defaults to `keyring.json` if you omit it.

### New cluster

The target cluster has no access to Secrets from the source environment. Copy the keyring Secret, then point the restore at it.

1. On the **source** cluster, export the keyring Secret. Use the name from `spec.backup.pitr.binlogServer.keyringSecret` on the source Custom Resource:

    ```bash
    kubectl get secret ps-cluster1-binlog-server-keyring -n <source-namespace> -o yaml > binlog-keyring.yaml
    ```

2. Strip cluster-specific metadata:

    ```bash
    yq eval 'del(.metadata.ownerReferences, .metadata.annotations, .metadata.labels, .metadata.creationTimestamp, .metadata.resourceVersion, .metadata.selfLink, .metadata.uid, .metadata.namespace)' binlog-keyring.yaml > binlog-keyring-target.yaml
    ```

3. Apply the Secret on the **target** cluster:

    ```bash
    kubectl apply -f binlog-keyring-target.yaml -n <target-namespace>
    ```

    Confirm the Secret's `keyring.json` still lists **every** KEK that encrypted the binlogs still in the source bucket (including retired `id` values after rotation).

4. Create the restore as in [Restore on a new cluster](#restore-on-a-new-cluster) and add `spec.pitr.keyringSecret`:

    ```yaml
    spec:
      clusterName: ps-cluster1
      backupSource:
        destination: s3://S3-BUCKET-NAME/BACKUP-NAME
        storage:
          type: s3
          s3:
            bucket: S3-BUCKET-NAME
            credentialsSecret: ps-cluster1-s3-credentials
            region: us-west-2
            prefix: <BACKUP-PREFIX>
      pitr:
        type: date
        date: "2026-03-20 09:15:00"
        keyringSecret:
          name: ps-cluster1-binlog-server-keyring
          key: keyring.json
        backupSource:
          binlogServer:
            storage:
              s3:
                bucket: S3-BINLOG-BUCKET-NAME
                credentialsSecret: ps-cluster1-s3-credentials
                region: us-west-2
                prefix: binlogs
    ```

If the **base backup** was also encrypted, add `spec.backupSource.storage.encryptionKeySecret` as well. That key is separate from the binlog keyring. See [Encrypted backups](backups-encrypted.md).

!!! warning "Keep your binlog encryption keys safe"

    If a KEK is lost or removed from the keyring, binlogs wrapped with that key are irrecoverable. Store a backup of the keyring Secret separately from the binlog bucket.

Apply the restore and [watch the restore](#view-restore-details). If decryption fails, see [Encrypted binlogs fail to decrypt](debug-backup-restore.md#encrypted-binlogs-fail-to-decrypt).

## Ignore SQL errors during binlog replay

Updates made by `mysql-shell` can produce replication errors during replay, for example `Error_code: 1032` / `HA_ERR_KEY_NOT_FOUND` on `mysql_innodb_cluster_metadata.instances`.

To ignore SQL errors, add `force: true` under `spec.pitr`. This passes `--force` to the MySQL client.

```yaml
spec:
  pitr:
    force: true
    type: date
    date: "2026-04-16 21:12:00"
```

!!! warning "`force: true` can hide data loss"

    The client silently ignores **all** SQL errors during binlog replay, not only metadata errors. Use it only when you accept that risk.

## View restore details

Point-in-time recovery creates a base restore Job (`xb-restore-<name>`) and a PITR Job (`pitr-restore-<name>`). Check both:

```bash
kubectl get job -n <namespace>
kubectl get ps-restore -n <namespace>
```

## Troubleshooting

If the restore fails, see [Troubleshoot backups and restores](debug-backup-restore.md#restores) and [Point-in-time recovery](debug-backup-restore.md#point-in-time-recovery).
