> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# About backups

Backing up your database protects your data from loss and corruption, helps ensure business continuity, and lets you quickly recover if something goes wrong.

## How backups work

The Operator stores your MySQL backups outside the Kubernetes cluster on cloud storage. You can use:

- [Amazon S3 or S3-compatible storage](https://en.wikipedia.org/wiki/Amazon_S3#S3_API_and_competing_services)
- [Azure Blob Storage](https://azure.microsoft.com/en-us/services/storage/blobs/)
- [Google Cloud Storage](https://cloud.google.com/storage)

The Operator creates physical backups using [Percona XtraBackup](https://docs.percona.com/percona-xtrabackup/latest/) . Here’s how it works:

1. Each database Pod includes a sidecar container called `xtrabackup` that runs an HTTP server.
1. When you create a backup, the Operator creates a Job that sends an HTTP request to the backup source Pod.
1. The `xtrabackup` container receives the request and starts the backup process.
1. Backups are streamed to storage; the Operator does not keep a separate local copy of the backup on disk.

Important

For [asynchronous replication](https://docs.percona.com/percona-operator-for-mysql/1.3.0/architecture.html#asynchronous-replication-tech-preview) clusters, the Operator uses a replica as the backup source and stops replication for the duration of the backup. If a cluster consists of only 2 members, that replica is the only standby. See [Known limitations](https://docs.percona.com/percona-operator-for-mysql/1.3.0/limitations.html#replication-and-topology).

The following diagram outlines this workflow:

## Backup types

You can make the following types of physical backups:

- Full backup - contains full data set
- An incremental backup - contains only the changes that occurred since the previous backup. To learn more, read [Incremental backups](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-incremental.html).

## Configuring backups

You configure backups in the `backup` section of the [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/v1.3.0/deploy/cr.yaml) file. At minimum, you must:

- Set [backup.enabled](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#backupenabled) to `true` to enable backups
- Configure at least one [storage location](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-storage.html) in `backup.storages` subsection.

You can customize a backup type, scheduling and encryption. See [Making scheduled backups](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-scheduled.html), [Creating a backup on demand](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-ondemand.html), and [Encrypted backups](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-encrypted.html) tutorials for the guidelines.

To fine-tune how long a backup waits to start, see [Set a waiting time for a backup to start](#set-a-waiting-time-for-a-backup-to-start). To suspend backups when the cluster is unhealthy, see [Suspend backups on an unhealthy cluster](#suspend-backups-on-an-unhealthy-cluster).

For the full set of backup-related fields, see the [Custom Resource reference](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#operator-backup-section) and the [Backup Resource reference](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backup-cr.html) for per-backup options.

## Backup runs

You can create backups in two ways:

- **Scheduled backups**: Configure these in your [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/v1.3.0/deploy/cr.yaml) file. The Operator runs them automatically at the times you specify.
- **On-demand backups**: Create these manually whenever you need them. You configure them in the [deploy/backup/backup.yaml](https://github.com/percona/percona-server-mysql-operator/blob/v1.3.0/deploy/backup/backup.yaml) file.

## Set a waiting time for a backup to start

Version added: [1.3.0](https://docs.percona.com/percona-operator-for-mysql/1.3.0/ReleaseNotes/index.html)

You can fine-tune a backup queue by assigning a waiting time for a backup to start.

Use the [`backup.startingDeadlineSeconds`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#backupstartingdeadlineseconds) option in the `deploy/cr.yaml` file to set this time for all backups. Override it for an on-demand backup by setting the [`startingDeadlineSeconds`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backup-cr.html#startingdeadlineseconds) option on the `PerconaServerMySQLBackup` object. If the Operator does not create the Job before this time expires, the backup state becomes `Error` with `stateDescription: backup did not start before startingDeadlineSeconds expired`.

This timer also covers a backup that is waiting because the cluster is not ready. See [Suspend backups on an unhealthy cluster](#suspend-backups-on-an-unhealthy-cluster).

## Suspend backups on an unhealthy cluster

Version added: [1.3.0](https://docs.percona.com/percona-operator-for-mysql/1.3.0/ReleaseNotes/index.html)

Your database cluster can become unhealthy. For example, when one of the Pods crashes and restarts. The Operator monitors the database cluster state while a backup is running and suspends it for an unhealthy cluster to reduce the load on the cluster.

When the cluster is ready again, the Operator resumes the backup Job. Resuming a Job creates a new Pod, so the backup starts over from the beginning rather than continuing from where it stopped.

To offload the database cluster even more, you can define how long a backup remains suspended. Use the [`backup.suspendedDeadlineSeconds`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#backupsuspendeddeadlineseconds) option in the `cr.yaml` file for all backups. Or override it with the [`suspendedDeadlineSeconds`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backup-cr.html#suspendeddeadlineseconds) option in the `deploy/backup/backup.yaml` configuration files for a specific backup. The setting in the `backup.yaml` file has a higher priority.

After this duration expires, the Operator automatically marks this backup as `Failed` with `stateDescription: backup did not resume before suspendedDeadlineSeconds expired`, and deletes the suspended Job.

A backup that has not started yet does not move to `Suspended`. If the cluster is still unready when `startingDeadlineSeconds` expires, the backup state changes to `Error`. See [Set a waiting time for a backup to start](#set-a-waiting-time-for-a-backup-to-start).

For the full list of backup states, see [Backup state values](https://docs.percona.com/percona-operator-for-mysql/1.3.0/cr-statuses.html#backup-state-values).

## Point-in-time recovery

Starting with Operator 1.1.0, you can combine a base backup with archived binary logs to [restore to a specific GTID or timestamp](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-restore-pitr.html). [Enable binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.html#enable-binlog-collection) to stream binlogs to the object storage alongside your normal backup configuration.

You can also [encrypt binlogs](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.html#binlog-encryption) for an additional security layer.
