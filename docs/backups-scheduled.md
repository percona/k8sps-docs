# Making scheduled backups
 

Backups schedule is defined in the `backup` section of the Custom
Resource and can be configured via the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
file.

1. The `backup.storages` subsection should contain at least one [configured storage](backups-storage.md).

2. The `backup.schedule` subsection allows to actually schedule backups:

    * set the `backup.schedule.name` key to some arbitray backup name (this name
        will be needed later to [restore the bakup](backups-restore.md)).

    * specify the `backup.schedule.schedule` option with the desired backup
        schedule in [crontab format :octicons-link-external-16:](https://en.wikipedia.org/wiki/Cron).

    * set the `backup.schedule.storageName` key to the name of your [already configured storage](backups-storage.md).

    * you can optionally set the `backup.schedule.keep` key to the number of
       backups which should be kept in the storage.

Here is an example of the `deploy/cr.yaml` with a scheduled Saturday night
backup kept on the Amazon S3 storage:

```yaml
...
backup:
  storages:
    s3-us-west:
      type: s3
      s3:
        bucket: S3-BACKUP-BUCKET-NAME-HERE
        region: us-west-2
        credentialsSecret: my-cluster-name-backup-s3
  schedule:
   - name: "sat-night-backup"
     schedule: "0 0 * * 6"
     keep: 3
     storageName: s3-us-west
  ...
```

## Managing multiple backup schedules

You can define multiple backup schedules to meet different recovery and compliance needs. For example, create daily backups for quick recovery from recent changes and monthly backups for long-term retention or audit purposes. 

When using the same storage location for multiple schedules, be aware of these important considerations:

1. **Retention policy conflicts.** The Operator only applies retention policies to the first schedule in your configuration. For example, if you set daily backups to keep 5 copies and monthly backups to keep 3 copies, the Operator will only keep 5 total backups in storage, not 8 as you might expect. However, all backup objects will still appear in `kubectl get ps-backup` output.

2. **Concurrent backup conflicts.** When multiple schedules run simultaneously and write to the same storage path, backups can overwrite each other, resulting in incomplete or corrupted data.

To avoid these issues and ensure each schedule maintains its own retention policy, configure separate storage locations for each schedule.

The configuration steps are the following:

1. Create separate storage configurations in your Custom Resource with different names
2. Specify unique buckets or prefixes for each storage configuration
3. Assign different storage names to specific schedules

Here is the example configuration:

    ```yaml
    storages:
      minio1:
        type: s3
        s3:
          credentialsSecret: minio-secret
          bucket: my-bucket
          prefix: minio1
          endpointUrl: "http://minio.minio.svc.cluster.local:9000/"
        verifyTLS: false
      minio2:
        type: s3
        s3:
          credentialsSecret: minio-secret
          bucket: my-bucket
          prefix: minio2
          endpointUrl: "http://minio.minio.svc.cluster.local:9000/"
        verifyTLS: false

    ....

    backup:
      schedule:
      - name: "daily-backup"
        schedule: "0 2 * * *"
        keep: 2
        storageName: minio1
      - name: "monthly-backup"
        schedule: "0 2 1 * *"
        keep: 5
        storageName: minio2
    ```



