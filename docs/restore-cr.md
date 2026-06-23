# Restore Resource options for Percona Server for MySQL

A Restore resource is a Kubernetes object that tells the Operator how to restore your database from a specific backup. The `deploy/backup/restore.yaml` file is a template for creating restore resources. It defines the `PerconaServerMySQLRestore` resource.

This document describes all available options that you can use to customize a restore. 

## `apiVersion`

Specifies the API version of the Custom Resource.
`ps.percona.com` indicates the group, and `v1alpha1` is the version of the API.

## `kind`

Defines the type of resource being created: `PerconaServerMySQLRestore`.

## `metadata`

The metadata part of the `deploy/backup/restore.yaml` contains metadata about the resource, such as its name and other attributes. It includes the following keys:

* `name` - The name of the restore object used to identify it in your deployment. You use this name to track the restore operation status and view information about it.

## `spec`

This section includes the configuration of a restore resource.

### `clusterName`

Specifies the name of the Percona Server for MySQL cluster to restore. 

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ps-cluster1` |

### `backupName`

Specifies the name of a backup to be used for a restore. This backup should be from the same cluster.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `backup1` |

### `pitr` section

This subsection contains configuration options for **point-in-time recovery**. When present, the Operator restores the base backup and then replays binary logs until the requested **GTID** or **timestamp**. You must enable point-in-time recovery and configure a Binlog Server in the cluster; see [Point-in-time recovery](backups-pitr.md) for details.

#### `pitr.type`

The type of point-in-time recovery. Supported values are:

| Value   | Meaning                                      |
| ------- | -------------------------------------------- |
| `gtid`  | Restore just before the specified GTID target (`pitr.gtid`). |
| `date`  | Restore just before the specified timestamp (`pitr.date`). |

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `gtid` |

#### `pitr.gtid`

The exact GTID set for point-in-time recovery, specified in the format "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee:nnn". Used when `pitr.type` is `gtid`.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5` |

#### `pitr.date`

Timestamp string used when `pitr.type` is `date`. Specified in the format "yyyy-mm-dd hh:mm:ss" .

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `2026-03-30 14:32:00` |

#### `pitr.force`

Forces the `mysql` client to run with the `--force` flag and this silently ignores all SQL errors during binlog replay.

**Warning:** This might result in data loss if underlying replication or data integrity errors are ignored.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch: boolean     | `false` |

### The  `pitr.backupSource` subsection

This subsection contains the BinLog Server settings that the Operator uses for point-in-time recovery when restoring to a cluster that does not have its own Binlog Server — for example, when [restoring to a new Kubernetes environment](backups-restore-to-new-cluster.md#restore-with-point-in-time-recovery). When specified, the Operator starts a temporary Binlog Server from these settings, uses it to locate the required binlogs, and removes it when the restore completes.

#### `pitr.backupSource.binlogServer.size`

Controls the number of Percona Binarylog Server Pods for binlog collection. Defaults to 1. This is the only allowed number. All greater values will be rejected. To learn more, see [Point-in-time recovery](backups-pitr.md).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

#### `pitr.backupSource.binlogServer.image`

The Docker image to use to deploy Percona Binarylog Server.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-binlog-server:0.2.1` |

#### `pitr.backupSource.binlogServer.serverId`

The unique server ID that Percona Binarylog Server uses when connecting to MySQL as a replication client for binlog collection.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `101` |

#### `pitr.backupSource.binlogServer.storage.s3.bucket`

The name of the bucket on AWS S3 or S3-compatible storage where binlogs are streamed. You can use the same values as defined in the `spec.backup.pitr.binlogServer` on the cluster Custom Resource. For the restore to the new cluster, you can copy the settings from the source cluster, but specify a different binlog `prefix`.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `S3-BACKUP-BUCKET-NAME-HERE` |

#### `pitr.backupSource.binlogServer.storage.s3.credentialsSecret`

The Kubernetes Secret for binlog storage. It should contain `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` keys.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ps-cluster1-s3-credentials` |

### `pitr.backupSource.binlogServer.storage.s3.endpointUrl`

The URL to access the bucket on S3-compatible storage. Not needed for AWS S3.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `https://s3.amazonaws.com` |

### `pitr.backupSource.binlogServer.storage.s3.prefix`

Specifies the path prefix (folder) in the bucket where binlogs are stored. After configuring the Binlog Server, this prefix cannot be changed. 

**Important:**  
If you are restoring to a new cluster and both the source and target clusters use the same binlog storage, be sure to specify a different prefix for the target cluster to avoid conflicts.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `PREFIX_NAME` |

### `pitr.backupSource.binlogServer.storage.s3.region`

The region of the bucket. Required for Amazon S3 and for S3-compatible storage.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `us-west-2` |

### `pitr.backupSource.binlogServer.connectTimeout`

Timeout in seconds for establishing a connection to MySQL.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `30` |

### `pitr.backupSource.binlogServer.readTimeout`

The maximum time in seconds the Binlog Server waits to read data from the MySQL instance.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `30` |

### `pitr.backupSource.binlogServer.writeTimeout`

The maximum time in seconds the Binlog Server waits to write data to a remote server.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `30` |

### `pitr.backupSource.binlogServer.idleTime`

The maximum time in seconds the Binlog Server stays in idle mode before trying to reconnect.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `30` |

### `pitr.backupSource.binlogServer.logLevel`

The verbosity level for Binlog Server logs. Supported values are: `info` (default), `warning`, `error`, `debug`.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `info` |

## The `backupSource` subsection

Contains the configuration options to restore from a backup made in a different cluster, namespace, or Kubernetes environment. 

### `backupSource.destination`

Specifies the path to the backup on the storage

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `s3://bucket-name/backup-destination/` |

### `backupSource.storage.s3.bucket`

Specifies the name of the bucket where the backup that you wish to restore from is saved.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     |  |

### `backupSource.storage.s3.credentialsSecret`

Specifies the Secrets object name with the credentials to access the storage with a backup. 

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ps-cluster1-s3-credentials` | 
 

### `backupSource.storage.s3.region`

The [AWS region  :octicons-link-external-16:](https://docs.aws.amazon.com/general/latest/gr/rande.html) to use. Please note **this option is mandatory** for Amazon and all S3-compatible storages.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `us-west-2`|

### `backupSource.storage.type`

Specifies the type of the backup storage. Available options: `s3`, `azure`.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `s3`|

## `containerOptions.env`

The [environment variables set as key-value pairs :octicons-link-external-16:](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/) for the restore job.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>- name: VERIFY_TLS<br>  value: "false"</pre> |

## `containerOptions.args.xtrabackup`

Custom [command line options :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/innovation-release/xtrabackup-option-reference.html) for the [`xtrabackup` Percona XtraBackup tool :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/8.0/xtrabackup-binary-overview.html).

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>- "--someflag=abc"</pre> |

### `containerOptions.args.xbcloud`

Custom [command line options :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/innovation-release/xbcloud-options.html) for the [`xbcloud` Percona XtraBackup tool :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/8.0/xbcloud-binary-overview.html).

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>- "--someflag=abc"</pre> |

### `containerOptions.args.xbstream`

Custom [command line options :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/innovation-release/xbstream-options.html) for the [`xbstream` Percona XtraBackup tool :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/8.0/xbstream-binary-overview.html)

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>- "--someflag=abc"</pre> |
