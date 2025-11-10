# Restore the cluster from a previously saved backup

Backup can be restored not only on the Kubernetes cluster where it was made, but
also on any Kubernetes-based environment with the installed Operator.

!!! note

    When restoring to a new Kubernetes-based environment, make sure it
    has a Secrets object with the same user passwords as in the original cluster.
    More details about secrets can be found in [System Users](users.md#system-users).

The example of the restore configuration file is [deploy/backup/restore.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/restore.yaml). The options that can be used in it are described in the [restore options reference](restore-cr.md).

Following things are needed to restore a previously saved backup:

* Make sure that the cluster is running.

* Find out correct names for the **backup** and the **cluster**. Available
    backups can be listed with the following command:

    ```bash
    kubectl get ps-backup
    ```

    !!! note

        Obviously, you can make this check only on the same cluster on
        which you have previously made the backup.

    And the following command will list existing Percona Distribution for MySQL
    Cluster names in the current Kubernetes-based environment:

    ```bash
    kubectl get ps
    ```

When the correct names for the backup and the cluster are known, backup
restoration can be done in the following way.

1. Set appropriate keys in the `deploy/backup/restore.yaml` file.

    * set `spec.clusterName` key to the name of the target cluster to restore
        the backup on,

    * if you are restoring backup on the *same* Kubernetes-based cluster you have
        used to save this backup, set `spec.backupName` key to the name of your
        backup,

    * if you are restoring backup on the Kubernetes-based cluster *different*
        from one you have used to save this backup, set `spec.backupSource`
        subsection instead of `spec.backupName` field to point on the appropriate
        cloud storage:

        === "S3-compatible storage"

            The `backupSource` key should contain `destination` key equal to the
            S3 [bucket :octicons-link-external-16:](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingBucket.html)
            with a special `s3://` prefix, followed by the necessary S3
            configuration keys, same as in `deploy/cr.yaml` file:

            ```yaml
            ...
            backupSource:
              destination: s3://S3-BUCKET-NAME/BACKUP-NAME
              s3:
                bucket: S3-BUCKET-NAME
                credentialsSecret: my-cluster-name-backup-s3
                region: us-west-2
                endpointUrl: https://URL-OF-THE-S3-COMPATIBLE-STORAGE
                ...
            ```

        === "Azure Blob storage"

            The `backupSource` key should contain `destination` key equal to the
            Azure Blob [container :octicons-link-external-16:](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction#containers)
            and backup name, followed by the necessary Azure
            configuration keys, same as in `deploy/cr.yaml` file:

            ```yaml
            ...
            backupSource:
              destination: AZURE-CONTAINER-NAME/BACKUP-NAME
              azure:
                container: AZURE-CONTAINER-NAME
                credentialsSecret: my-cluster-azure-secret
                ...
            ```
2. After that, the actual restoration process can be started as follows:

    ```bash
    kubectl apply -f deploy/backup/restore.yaml
    ```

!!! note

    Storing backup settings in a separate file can be replaced by passing
    its content to the `kubectl apply` command as follows:

    ```bash
    cat <<EOF | kubectl apply -f-
    apiVersion: "ps.percona.com/v1alpha1"
    kind: "PerconaServerMySQLRestore"
    metadata:
      name: "restore1"
    spec:
      clusterName: "ps-cluster1"
      backupName: "backup1"
    EOF
    ```
