# Troubleshoot backups and restores

You can troubleshoot failed backups or restores by checking the status of backup and restore objects, examining the jobs that executed them, and reviewing logs from the jobs and /or the pods created by the Jobs.

The overall troubleshooting workflow looks like this:

1. Check the object status. Use `kubectl get ps-backup` or `kubectl get ps-restore` to see the current state.
2. Review error details. Use `kubectl describe` to get the error message from the `State Description` field.
3. Examine job logs. Check the logs from the backup or restore job for detailed execution information.
4. Check source pod logs. For backups, review logs from the `xtrabackup` container in the source pod. For restores, view logs of the Pod created by the restore Job.
5. Verify configuration. Ensure storage configurations, credentials, and cluster settings are correct.

Refer to the following sections for details.

## Backups

### Check backup status

Start by checking the status of your backup objects:

```bash
kubectl get ps-backup -n <namespace>
```

This shows you all backup objects with their current state. The `STATE` column indicates whether a backup succeeded, failed, or is in progress.

??? example "Example output"

    ```{.text .no-copy}
    NAME                                           STORAGE      DESTINATION                                                  STATE       COMPLETED   AGE
    backup1                                        aws-s3       s3://operator-testing/ps-cluster1-2025-11-07-20:59:28-full   Succeeded   11m         11m
    backup2                                        azure                                                                     Error                   10m
    backup3                                        azure-blob   operator-testing/ps-cluster1-2025-11-07-21:00:14-full        Succeeded   10m         10m
    backup4                                        gcp-cs       s3://operator-testing/ps-cluster1-2025-11-07-21:01:19-full   Succeeded   3m37s       9m29s
    backup5                                        gcp-cs       s3://operator-testing/ps-cluster1-2025-11-07-21:07:20-full   Succeeded   3m17s       3m28s
    cron-ps-cluster1-aws-s3-20251107211029-45srk   aws-s3       s3://operator-testing/ps-cluster1-2025-11-07-21:10:29-full   Succeeded
    ```

### Check backup error details

When a backup fails, use `kubectl describe` to get detailed error information:

```bash
kubectl describe ps-backup <backup-name> -n <namespace>
```

The `Status` section contains the `State` and `State Description` fields that explain why the backup failed.

??? example "Example error output"

    ```{.text .no-copy}
    Name:         backup2
    Namespace:    default
    ...
    Status:
      State:              Error
      State Description:  azure not found in spec.backup.storages in PerconaServerMySQL CustomResource
    Events:               <none>
    ```

Common error scenarios include:

* **Storage not found**: The storage name specified in the backup doesn't exist in the cluster configuration
* **Authentication failures**: Invalid credentials for accessing cloud storage
* **Network issues**: Problems connecting to the storage service
* **Insufficient permissions**: The backup job doesn't have permission to write to the storage location

### Check backup Jobs

When a backup runs, the Operator creates a Kubernetes Job to execute it. You can view these Jobs to see which backups are running or have completed:

```bash
kubectl get jobs -n <namespace>
```

Backup jobs follow this naming pattern:

* `xb-<backup-name>-<storage-name>` for on-demand backups
* `xb-cron-<cluster-name>-<storage-name>-<timestamp>-<hash>-<storage-name>` for scheduled backups

??? example "Example output"

    ```{.text .no-copy}
    NAME                                                     STATUS     COMPLETIONS   DURATION   AGE
    xb-backup1-aws-s3                                        Complete   1/1           14s        11m
    xb-backup3-azure-blob                                    Complete   1/1           12s        10m
    xb-backup4-gcp-cs                                        Complete   1/1           5m52s      9m45s
    xb-backup5-gcp-cs                                        Complete   1/1           10s        3m43s
    xb-cron-ps-cluster1-aws-s3-20251107211029-45srk-aws-s3   Complete   1/1           12s        35s
    ```

### View backup job logs

To see detailed logs from a backup job, use the job name:

```bash
kubectl logs job/<job-name> -n <namespace>
```

Find the name using the steps from the [Check backup Jobs](#check-backup-jobs) section

For example, to view logs from the `xb-backup1-aws-s3` job:

```bash
kubectl logs job/xb-backup1-aws-s3 -n <namespace>
```

These logs show the backup process execution, including Percona XtraBackup operations and any errors that occurred.

??? example "Example output"

    ```{.text .no-copy}
    Defaulted container "xtrabackup" out of: xtrabackup, xtrabackup-init (init)
    Trying to run backup backup1 on ps-cluster1-mysql-1.ps-cluster1-mysql.default
    2025-11-07T20:59:33.889841-00:00 0 [Note] [MY-011825] [Xtrabackup] recognized server arguments: --datadir=/var/lib/mysql 
    2025-11-07T20:59:33.890011-00:00 0 [Note] [MY-011825] [Xtrabackup] recognized client arguments: --backup=1 --stream=xbstream --safe-slave-backup=1 --slave-info=1 --target-dir=/backup/ --user=xtrabackup --password=* 
    xtrabackup version 8.4.0-4 based on MySQL server 8.4.0 Linux (x86_64) (revision id: c584cb20)
    2025-11-07T20:59:33.890062-00:00 0 [Note] [MY-011825] [Xtrabackup] Connecting to MySQL server host: localhost, user: xtrabackup, password: set, port: not set, socket: not set
    2025-11-07T20:59:33.903741-00:00 0 [Note] [MY-011825] [Xtrabackup] Using server version 8.4.6-6
    2025-11-07T20:59:33.934529-00:00 0 [Note] [MY-011825] [Xtrabackup] Not checking slave open temp tables for --safe-slave-backup because host is not a slave
    2025-11-07T20:59:33.934783-00:00 0 [Note] [MY-011825] [Xtrabackup] Executing LOCK TABLES FOR BACKUP ...
    2025-11-07T20:59:33.940450-00:00 0 [Note] [MY-011825] [Xtrabackup] uses posix_fadvise().
    2025-11-07T20:59:33.940508-00:00 0 [Note] [MY-011825] [Xtrabackup] cd to /var/lib/mysql
    ```

You can also view logs from the Pod created by the Job:

```bash
kubectl logs <pod-name> -n <namespace>
```

To find the Pod name, list pods and look for pods with names matching your backup job:

```bash
kubectl get pods -n <namespace> | grep xb-
```

### Find the backup source Pod

Each backup object contains information about which MySQL Pod was used as the backup source. You can retrieve this information using:

```bash
kubectl get ps-backup <backup-name> -o jsonpath='{.status.backupSource}' -n <namespace>
```

For example:

```bash
kubectl get ps-backup backup1 -o jsonpath='{.status.backupSource}'
```

This returns the fully qualified domain name (FQDN) of the source pod, such as `ps-cluster1-mysql-1.ps-cluster1-mysql.default`.

### View backup logs from the source pod

The `xtrabackup` container in the source pod also contains backup logs. To view them, run:

```bash
kubectl logs <source-pod-name> -c xtrabackup -n <namespace>
```

For example, if the backup source is `ps-cluster1-mysql-1`:

```bash
kubectl logs ps-cluster1-mysql-1 -c xtrabackup -n <namespace>
```

These logs show the backup request received by the sidecar container, including the backup destination, storage type, and Percona XtraBackup commands executed.

??? example "Example output"

    ```{.text .no-copy}
    2025-11-07T20:44:11Z    INFO    startServer     starting http server
    2025-11-07T20:59:33Z    INFO    sidecar.create backup   Checking if backup exists       {"namespace": "default", "name": "backup1"}
    2025-11-07T20:59:33Z    INFO    sidecar.create backup   Backup starting {"namespace": "default", "name": "backup1", "destination": "ps-cluster1-2025-11-07-20:59:28-full", "storage": "s3", "xtrabackupCmd": "/usr/bin/xtrabackup --backup --stream=xbstream --safe-slave-backup --slave-info --target-dir=/backup/ --user=xtrabackup ", "xbcloudCmd": "/usr/bin/xbcloud put --parallel=10 --curl-retriable-errors=7 --md5 --storage=s3 --s3-bucket=operator-testing --s3-region=us-east-1   ps-cluster1-2025-11-07-20:59:28-full"}
    2025-11-07T20:59:33.889841-00:00 0 [Note] [MY-011825] [Xtrabackup] recognized server arguments: --datadir=/var/lib/mysql 
    2025-11-07T20:59:33.890011-00:00 0 [Note] [MY-011825] [Xtrabackup] recognized client arguments: --backup=1 --stream=xbstream --safe-slave-backup=1 --slave-info=1 --target-dir=/backup/ --user=xtrabackup --password=* 
    xtrabackup version 8.4.0-4 based on MySQL server 8.4.0 Linux (x86_64) (revision id: c584cb20)
    2025-11-07T20:59:33.890062-00:00 0 [Note] [MY-011825] [Xtrabackup] Connecting to MySQL server host: localhost, user: xtrabackup, password: set, port: not set, socket: not set
    2025-11-07T20:59:33.903741-00:00 0 [Note] [MY-011825] [Xtrabackup] Using server version 8.4.6-6
    2025-11-07T20:59:33.934529-00:00 0 [Note] [MY-011825] [Xtrabackup] Not checking slave open temp tables for --safe-slave-backup because host is not a slave
    2025-11-07T20:59:33.934783-00:00 0 [Note] [MY-011825] [Xtrabackup] Executing LOCK TABLES FOR BACKUP ...
    ```

## Restores

### Check restore status

To check the status of restore operations, run:

```bash
kubectl get ps-restore -n <namespace>
```

This shows all restore objects with their current state.

??? example "Example output"

    ```{.text .no-copy}
    NAME       STATE       AGE
    restore1   Error       5m56s
    restore2   Succeeded   5m37s
    ```

### Check restore error details

When a restore fails, use the `kubectl describe` command to get detailed error information:

```bash
kubectl describe ps-restore <restore-name> -n <namespace>
```

The `Status` section contains the `State` and `State Description` fields that explain why the restore failed.

??? example "Example error output"

    ```{.text .no-copy}
    Name:         restore1
    Namespace:    default
    ...
    Status:
      State:              Error
      State Description:  PerconaServerMySQLBackup backup11 in namespace default is not found
    Events:               <none>
    ```

??? example "Example success output"

    ```{.text .no-copy}
    Name:         restore2
    Namespace:    default
    ...
    Status:
      State:  Succeeded
    Events:   <none>
    ```

Common restore error scenarios include:

* **Backup not found**: The backup specified in the restore doesn't exist
* **Storage access issues**: Problems reading from the backup storage location
* **Cluster state conflicts**: The cluster is not in a state that allows restore
* **Insufficient resources**: Not enough disk space or memory to complete the restore

### Check restore jobs

When a restore runs, the Operator creates a Kubernetes Job to execute it. View these Jobs:

```bash
kubectl get jobs -n <namespace>
```

Restore jobs follow the naming pattern `xb-restore-<restore-name>`.

??? example "Example output"

    ```{.text .no-copy}
    NAME                                                     STATUS     COMPLETIONS   DURATION   AGE
    xb-restore-restore2                                      Complete   1/1           23s        5m42s
    ```

### View restore job logs

To see detailed logs from a restore Job, run:

```bash
kubectl logs job/<restore-job-name> -n <namespace>
```

For example:

```bash
kubectl logs job/xb-restore-restore2 -n <namespace>
```

??? example "Sample output"

    ```{.text .no-copy}
    Defaulted container "xtrabackup" out of: xtrabackup, xtrabackup-init (init)
    ++ awk '/^xtrabackup version/{print $3}'
    ++ awk -F. '{print $1"."$2}'
    ++ xtrabackup --version
    * XTRABACKUP_VERSION=8.4
    * DATADIR=/var/lib/mysql
    ++ grep -c processor /proc/cpuinfo
    * PARALLEL=4
    * XBCLOUD_ARGS='--curl-retriable-errors=7 --parallel=4 '
    * '[' -n true ']'
    * [[ true == \f\a\l\s\e ]]
    ```

### View logs from the Pod created by the restore Job

You can also view logs from the Pod created by the restore Job. To find the Pod name, list pods and look for pods with names matching your restore job:

```bash
kubectl get pods -n <namespace> | grep xb-restore
```

Then check the logs:

```bash
kubectl logs <restore-pod-name> -n <namespace>
```

??? example "Example output"

    ```{.text .no-copy}
    Defaulted container "xtrabackup" out of: xtrabackup, xtrabackup-init (init)
    ++ awk '/^xtrabackup version/{print $3}'
    ++ awk -F. '{print $1"."$2}'
    ++ xtrabackup --version
    + XTRABACKUP_VERSION=8.4
    + DATADIR=/var/lib/mysql
    ++ grep -c processor /proc/cpuinfo
    + PARALLEL=4
    + XBCLOUD_ARGS='--curl-retriable-errors=7 --parallel=4 '
    + '[' -n true ']'
    + [[ true == \f\a\l\s\e ]]
    ```
