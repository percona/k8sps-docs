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
| **GTID** | A GTID set | The Operator restores the database up to that transaction. | Precise, replication-friendly recovery when you know the GTID to stop before |
| **Date / time** | A timestamp | The Operator restores the database up to the specified timestamp | Use when wall-clock time is easier than GTIDs |


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

To restore, use [Restore with point-in-time recovery](backups-restore-pitr.md).

## Verify TLS with a custom CA

!!! note "Version added: [1.3.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.3.0.md)"

You can use your organization's CA to verify TLS to S3-compatible storage. This way you ensure secure communication and comply with the security policies in your organization.

This setting is independent from [configuring custom certificates for a backup storage](backups-storage.md#configure-tls-verification-with-custom-certificates-for-s3-storage). Configuring a custom CA for backups does not apply it to Binlog Server.

You must run the Operator 1.3.0 and have a Custom Resource version (`spec.crVersion`) set to `1.3.0` or later.

The steps are:

--8<-- "backups-storage.md:casecret"

1. Modify the storage configuration for the Binlog Server in the Custom Resource and specify the following:
  
    * `backup.pitr.binlogServer.storage.s3.caBundle.name` is the name of the Secret you created
    * `backup.pitr.binlogServer.storage.s3.caBundle.key` is the key in the Secret that holds the CA certificate. If you omit `key`, the Operator uses `ca.crt`.

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
                  endpointUrl: https://minio-service:9000
                  caBundle:
                    name: minio-ca-bundle
                    key: ca.crt
      ```

2. Apply the configuration:
     
    ```bash
    kubectl apply -f deploy/cr.yaml -n <namespace>
    ```

When you restore with `backupSource`, create the CA Secret on the target cluster and set `caBundle` on the restore object. See [Use a custom CA](backups-restore-pitr.md#use-a-custom-ca).

## Implementation specifics

1. Point-in-time recovery is supported for both asynchronous and group replication topologies.
2. The Binlog Server is deployed with the number of Pods restricted to 1. This is because it connects to MySQL as a replication client with a specific server ID and only one instance can connect to the database with the same ID. Any number you set for the `size` in the Custom Resource will be ignored.
3. Enabling the Binlog Server requires the GTID mode to be enabled on the cluster for replaying binary logs. This mode is enabled by default.
4. The cluster is paused during point-in-time recovery. The Operator starts a temporary `mysqld` pod to perform the restore operation using the data PVC.
5. The Binlog Server must be running before the restore begins. The reconciler locates the required binlogs before pausing the cluster.
6. The Binlog Server stores binlogs in a dedicated folder. Therefore, you must specify the folder name (`prefix`) when configuring storage for the Binlog Server.

## Known limitations

Also see [Known limitations](limitations.md#point-in-time-recovery) for a summary of Operator-wide constraints that affect this feature.

* **AWS S3 and S3-compatible storage** are currently supported for Binlog Server to stream binlogs, even if the base backup is on GCS or Azure. Provide credentials using a Secret. Set the endpoint URL, region, and [TLS options to match your environment](#verify-tls-with-a-custom-ca).

* **You cannot change the `prefix` value for the binlog bucket** after you configure Binlog Server.
* **Data-at-rest encryption is not supported** with point-in-time recovery.
* **Password change.** If the Operator user password differs from the password stored in the base backup, point-in-time recovery fails. Take a new full backup after you change that password.
* **Restore retries are not idempotent.** If recovery fails after the base backup is restored, a retry does not restore the full backup again. Set `spec.backup.backoffLimit=0` in `cr.yaml` to prevent automatic Job retries.
* **Binlog storage is separate** from base backup storage. During the in-place restore on the same cluster, the Operator uses the settings defined in the `spec.backup.pitr.binlogServer` of the cluster's Custom Resource. For a cross-cluster restore, specify the Binlog storage settings
under `spec.pitr.backupSource.binlogServer` in the restore
object.
* **Large buckets.** Too many objects in the binlog bucket can leave Binlog Server in CrashLoopBackOff. Monitor object count and delete old binlogs. See [Troubleshoot point-in-time recovery](debug-backup-restore.md#point-in-time-recovery).

If a restore fails, inspect the `PerconaServerMySQLRestore` status and the restore and PITR Jobs. See [Troubleshoot backups and restores](debug-backup-restore.md).
