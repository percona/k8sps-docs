> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Backup Resource options for Percona Server for MySQL

The `PerconaServerMySQLBackup` Custom Resource is used to define and manage backups for a Percona Server for MySQL cluster. This CR allows you to specify the backup configuration, including the cluster to back up and the storage location.

This document describes all available options that you can use to customize your backups.

## `apiVersion`

Specifies the API version of the Custom Resource. `ps.percona.com` indicates the group, and `v1alpha1` is the version of the API.

## `kind`

Defines the type of resource being created: `PerconaServerMySQLBackup`.

## `metadata`

The metadata part of the `deploy/backup/backup.yaml` contains metadata about the resource, such as its name and other attributes. It includes the following keys:

- `finalizers` ensure safe deletion of resources in Kubernetes under certain conditions. This subsection includes the following finalizers:

  - `percona.com/delete-backup` - deletes the backup resource after the backup data is deleted from storage.

- `name` - The name of the backup resource used to identify it in your deployment. You also use the backup name for the restore operation.

## `spec`

This subsection includes the configuration of a backup resource.

### `sourcePod`

Specifies the MySQL instance to take a backup from. When defined, takes precedence, regardless of the cluster type (async or group-replication) and topology. Overrides the `sourcePod` value if defined in the `deploy/cr.yaml`.

| Value type | Example               |
| ---------- | --------------------- |
| string     | `ps-cluster1-mysql-0` |

### `clusterName`

Specifies the name of the Percona Server for MySQL cluster to back up.

| Value type | Example       |
| ---------- | ------------- |
| string     | `ps-cluster1` |

### `storageName`

Specifies the name of the storage where to save a backup. It must match the name you specified in the `spec.backup.storages` subsection of the `deploy/cr.yaml` file.

If the cluster or the matching storage entry defines [`encryptionKeySecret`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#backupencryptionkeysecretname), the Operator encrypts this backup automatically. See [Encrypted backups](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-encrypted.html).

| Value type | Example      |
| ---------- | ------------ |
| string     | `s3-us-west` |

### `type`

Specifies the backup type. Supported values: `full`, `incremental`. When undefined, defaults to `full`.

| Value type | Example |
| ---------- | ------- |
| string     | `full`  |

### `incrementalBaseBackupName`

Specifies the **full backup** to serve as the base for the incremental chain. This option is only valid when `type` is set to `incremental`. When undefined, the Operator uses the most recent full backup as the base for the incremental chain. Both the specified base backup and the incremental backup must be on the same storage.

| Value type | Example     |
| ---------- | ----------- |
| string     | `ps-backup` |

### `startingDeadlineSeconds`

The maximum time, in seconds, a backup can wait to start before the Operator marks it as `Error`. When defined, takes precedence over the cluster-level [`backup.startingDeadlineSeconds`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#backupstartingdeadlineseconds).

| Value type | Example |
| ---------- | ------- |
| int        | `900`   |

### `suspendedDeadlineSeconds`

The maximum time, in seconds, a [suspended](https://docs.percona.com/percona-operator-for-mysql/1.3.0/cr-statuses.html#backup-state-values) backup can wait to resume before the Operator marks it as failed. The default is `0`, which means the Operator does not enforce a resume deadline.

When defined, takes precedence over the cluster-level [`backup.suspendedDeadlineSeconds`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#backupsuspendeddeadlineseconds).

| Value type | Example |
| ---------- | ------- |
| int        | `900`   |

### `containerOptions.env`

The [environment variables set as key-value pairs](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/) for the backup job.

| Value type | Example                               |
| ---------- | ------------------------------------- |
| subdoc     | `- name: VERIFY_TLS   value: “false”` |

### `containerOptions.args.xtrabackup`

Custom [command line options](https://docs.percona.com/percona-xtrabackup/latest/xtrabackup-option-reference.html) for the [`xtrabackup` Percona XtraBackup tool](https://docs.percona.com/percona-xtrabackup/8.0/xtrabackup-binary-overview.html) .

| Value type | Example             |
| ---------- | ------------------- |
| subdoc     | `- “–someflag=abc”` |

### `containerOptions.args.xbcloud`

Custom [command line options](https://docs.percona.com/percona-xtrabackup/latest/xbcloud-options.html) for the [`xbcloud` Percona XtraBackup tool](https://docs.percona.com/percona-xtrabackup/8.0/xbcloud-binary-overview.html) .

| Value type | Example             |
| ---------- | ------------------- |
| subdoc     | `- “–someflag=abc”` |

### `containerOptions.args.xbstream`

Custom [command line options](https://docs.percona.com/percona-xtrabackup/latest/xbstream-options.html) for the [`xbstream` Percona XtraBackup tool](https://docs.percona.com/percona-xtrabackup/8.0/xbstream-binary-overview.html)

| Value type | Example             |
| ---------- | ------------------- |
| subdoc     | `- “–someflag=abc”` |
