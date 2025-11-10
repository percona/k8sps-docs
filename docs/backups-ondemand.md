# Making on-demand backup

## Before you begin 

1. Export the namespace as an environment variable. Replace the `<namespace>` placeholder with your value:

    ```bash
    export NAMESPACE = <namespace>
    ```

2. Check the configuration of the `PerconaServerMySQL` object:

    * Check that the `backup.enabled` key is set to `true`. Use the following command:

       ```bash
       kubectl get ps <cluster-name> -n $NAMESPACE -o jsonpath='{.spec.backup.enabled}'
       ```

    * Verify that you have [configured backup storage](backups-storage.md) and specified its configuration in the `backup.storages` subsection of the Custom Resource.

## Backup steps

To make an on-demand backup, use
*a special backup configuration YAML file*. The example of such file is [deploy/backup/backup.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/backup.yaml).

You can check available options in the [Backup resource reference](backup-cr.md)

Specify the following keys:

* Set the `metadata.name` key to assign a name to the backup.
* Set the `spec.clusterName` key to the name of your cluster.
* Set the `spec.storageName` key to a storage configuration defined in your `deploy/cr.yaml` file.
* Optionally, add the `percona.com/delete-backup` entry under `metadata.finalizers` to enable deletion of backup files from a cloud storage when the backup object is removed (manually or by schedule).

Pass this information to the Operator:

=== "via the YAML manifest"

    1. Edit the `deploy/backup/backup.yaml` file:
       
        ```yaml
        apiVersion: ps.percona.com/v1
        kind: PerconaServerMySQLBackup
        metadata:
          name: backup1
          finalizers:
            - percona.com/delete-backup
        spec:
          clusterName: ps-cluster1
          storageName: s3-us-west
        ```
        
    2. Start the backup process:

        ```bash
        kubectl apply -f deploy/backup/backup.yaml -n $NAMESPACE
        ```

=== "via the command line"

    Instead of storing backup settings in a separate file, you can pass them directly to the `kubectl apply` command as follows:

    ```bash
    cat <<EOF | kubectl apply -n $NAMESPACE -f-
    apiVersion: ps.percona.com/v1
    kind: PerconaServerMySQLBackup
    metadata:
      name: backup1
      finalizers:
        - percona.com/delete-backup
    spec:
      clusterName: ps-cluster1
      storageName: s3-us-west
    EOF
    ```

List backups with this command:

```bash
kubectl get ps-backup -n $NAMESPACE
```