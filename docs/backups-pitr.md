# Point-in-time recovery (PITR)

!!! admonition ""

    This feature is in the tech preview stage. The behavior can change in future releases. We don't recommend using it in production yet, but we encourage you to try it out and share your feedback.

A base backup captures your data at a single moment. That is enough in many cases. If you need to undo a bad migration, recover right before someone dropped the wrong table or meet a tighter recovery point, a base backup alone won't give you that level of
precision. You also need the binary logs generated after that backup. A binary
log records all changes made to the database, such as updates,
inserts, and deletes.

Point-in-time recovery restores the closest base backup, then applies those binary logs up to a timestamp or a specific transaction target (GTID). It is available starting with Operator [1.1.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.1.0.md).

## How it works

The Operator uses [Percona Binlog Server](#enable-binlog-collection) to collect binary logs continuously. The Binlog Server connects to MySQL
as a replication client and uploads binlogs to a dedicated S3-compatible
object storage location. The Binlog Server can resume collection automatically
after being interrupted or stopped.  

When you start a restore with a point-in-time target, the Operator:

1. Finds the binlogs needed for that target
2. Pauses the cluster
3. Restores the closest base physical backup taken with Percona XtraBackup
4. Runs the point-in-time recovery Job that:

    * Starts a temporary `mysqld` instance
    * Retrieves binlogs from the storage and applies them to the
    `mysql` client
    * Shuts down the temporary `mysqld` instance
  
5. Re-bootstraps the cluster from the restored data

```mermaid
flowchart LR
        PS["Percona Server<br/>primary"]
        BS["Binlog Server"]
        S3["S3-compatible<br/>storage"]
        PS -->|"binary logs"| BS
        BS -->|"archived binlogs"| S3
```

Point-in-time recovery is supported for group replication and asynchronous replication. GTID mode must be on (it is on by default).

## Recovery modes

You can restore up to a specific moment in time or
up to a specific transaction. Specify the target in the `PerconaServerMySQLRestore` object:

| Mode | What you specify | How it works | Typical use case |
| ---- | ----------------- | ----------- | ---------------- |
| **GTID** | A GTID set | The Operator restores the database up
to that transaction. | Precise, replication-friendly recovery
when you know the GTID to stop before |
| **Date / time** | A timestamp | The Operator restores the
database up to the specified timestamp | Use when wall-clock
time is easier than GTIDs |


## Enable binlog collection

Binlog collection needs its own S3 (or S3-compatible) location, separate from base backup storage. You must set a folder on the bucket with the `prefix` option. You cannot change that prefix later. Only one Binlog Server Pod is allowed.

1. Configure the `spec.backup.pitr` section in your Custom Resource:

    ```yaml
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
                endpointUrl: https://s3.amazonaws.com # Required for S3-compatible storage. Omit for AWS S3
    ```

2. Apply the configuration:

    ```bash
    kubectl apply -f deploy/cr.yaml -n <namespace>
    ```

3. The Operator starts the Binlog Server Pod. Confirm it is running:

    ```bash
    kubectl get pods -n <namespace> | grep binlog
    ```

By default, collected files are stored in plaintext. You can add an extra layer of protection by [encrypting them](#binlog-encryption) before they are written to the bucket.

To restore, use [Restore with point-in-time recovery](backups-restore-pitr.md). 



## Binlog encryption

!!! admonition "Version added: [1.3.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.3.0.md)"

Binlog encryption gives you an extra protection layer that you
control. This encrypts only the binlog copies in object storage. Binlog encryption is separate from [data-at-rest encryption](encryption.md) on the database and from [encrypted backups](backups-encrypted.md). Use it when you want a key you control, including on S3-compatible storage that has no server-side encryption.

After you enable binlog encryption, Percona Binlog Server encrypts each file **before**
writing it to the bucket, using a key you keep in a Kubernetes
Secret. The same key is used for decrypting files during
point-in-time recovery.

### How encryption works

* You store one or more **key encryption keys (KEKs)** in a keyring Secret. The Operator validates the Secret and mounts it into Binlog Server and the point-in-time recovery Job.
* Binlog Server generates a **data encryption key (DEK)** for each file, encrypts the binlog, wraps the DEK with the selected KEK, and records which KEK was used.
* During restore, the Job decrypts each encrypted file with the matching KEK. Unencrypted files are applied as-is, so you can enable encryption on a bucket that already has plaintext binlogs.

Changing the active KEK affects only **new** files. Binlog Server does not re-encrypt files already in storage. Keep every KEK that was ever used so older files remain recoverable.

### Enable binlog encryption

1. Generate a KEK. Key length must match the KEK cipher: 16 bytes for AES-128, 24 for AES-192, 32 for AES-256.

    ```bash
    openssl rand -hex 16
    ```

2. Create a Secret. Modify the example [`deploy/keyring-secret.yaml` :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/tree/v{{release}}/deploy/keyring-secret.yaml) manifest. Set:

    * `id` — identifier that `kekId` in the Custom Resource refers to
    * `cipher` — cipher used to wrap the DEK, in the format `AES-<128\|192\|256>-<mode>`. Supported modes: `ECB`, `CBC`, `CTR`, `GCM`
    * `data_hex` — the key from step 1. Do not use a sample value in production.

    ```yaml title="binlog-keyring.yaml"
    apiVersion: v1
    kind: Secret
    metadata:
      name: ps-cluster1-binlog-server-keyring
    stringData:
      keyring.json: |
        {
          "version": 1,
          "keys": [
            {
              "id": "alpha",
              "cipher": "AES-128-ECB",
              "data_hex": "<generated-hex-key>"
            }
          ]
        }
    ```

    Apply the manifest:

    ```bash
    kubectl apply -f binlog-keyring.yaml -n <namespace>
    ```

    The Operator rejects a missing, empty, or invalid keyring before it configures Binlog Server.

3. Edit `deploy/cr.yaml` and set these fields under `spec.backup.pitr.binlogServer`. Only CTR mode is supported for binlog **data** encryption. The KEK cipher in the keyring (for example `AES-128-ECB`) is separate from this data cipher.

    * `keyringSecret.name` — Secret that holds the keyring. Required when encryption is enabled. Keep it set after you disable encryption if the bucket still has encrypted binlogs.
    * `keyringSecret.key` — Key inside the Secret. Defaults to `keyring.json`.
    * `storage.encryption.cipher` — `AES-128-CTR`, `AES-192-CTR`, or `AES-256-CTR`. Defaults to `AES-256-CTR`.
    * `storage.encryption.kekId` — `id` of the KEK to use. If omitted, Binlog Server uses the first key in the file.

    ```yaml
    spec:
      backup:
        pitr:
          enabled: true
          binlogServer:
            keyringSecret:
              name: ps-cluster1-binlog-server-keyring
              key: keyring.json
            storage:
              encryption:
                cipher: AES-256-CTR
                kekId: alpha
              s3:
                bucket: my-binlogs
                credentialsSecret: my-s3-secret
                region: us-east-1
                prefix: binlogs
    ```

4. Apply the configuration:

    ```bash
    kubectl apply -f deploy/cr.yaml -n <namespace>
    ```

    The Operator restarts the Binlog Server Pod and starts encrypting new binlogs. Files already in the bucket stay as they are.

### Restore with encrypted binlogs

On the same cluster, the Operator uses the cluster keyring automatically. On a new cluster, or if keys live in a different Secret, set `spec.pitr.keyringSecret` on the restore object. See [Perform point-in-time recovery with encrypted binlogs](backups-restore-pitr.md#restore-with-encrypted-binlogs).

!!! warning "Keep your binlog encryption keys safe"

    To restore from encrypted binlogs, you **must have the original KEKs**. If a key is lost or removed from the keyring, binlogs wrapped with that key are irrecoverable. Back up the keyring Secret separately from the binlog bucket.

### Rotate encryption key

To start encrypting new binlogs with a different KEK, add the new key to the same Secret and **keep every previous key**. Then set `storage.encryption.kekId` to the new `id` and apply the Custom Resource. If you drop an old key, binlogs wrapped with it become unrestorable.

### Disable binlog encryption

To stop encrypting new binlogs, clear `storage.encryption`. Keep `keyringSecret` set so Binlog Server and later restores can still read encrypted files in the bucket:

```bash
kubectl patch ps ps-cluster1 -n <namespace> --type merge \
  -p '{"spec":{"backup":{"pitr":{"binlogServer":{"storage":{"encryption":null}}}}}}'
```

## Implementation specifics

1. Point-in-time recovery is supported for both asynchronous and group replication topologies.
2. The Binlog Server is deployed with the number of Pods restricted to 1. This is because it connects to MySQL as a replication client with a specific server ID and only one instance can connect to the database with the same ID. Any number you set for the `size` in the Custom Resource will be ignored.
3. Enabling the Binlog Server requires the GTID mode to be enabled on the cluster for replaying binary logs. This mode is enabled by default.
4. The cluster is paused during point-in-time recovery. The Operator starts a temporary `mysqld` pod to perform the restore operation using the data PVC.
5. The Binlog Server must be running before the restore begins. The reconciler locates the required binlogs before pausing the cluster.
6. The Binlog Server stores binlogs in a dedicated folder. Therefore, you must specify the folder name (`prefix`) when configuring storage for the Binlog Server.

## Known limitations

* **AWS S3 and S3-compatible storage** are currently supported for Binlog Server to stream binlogs, even if the base backup is on GCS or Azure. Provide credentials using a Secret. Set the endpoint URL, region, and TLS options to match your environment.

* **You cannot change the `prefix` value for the binlog bucket** after you configure Binlog Server.
* **Data-at-rest encryption is not supported** with point-in-time recovery. [Binlog encryption](#binlog-encryption) protects copies in object storage and is independent of Vault.
* **Binlog data encryption** supports only CTR (`AES-128-CTR`, `AES-192-CTR`, `AES-256-CTR`). Changing `kekId` does not re-encrypt existing files.
* **Password change.** If the Operator user password differs from the password stored in the base backup, point-in-time recovery fails. Take a new full backup after you change that password.
* **Restore retries are not idempotent.** If recovery fails after the base backup is restored, a retry does not restore the full backup again. Set `spec.backup.backoffLimit=0` in `cr.yaml` to prevent automatic Job retries.
* **Binlog storage is separate** from base backup storage. During the in-place restore on the same cluster, the Operator uses the settings defined in the `spec.backup.pitr.binlogServer` of the cluster's Custom Resource. For a cross-cluster restore, specify the Binlog storage settings
under `spec.pitr.backupSource.binlogServer` in the restore
object.
* **Large buckets.** Too many objects in the binlog bucket can leave Binlog Server in CrashLoopBackOff. Monitor object count and delete old binlogs. See [Troubleshoot point-in-time recovery](debug-backup-restore.md#point-in-time-recovery).

If a restore fails, inspect the `PerconaServerMySQLRestore` status and the restore and PITR Jobs. See [Troubleshoot backups and restores](debug-backup-restore.md).
