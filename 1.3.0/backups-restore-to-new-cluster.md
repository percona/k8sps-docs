> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Restore from a backup to a new Kubernetes-based environment

You can restore from a backup as follows:

- On [the same Kubernetes cluster where you made the backup](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-restore.html)
- On a new cluster deployed in a different Kubernetes-based environment.

This document focuses on the restore on a new cluster deployed in a different Kubernetes environment.

## Restore scenarios

To restore a backup onto this cluster, follow the steps below. If the backup was encrypted, include `encryptionKeySecret` as shown in [Restore from an encrypted backup](#restore-from-an-encrypted-backup). If the source used a custom CA, include `caBundle` as shown in [Restore from S3 storage that uses a custom CA](#restore-from-s3-storage-that-uses-a-custom-ca).

To restore to a timestamp or GTID, use [Restore with point-in-time recovery](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-restore-pitr.html#restore-on-a-new-cluster).

To restore from a backup, you create a Restore object using a special restore configuration file. The example of such file is [deploy/backup/restore.yaml](https://github.com/percona/percona-server-mysql-operator/blob/v1.3.0/deploy/backup/restore.yaml) .

You can check available options in the [restore options reference](https://docs.percona.com/percona-operator-for-mysql/1.3.0/restore-cr.html).

## Preconditions

When restoring to a new Kubernetes-based environment, make sure it has a Secrets object with the same user passwords as in the source cluster.

If the backup was [encrypted](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-encrypted.html), the Operator requires the Secret with the same encryption key that was used for the backup. Reference this Secret in the restore resource under `spec.backupSource.storage.encryptionKeySecret`.

If the source cluster verified TLS with a [custom CA](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-storage.html#configure-tls-verification-with-custom-certificates-for-s3-storage), create the CA Secret on the target cluster and set `caBundle` on `spec.backupSource.storage.s3`. For a point-in-time restore to a timestamp or GTID, see [Use a custom CA](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-restore-pitr.html#use-a-custom-ca).

You can export the user Secret from the source cluster and create a Secrets object on the target one. Here’s how to do it:

1. Find the secret name. Run this command on the **cluster where you made the backup**:

   ```
   kubectl get ps ps-cluster1 -n $NAMESPACE -o jsonpath='{.spec.secretsName}'
   ```

   Expected output

   ```
   ps-cluster1-secrets
   ```

1. Export the secret to a file:

   ```
   kubectl get secrets -n $NAMESPACE ps-cluster1-secrets -o yaml > ps-cluster1-secrets.yaml
   ```

1. Remove the `annotations`, `labels`, `creationTimestamp`, `resourceVersion`, `selfLink`, `uid` and `namespace` metadata fields from the resulting file to make it ready for the source cluster. Use the following script to do it:

   ```
   yq eval 'del(.metadata.ownerReferences, .metadata.annotations, .metadata.labels, .metadata.creationTimestamp, .metadata.resourceVersion, .metadata.selfLink, .metadata.uid, .metadata.namespace)' ps-cluster1-secrets.yaml > ps-cluster1-secrets-target.yaml
   ```

   Expected output

   ```
   apiVersion: v1
   data:
     heartbeat: MUBra1Z2IWRNVjNFe0lJM3o=
     monitor: b1k3IyxyWns8eGxVSmFfTiU=
     operator: XT8oYWVhQnd3Sk5FeVdbJg==
     orchestrator: ZF8yXy04PGNTTSl4Qk5ZdFU=
     replication: JFZxVUF4XjBvOFJoI0hPbjZS
     root: QGckTSQtMF9ZeUlYWzV3UWIp
     xtrabackup: REZtVGNbTW5fKUVMfTUqRSEo
   kind: Secret
   metadata:
     name: my-db-ps-db-secrets
   type: Opaque
   ```

1. **On the target cluster**, create the Secrets object. Replace the `<namespace>` with your value:

   ```
   kubectl apply -f ps-cluster1-secrets-target.yaml -n <namespace>
   ```

## Before you begin

1. Export the namespace as an environment variable. Replace the `<namespace>` placeholder with your value:

   ```
   export NAMESPACE = <namespace>
   ```

1. Make sure that the cluster is running. Use this command to check it:

   ```
   kubectl get ps <cluster-name> -n $NAMESPACE
   ```

1. List backups on the source cluster with the following command:

   ```
   kubectl get ps-backup -n $NAMESPACE
   ```

## Restore from a backup

Configure the `PerconaServerMySQLRestore` Custom Resource. Specify the following keys:

- set `spec.clusterName` key to the name of the target cluster to restore the backup on

- configure the `spec.backupSource` subsection to point to the cloud storage where the backup is stored. This subsection should include:

  - a destination key. Take it from the output of the `kubectl get ps-backup` command

  - the necessary [storage configuration keys](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-storage.html#configure-storage-for-backups), just like in the `deploy/cr.yaml` file of the source cluster.

    **S3-compatible storage**

    ```
    apiVersion: ps.percona.com/v1
    kind: PerconaServerMySQLRestore
    metadata:
      name: restore1
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
            endpointUrl: https://URL-OF-THE-S3-COMPATIBLE-STORAGE
            prefix: <PREFIX-WHERE-BACKUP-IS-STORED>
            ...
    ```

    **Google Cloud Storage**

    ```
    apiVersion: ps.percona.com/v1
    kind: PerconaServerMySQLRestore
    metadata:
      name: restore1
    spec:
      clusterName: ps-cluster1
      backupSource:
        destination: gs://BUCKET-NAME/BACKUP-NAME
        storage:
          gcs:
            bucket: operator-testing
            credentialsSecret: ps-cluster1-gcp-credentials
            prefix: <PREFIX-WHERE-BACKUP-IS-STORED>
          type: gcs
    ```

Start the restore:

```
kubectl apply -f deploy/backup/restore.yaml -n $NAMESPACE
```

## Restore from an encrypted backup

Configure the `PerconaServerMySQLRestore` Custom Resource. Specify the following keys:

- `spec.clusterName` — the target cluster
- `spec.backupSource` — destination and storage for the backup, including `encryptionKeySecret` with the same key that encrypted the backup

```
apiVersion: ps.percona.com/v1
kind: PerconaServerMySQLRestore
metadata:
  name: restore1
spec:
  clusterName: ps-cluster1
  backupSource:
    destination: s3://S3-BUCKET-NAME/BACKUP-NAME
    storage:
      encryptionKeySecret:
        name: my-encryption-key
        key: encryptionKey
      type: s3
      s3:
        bucket: S3-BUCKET-NAME
        credentialsSecret: ps-cluster1-s3-credentials
        region: us-west-2
```

Start the restore:

```
kubectl apply -f deploy/backup/restore.yaml -n <namespace>
```

## Restore from S3 storage that uses a custom CA

If the source cluster verified S3-compatible storage with a [custom CA](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-storage.html#configure-tls-verification-with-custom-certificates-for-s3-storage), keep `verifyTLS` enabled and set `caBundle` in the restore resource.

For a restore to a timestamp or GTID, follow [Use a custom CA](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-restore-pitr.html#use-a-custom-ca).

1. Create a CA Secret on the **target** cluster from the same CA file you used on the source. See [Create a CA Secret](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-storage.html#configure-tls-verification-with-custom-certificates-for-s3-storage).

   ```
   kubectl create secret generic minio-ca-bundle \
     --from-file=ca.crt=/path/to/ca.crt -n <target-namespace>
   ```

1. Edit the `deploy/backup/restore.yaml` manifest and set `caBundle` on `spec.backupSource.storage.s3` to that Secret.

```
apiVersion: ps.percona.com/v1
kind: PerconaServerMySQLRestore
metadata:
  name: restore1
spec:
  clusterName: ps-cluster1
  backupSource:
    destination: s3://S3-BUCKET-NAME/BACKUP-NAME
    storage:
      type: s3
      verifyTLS: true
      s3:
        bucket: S3-BUCKET-NAME
        credentialsSecret: ps-cluster1-s3-credentials
        region: us-west-2
        endpointUrl: https://minio-service:9000
        prefix: <PREFIX-WHERE-BACKUP-IS-STORED>
        caBundle:
          name: minio-ca-bundle
          key: ca.crt
```

Start the restore:

```
kubectl apply -f deploy/backup/restore.yaml -n <namespace>
```

## View restore details

When you start the restore, the restore job is created. You can check the job details using these commands:

```
kubectl get job
```

Sample output

```
xb-restore-restore2                                Running    0/1                      0s
xb-restore-restore2                                Complete             1/1           25s        25s
```

You can check the restore progress with this command:

```
kubectl get ps-restore -n $NAMESPACE
```

## Post-restore steps

Make a fresh base backup to start a new timeline for subsequent restores.

## Troubleshooting

If you face issues with restore, refer to [Troubleshoot backups and restores](https://docs.percona.com/percona-operator-for-mysql/1.3.0/debug-backup-restore.html#restores).
