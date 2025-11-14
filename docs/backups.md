# About backups

Backing up your database protects your data from loss and corruption, helps ensure business continuity, and lets you quickly recover if something goes wrong.

## How backups work

The Operator stores your MySQL backups outside the Kubernetes cluster on cloud storage. You can use:

* [Amazon S3 or S3-compatible storage :octicons-link-external-16:](https://en.wikipedia.org/wiki/Amazon_S3#S3_API_and_competing_services)
* [Azure Blob Storage :octicons-link-external-16:](https://azure.microsoft.com/en-us/services/storage/blobs/)
* [Google Cloud Storage :octicons-link-external-16:](https://cloud.google.com/storage)

![image](assets/images/backup-s3.svg)

The Operator creates physical backups using [Percona XtraBackup :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/latest/). Here's how it works:

1. Each database Pod includes a sidecar container called `xtrabackup` that runs an HTTP server.
2. When you create a backup, the Operator creates a Job that sends an HTTP request to the backup source pod.
3. The `xtrabackup` container receives the request and starts the backup process.

The following diagram outlines this workflow:

![image](assets/images/backup-job.svg)

## Configuring backups

You configure backups in the `backup` section of your
[deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml)
file. This section includes:

* The [backup.enabled](operator.md#backupenabled) key, which you set to `true` to enable backups
* The `storages` subsection, where you [configure access to your cloud storage](backups-storage.md)

## Backup types

You can create backups in two ways:

* **Scheduled backups**: Configure these in your
    [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml)
    file. The Operator runs them automatically at the times you specify.
* **On-demand backups**: Create these manually whenever you need them. You configure them in the
    [deploy/backup/backup.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/backup.yaml)
    file.
