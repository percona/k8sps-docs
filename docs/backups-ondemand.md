# Making on-demand backup

To make an on-demand backup, the user should first make changes in the
`deploy/cr.yaml` configuration file: set the `backup.enabled` key to
`true` and configure backup storage in the `backup.storages` subsection.

When the `deploy/cr.yaml` file
contains correctly configured keys and is applied with `kubectl` command, use
*a special backup configuration YAML file* with the following contents:

* **backup name** in the `metadata.name` key,

* **Percona Distribution for MySQL Cluster name** in the `clusterName` key,

* **storage name** from `deploy/cr.yaml` in the `spec.storageName` key.

* <a name="finalizers"></a>**S3 backup finalizer** set by the `metadata.finalizers.delete-backup` key (it triggers the actual deletion of backup files from the S3 bucket when there is a manual or scheduled removal of the corresponding backup object).

The example of such file is [deploy/backup/backup.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/backup.yaml).

When the backup destination is configured and applied with kubectl apply -f deploy/cr.yaml command, make backup as follows:

```{.bash data-prompt="$"}
$ kubectl apply -f deploy/backup.yaml
```

!!! note

    Storing backup settings in a separate file can be replaced by
    passing its content to the `kubectl apply` command as follows:

    ```{.bash data-prompt="$"}
    $ cat <<EOF | kubectl apply -f-
    apiVersion: ps.percona.com/v1alpha1
    kind: PerconaServerMySQLBackup
    metadata:
      name: backup1
      finalizers:
        - delete-backup
    spec:
      clusterName: cluster1
      storageName: s3-us-west
    EOF
    ```
