# Making scheduled backups

Scheduled backups run automatically at times you specify. You configure them in the `backup` section of your Custom Resource using the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml) file.

Before setting up scheduled backups, make sure you have at least one [configured storage](backups-storage.md) in the `backup.storages` subsection.

## Configure a backup schedule

To schedule backups, specify the following configuration in your Custom Resource:

1. Enable backup by setting `backup.enabled` to `true`.
2. Add entries to the `backup.schedule` subsection in your Custom Resource. Each schedule entry requires the following:

    * `name` - a unique name for this backup schedule
    * `schedule` - the backup schedule in [crontab format :octicons-link-external-16:](https://en.wikipedia.org/wiki/Cron). For example, `"0 0 * * 6"` runs every Saturday at midnight.
    * `storageName` - the name of your [configured storage](backups-storage.md) where backups will be stored
    * `keep` (optional) - the number of backups to keep in storage. Older backups are automatically deleted when this limit is reached.

Here's an example configuration that creates a backup every Saturday night at midnight and keeps the last 3 backups:

```yaml
...
backup:
  enabled: true
  storages:
    s3-us-west:
      type: s3
      s3:
        bucket: S3-BACKUP-BUCKET-NAME-HERE
        region: us-west-2
        credentialsSecret: ps-cluster1-s3-credentials
  schedule:
   - name: "sat-night-backup"
     schedule: "0 0 * * 6"
     keep: 3
     storageName: s3-us-west
  ...
```

## Managing multiple backup schedules in the same storage

You can define multiple backup schedules to meet different recovery and compliance needs. For example, you might want daily backups for quick recovery from recent changes and monthly backups for long-term retention or audit purposes.

When you use the same storage location for multiple schedules, be aware of these important limitations:

1. **Retention policy conflicts**: The Operator only applies retention policies to the first schedule in your configuration. For example, if you set daily backups to keep 5 copies and monthly backups to keep 3 copies, the Operator will only keep 5 total backups in storage, not 8 as you might expect. However, all backup objects will still appear in `kubectl get ps-backup` output.

2. **Concurrent backup conflicts**: When multiple schedules run at the same time and write to the same storage path, backups can overwrite each other, resulting in incomplete or corrupted data.

To avoid these issues and ensure each schedule maintains its own retention policy, configure separate storage locations for each schedule. Here's how:

1. Create separate storage configurations in your Custom Resource with different names
2. Specify unique buckets or prefixes for each storage configuration
3. Assign different storage names to specific schedules

Here's an example configuration that uses separate storage locations for daily and monthly backups:

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

In this example, daily backups are stored in `minio1` and monthly backups are stored in `minio2`, each with their own retention policy.

## Monitoring scheduled backups

When a scheduled backup runs, the Operator creates a Kubernetes Job to execute the backup. You can view these jobs to monitor backup execution:

```bash
kubectl get jobs -n <namespace>
```

??? example "Example output"

    ```{.text .no-copy}
    NAME                                                      COMPLETIONS   DURATION   AGE
    xb-cron-ps-cluster2-gcp-20251107152047-9mgo5-gcp         1/1           9s         21s
    ```

To find all backups created by a specific schedule, use the `percona.com/backup-ancestor` label. The label format is `percona.com/backup-ancestor: <hash>-<schedule-name>`, where `<hash>` is a unique identifier and `<schedule-name>` is the name you specified in your schedule configuration.

For example, to find all backups created by the `sat-night-backup` schedule:

```bash
kubectl get ps-backup -l percona.com/backup-ancestor -n <namespace>
```

Or to filter for a specific schedule:

```bash
kubectl get ps-backup -l percona.com/backup-ancestor=0ed1d-sat-night-backup -n <namespace>
```

## Troubleshooting

If you face issues with backups, refer to our [Backup troubleshooting guide](debug-backup-restore.md) for help.
