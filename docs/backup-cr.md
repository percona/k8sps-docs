# Backup Resource options for Percona Server for MySQL

The `PerconaServerMySQLBackup` Custom Resource is used to define and manage backups for a Percona Server for MySQL cluster. This CR allows you to specify the backup configuration, including the cluster to back up and the storage location.

This document describes all available options that you can use to customize your backups.

## `apiVersion`

Specifies the API version of the Custom Resource.
`ps.percona.com` indicates the group, and `v1alpha1` is the version of the API.

## `kind`

Defines the type of resource being created: `PerconaServerMySQLBackup`.

## `metadata`

The metadata part of the `deploy/backup.yaml` contains metadata about the resource, such as its name and other attributes. It includes the following keys:

* `finalizers` ensure safe deletion of resources in Kubernetes under certain conditions. This subsection includes the following finalizers:
  
    * `percona.com/delete-backup` - deletes the backup resource after the backup data is deleted from storage. 

* `name` - The name of the backup resource used to identify it in your deployment. You also use the backup name for the restore operation.

## `spec`

This subsection includes the configuration of a backup resource.

### `clusterName`

Specifies the name of the Percona Server for MySQL cluster to back up. 

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `cluster1` |

### `storageName`

Specifies the name of the storage where to save a backup. It must match the name you specified in the `spec.backup.storages` subsection of the `deploy/cr.yaml` file.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `s3-us-west` |

## `containerOptions.env`

The [environment variables set as key-value pairs :octicons-link-external-16:](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/) for the backup job.

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
