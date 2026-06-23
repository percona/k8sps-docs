# Encrypted backups

!!! note "Version added: [1.2.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.2.0.md)"

Percona Operator for MySQL uses [Percona XtraBackup :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/latest/) to create physical backups. By default, backups are unencrypted. To add an extra security layer, you can encrypt backup files before they are stored in your cloud object storage. Encryption is applied inline during the backup stream, so files in the storage stay protected at rest even if the storage account is shared or accessed without authorization. This helps you meet compliance requirements without adding external encryption tools or changing how you run scheduled and on-demand backups.

Encryption is available for the Group Replication and asynchronous replication cluster types.

## Backup flow

You can encrypt both full and [incremental](backups-incremental.md) backups, whether they are [scheduled](backups-scheduled.md) or [on-demand](backups-ondemand.md). When encrypting incremental backups, the key must be the same for every backup in an incremental chain.

You can enable encryption globally for all backups, or set different encryption options for each storage. The setting you configure for a specific storage overrides the global setting. This flexibility lets
you tailor backup security to your unique requirements.

## Restore flow

During the in-place restore to the same cluster, the Operator recognizes the encrypted backup and uses the same encryption key Secret to decrypt the data. 

For a restore on a new cluster or in a different Kubernetes environment, provide the same encryption key in the Restore resource. This is required because the Operator has no access to the encryption key Secrets from the source cluster.

**The key used for the restore must match the key used to encrypt the backup**. If the key is lost or rotated, the backup cannot be recovered.

## Configuration 

### Create an encryption key Secret

Create a Kubernetes Secret that holds the encryption key. The encryption key must be base64-encoded.

To encode the key, use the following command:

=== ":material-linux: On Linux"

    ```bash
    echo -n 'key-string' | base64 --wrap=0 
    ```

=== ":material-apple: On Mac"

    ```bash
    echo -n 'key-string' | base64
    ```

Create a Secret configuration file and specify the encoded string within. Here's the example of the file `encryption-key.yaml`:

```yaml title="encryption-key.yaml"
apiVersion: v1
kind: Secret
metadata:
  name: my-encryption-key
stringData:
  encryptionKey: <base64-encoded-string>
```

Create the Secret object:

```bash
kubectl apply -f encryption-key.yaml -n <namespace>
```

Store this Secret securely and back it up separately from your database backups. If you lose the key, encrypted backups cannot be restored.

### Enable encryption for all backups

1. Edit the `deploy/cr.yaml` cluster Custom Resource and reference the Secret under `spec.backup.encryptionKeySecret`. Specify the name. The `key` field is optional and defaults to `encryptionKey`. The Operator never stores the key value, it only references it via the Secret.

   Here's the sample configuration:

   ```yaml
   spec:
     backup:
       enabled: true
       encryptionKeySecret:
         name: my-encryption-key
         key: encryptionKey
       storages:
         s3-us-west:
           type: s3
           s3:
             bucket: S3-BACKUP-BUCKET-NAME-HERE
             region: us-west-2
             credentialsSecret: ps-cluster1-s3-credentials
   ```

2. Apply the new configuration:

    ```bash
    kubectl apply -f deploy/cr.yaml -n <namespace>
    ```

This configuration applies to all backup storages unless a storage entry defines its own key.

### Enable encryption for a specific storage

To use a different key for a particular storage location, create a new Secret that stores this key. 

Next, configure the `encryptionKeySecret` subsection in the Custom Resource under that storage entry. 

This example configuration shows how to override encryption settings for the S3 storage. The new encryption key is stored within the Secret named `my-encryption-key-s3`:

```yaml
spec:
  backup:
    encryptionKeySecret:
      name: my-encryption-key
      key: encryptionKey
    storages:
      s3-us-west:
        encryptionKeySecret:
          name: my-encryption-key-s3
          key: encryptionKey
        type: s3
        s3:
          bucket: S3-BACKUP-BUCKET-NAME-HERE
          region: us-west-2
          credentialsSecret: ps-cluster1-s3-credentials
```

After you apply the configuration, the storage-level encryption settings take precedence over the global settings.

### Tune the encryption algorithm and performance

The Operator uses **AES256** by default. To use a different cipher or adjust encryption performance, pass Percona XtraBackup options through `containerOptions.args.xtrabackup` in the cluster Custom Resource or in a specific backup or restore manifest. See [Fine-tuning backup and restore operations](backups-fine-tune.md) for how global and per-job settings interact.

The example configuration shows how to tune Percona XtraBackup globally on the cluster level.

```yaml
spec:
  backup:
    storages:
      s3-us-west:
        containerOptions:
          args:
            xtrabackup:
              - "--encrypt=AES192"
              - "--encrypt-threads=3"
              - "--encrypt-chunk-size=64K"
```

## Make an encrypted backup

You don't need any additional configuration to make an encrypted backup. The Operator uses the encryption settings from the Custom Resource for both [on-demand](backups-ondemand.md) and [scheduled](backups-scheduled.md) backups.

## Restore from an encrypted backup on the same cluster

When you restore using [`backupName`](restore-cr.md#backupname) on the same cluster where the backup was created, the Operator reads the encryption key from the cluster Custom Resource automatically. No extra configuration is required as long as the same `encryptionKeySecret` is still defined in the cluster.

See [Restore the cluster from a previously saved backup](backups-restore.md).

## Restore from an encrypted backup on a new cluster

When you restore from a backup on a different cluster or in a different Kubernetes environment, you must provide the encryption key in the restore resource. The Operator has no access to Secrets from the source cluster.

The key used for restore **must match** the key that was used to encrypt the backup.

See [Restore from a backup to a new Kubernetes-based environment](backups-restore-to-new-cluster.md#restore-from-an-encrypted-backup) for the full cross-cluster restore workflow.

!!! warning "Keep your backup encryption keys safe"

    To restore from an encrypted backup, you **must have the original encryption key**. If the key is lost or rotated, your backups are irrecoverable. Always ensure you have a secure and reliable process for managing and backing up encryption keys separately from your database backups.
