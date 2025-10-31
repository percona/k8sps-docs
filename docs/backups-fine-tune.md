# Fine-tuning backup and restore operations

When you run Percona Server for MySQL on Kubernetes, the Operator uses [Percona XtraBackup :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/8.0/index.html) to handle all backup and restore tasks. This process involves a few key binaries: `xtrabackup`, `xbcloud`, and `xbstream`. The Operator sets sensible defaults for these tools, ensuring the smooth flow for backups and restores. However, you might want to customize their behavior for specific scenarios, such as performance optimization.

You can configure `xtrabackup`, `xbcloud`, and `xbstream` tools in two main ways:

  - **Globally**, by setting options in the main `deploy/cr.yaml` Custom Resource manifest. These settings apply to all backups and restores within the cluster.
  - **Individually**, by defining options in the specific `PerconaServerMySQLBackup` or `PerconaServerMySQLRestore` manifests for on-demand operations.

The Operator applies backup and restore settings in a defined order: any options set in a `PerconaServerMySQLBackup` or `PerconaServerMySQLRestore` manifest will override those set globally in `deploy/cr.yaml`. For example:

* If an option is present in both the global and individual manifest, the Operator uses the value from the specific backup or restore manifest.
* If you set `xtrabackup` arguments globally in `deploy/cr.yaml` and set `xbcloud` options for a particular `PerconaServerMySQLBackup`, only the `xbcloud` configuration from the `PerconaServerMySQLBackup` manifest is applied for that job.

This hierarchy gives you maximum flexibility: you can define consistent default settings for the entire cluster, but still tailor individual backup or restore operations as needed. This way you can optimize performance, troubleshoot, or customize specific scenarios without affecting the global configuration.

## Configuring through the Custom Resource

To apply settings globally, modify the `containerOptions` subsection within the `backup.storages` section of your `deploy/cr.yaml` file. This is useful for defining a consistent baseline for all backup and restore jobs.

You can set custom command-line arguments and environment variables for the backup binaries.

```yaml
spec:
  backup:
    storages:
      <storage-name>:
        containerOptions:
          args:
            xtrabackup: ["--compress"]
            xbcloud: ["--max-retries=5"]
            xbstream: ["--parallel=4"]
          env:
            - name: MY_CUSTOM_VAR
              value: "some-value"
```

- **`xtrabackup`**: This tool handles the core backup process, interacting directly with the database. You can pass arguments like `--compress` to override the default compression mechanism. Read more about xtrabackup options in [The xtrabackup command-line options reference :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/8.0/xtrabackup-option-reference.html)
- **`xbcloud`**: This binary is used for transferring backup data to and from cloud storage. An example configuration is to define the number of retries after the failure. Read more about available options in [The xbcloud command-line options reference :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/8.0/xbcloud-options.html)
- **`xbstream`**: This binary is for streaming and decompressing backup data during restore. Arguments here, like `--parallel`, can help accelerate the process. Read more about available options in [The xbstream command-line options reference :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/8.0/xbstream-options.html).

The settings you define here are used for both backup and restore jobs, although `xbstream` and `xbcloud` arguments are primarily used during the restore process. 

## Overriding configuration for Specific Jobs

For on-demand backups and restores, you can provide specific `containerOptions` for the `PerconaServerMySQLBackup` or `PerconaServerMySQLRestore` objects in the respective `deploy/backup/backup.yaml` and  `deploy/backup/restore.yaml` custom resources. This is helpful when you need a one-off task with unique settings that you don't want to apply globally.

### Example for an on-demand backup

To apply specific settings for a single backup job, edit the `deploy/backup/backup.yaml` manifest.

```yaml
apiVersion: ps.percona.com/v1alpha1
kind: PerconaServerMySQLBackup
metadata:
  name: my-special-backup
spec:
  clusterName: ps-cluster1
  storageName: s3-us-west
  containerOptions:
    args:
      xtrabackup: ["--binlog-info=off"]
      xbcloud: ["--retries=10"]
    env:
      - name: CUSTOM_BACKUP_ENV
        value: "extra-value"
```

You can see here that only `xtrabackup` and `xbcloud` arguments are specified. The `xbstream` binary is not used for backups and its configuration will be ignored, even if you specify it. 

Note that the settings you specify here are used, overriding any global configuration from the `deploy/cr.yaml` file.

### Example for a Restore

Similarly, for a restore operation, you can define options in the `deploy/backup/restore.yaml` manifest.

```yaml
apiVersion: ps.percona.com/v1alpha1
kind: PerconaServerMySQLRestore
metadata:
  name: my-special-restore
spec:
  clusterName: cluster1
  backupName: backup1
  containerOptions:
    args:
      xtrabackup: ["--apply-log-only"]
      xbcloud: ["--retries=5"]
      xbstream: ["--parallel=8"]
    env:
      - name: CUSTOM_RESTORE_ENV
        value: "restore-value"
```

When this restore job runs, it will use the `xtrabackup`, `xbcloud`, and `xbstream` arguments defined here, ignoring any settings in the main `cr.yaml`.

The Percona Operator for MySQL provides a flexible and powerful way to manage backup and restore operations using `xtrabackup`, `xbcloud`, and `xbstream`. By leveraging the layered configuration system, you can set general policies in `deploy/cr.yaml` while retaining the ability to use specialized options for individual jobs. This ensures your operations remain efficient, reliable, and tailored to your specific needs.

## Implementation specifics

1. The `xbstream` settings apply only to restores.
2. If you pass storage-specific parameters (like `--s3-region`) directly to the `xtrabackup`, `xbcloud`, and `xbstream` binaries, they will be overridden by the configuration in the storage section of the Custom Resource.
3. If you define environment variables for a backup job, they are passed to both the `xtrabackup` and `xbcloud` processes running within the `xtrabackup` sidecar container. You can verify this by inspecting the process environment variables inside the container during a backup.
4. Environment variables for a restore job are set for the `xtrabackup` container in the restore Pod.
5. The `VERIFY_TLS` environment variable currently applies only to restore operations and is ignored for backups. 
6. If the same binary is configured globally and individually for backups or restores, individual settings take precedence. 
 
