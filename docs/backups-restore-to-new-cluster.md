# Restore from a backup to a new Kubernetes-based environment

You can restore from a backup as follows:

* On [the same Kubernetes cluster where you made the backup](backups-restore.md)
* On a new cluster deployed in a different Kubernetes-based environment.

This document focuses on the restore on a new cluster deployed in a different Kubernetes environment.

## Restore scenarios

To restore a backup onto this cluster, follow the steps below. If the backup was encrypted, include `encryptionKeySecret` as shown in [Restore from an encrypted backup](#restore-from-an-encrypted-backup).

To restore to a timestamp or GTID, use [Restore with point-in-time recovery](backups-restore-pitr.md#restore-on-a-new-cluster). 

To restore from a backup, you create a Restore object using a special restore configuration file. The example of such file is [deploy/backup/restore.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/restore.yaml).

You can check available options in the [restore options reference](restore-cr.md).

## Preconditions

When restoring to a new Kubernetes-based environment, make sure it has a Secrets object with the same user passwords as in the source cluster.

If the backup was [encrypted](backups-encrypted.md), the Operator requires the Secret with the same encryption key that was used for the backup. Reference this Secret in the restore resource under `spec.backupSource.storage.encryptionKeySecret`.

You can export the user Secret from the source cluster and create a Secrets object on the target one. Here's how to do it:

1. Find the secret name. Run this command on the **cluster where you made the backup**:

    ```bash
    kubectl get ps ps-cluster1 -n $NAMESPACE -o jsonpath='{.spec.secretsName}'
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        ps-cluster1-secrets
        ```

2. Export the secret to a file:

    ```bash
    kubectl get secrets -n $NAMESPACE ps-cluster1-secrets -o yaml > ps-cluster1-secrets.yaml
    ```

3. Remove the `annotations`, `labels`, `creationTimestamp`, `resourceVersion`, `selfLink`, `uid` and `namespace` metadata fields from the resulting file to make it ready for the source cluster. Use the following script to do it:

    ```bash
    yq eval 'del(.metadata.ownerReferences, .metadata.annotations, .metadata.labels, .metadata.creationTimestamp, .metadata.resourceVersion, .metadata.selfLink, .metadata.uid, .metadata.namespace)' ps-cluster1-secrets.yaml > ps-cluster1-secrets-target.yaml
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
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

4. **On the target cluster**, create the Secrets object. Replace the `<namespace>` with your value:

    ```bash
    kubectl apply -f ps-cluster1-secrets-target.yaml -n <namespace>
    ```

## Before you begin

1. Export the namespace as an environment variable. Replace the `<namespace>` placeholder with your value:

    ```bash
    export NAMESPACE = <namespace>
    ```

2. Make sure that the cluster is running. Use this command to check it:

    ```bash
    kubectl get ps <cluster-name> -n $NAMESPACE
    ```

3. List backups on the source cluster with the following command:

    ```bash
    kubectl get ps-backup -n $NAMESPACE
    ```

## Restore from a backup

Configure the `PerconaServerMySQLRestore` Custom Resource. Specify the following keys:

* set `spec.clusterName` key to the name of the target cluster to restore the backup on
* configure the `spec.backupSource` subsection to point to the cloud storage where the backup is stored. This subsection should include:

    * a destination key. Take it from the output of the `kubectl get ps-backup` command
    * the necessary [storage configuration keys](backups-storage.md#configure-storage-for-backups), just like in the `deploy/cr.yaml` file of the source cluster.

        === "S3-compatible storage"

            ```yaml
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

        === "Google Cloud Storage"

            ```yaml
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

```bash
kubectl apply -f deploy/backup/restore.yaml -n $NAMESPACE
```

## Restore from an encrypted backup

Configure the `PerconaServerMySQLRestore` Custom Resource. Specify the following keys:

* `spec.clusterName` — the target cluster
* `spec.backupSource` — destination and storage for the backup, including `encryptionKeySecret` with the same key that encrypted the backup


```yaml
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

```bash
kubectl apply -f deploy/backup/restore.yaml -n <namespace>
```

## View restore details

When you start the restore, the restore job is created. You can check the job details using these commands:

```bash
kubectl get job
```

??? example  "Sample output"

    ```
    xb-restore-restore2                                Running    0/1                      0s
    xb-restore-restore2                                Complete             1/1           25s        25s
    ```

You can check the restore progress with this command:

```bash
kubectl get ps-restore -n $NAMESPACE
```

## Post-restore steps

Make a fresh base backup to start a new timeline for subsequent restores.

## Troubleshooting

If you face issues with restore, refer to [Troubleshoot backups and restores](debug-backup-restore.md#restores).
