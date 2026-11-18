> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Making on-demand backup

## Before you begin

1. Export the namespace as an environment variable. Replace the `<namespace>` placeholder with your value:

   ```
   export NAMESPACE = <namespace>
   ```

1. Check the configuration of the `PerconaServerMySQL` object:

   - Check that the `backup.enabled` key is set to `true`. Use the following command:

   ```
   kubectl get ps <cluster-name> -n $NAMESPACE -o jsonpath='{.spec.backup.enabled}'
   ```

   - Verify that you have [configured backup storage](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-storage.html) and specified its configuration in the `backup.storages` subsection of the Custom Resource.

1. For incremental backups, check [implementation specifics and rules](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-incremental.html#implementation-specifics-and-rules).

## Backup steps

To make an on-demand backup, use *a special backup configuration YAML file*. The example of such file is [deploy/backup/backup.yaml](https://github.com/percona/percona-server-mysql-operator/blob/v1.3.0/deploy/backup/backup.yaml) .

You can check available options in the [Backup resource reference](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backup-cr.html)

Specify the following keys:

- Set the `metadata.name` key to assign a name to the backup.
- Set the `spec.clusterName` key to the name of your cluster.
- Set the `spec.storageName` key to a storage configuration defined in your `deploy/cr.yaml` file.
- Set the `spec.type` key to make an [incremental backup](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-incremental.html). When unset, a full backup is made by default.
- Optionally, specify the base backup for the `spec.incrementalBaseBackupName`. This option is only valid for the `spec.type=incremental`.
- Optionally, add the `percona.com/delete-backup` entry under `metadata.finalizers` to enable deletion of backup files from a cloud storage when the backup object is removed (manually or by schedule).

Pass this information to the Operator:

**via the YAML manifest**

1. Edit the `deploy/backup/backup.yaml` file:

   ```
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

1. Start the backup process:

   ```
   kubectl apply -f deploy/backup/backup.yaml -n $NAMESPACE
   ```

**via the command line**

Instead of storing backup settings in a separate file, you can pass them directly to the `kubectl apply` command as follows:

```
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

```
kubectl get ps-backup -n $NAMESPACE
```

## View backup size

Version added: [1.3.0](https://docs.percona.com/percona-operator-for-mysql/1.3.0/ReleaseNotes/index.html)

After a backup succeeds, the Operator records its size on the Backup object.

The Backup object has two fields:

- `status.size` is the stored size in IEC units (`KiB`, `MiB`, `GiB`).
- `status.uncompressedSize` is the size before compression. The two values differ only for [compressed backups](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-compressed.html).

To view the backup size, run:

```
kubectl get ps-backup <backup-name> -n $NAMESPACE \
  -o jsonpath='{.status.size}{" / uncompressed "}{.status.uncompressedSize}{"\n"}'
```

These fields stay empty while the backup is running or if it failed.

Size reporting requires:

- the Operator and the Custom Resource (`spec.crVersion`) version 1.3.0 or higher.
- Percona XtraBackup 8.4.0-6 and later

For the full field list, see [Backup status](https://docs.percona.com/percona-operator-for-mysql/1.3.0/cr-statuses.html#perconaservermysqlbackup-status).

## Specifying the backup source

When you create a backup object, the Operator selects a Pod to take the backup from. You can see the backup source pod in the backup object’s status:

```
kubectl get ps-backup backup1 -o yaml
```

Sample output

```
apiVersion: ps.percona.com/v1
kind: PerconaServerMySQLBackup
metadata:
  name: backup1
  ...
status:
  backupSource: cluster1-mysql-1.cluster1-mysql.<namespace>
  ...
```

You can specify the source pod in the backup object to run the backup on this specific pod:

```
apiVersion: ps.percona.com/v1
kind: PerconaServerMySQLBackup
metadata:
  name: backup1
  finalizers:
    - percona.com/delete-backup
spec:
  clusterName: ps-cluster1
  storageName: s3-us-west
  sourcePod: ps-cluster1-mysql-2
```

## Troubleshooting

If you face issues with backups, refer to our [Backup troubleshooting guide](https://docs.percona.com/percona-operator-for-mysql/1.3.0/debug-backup-restore.html) for help.
