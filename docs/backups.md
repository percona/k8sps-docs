# Providing Backups

The Operator stores MySQL backups outside the Kubernetes cluster: on 
[Amazon S3 or S3-compatible storage :octicons-link-external-16:](https://en.wikipedia.org/wiki/Amazon_S3#S3_API_and_competing_services),
or on [Azure Blob Storage :octicons-link-external-16:](https://azure.microsoft.com/en-us/services/storage/blobs/).

![image](assets/images/backup-s3.svg)

The Operator currently allows [doing logical cluster backups on-demand](backups-ondemand.md)
(i.e. manually at any moment). 

It uses the [Percona XtraBackup :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/latest/) tool.

Backups are controlled by the `backup` section of the
[deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
file. This section contains the [backup.enabled](operator.md#backupenabled) key
(it should be set to `true` to enable backups), and the number of options in the
`storages` subsection, [needed to access cloud to store backups](backups-storage.md).

