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

### `sourceHost`

Specifies the MySQL instance to take a backup from. When defined, takes precedence, regardless the cluster type (async or group-replication) and topology. Overrides the `sourceHost` value if defined in the `deploy/cr.yaml`

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `cluster1-mysql-0.<mysql_service_name>.<namespace>` |

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

