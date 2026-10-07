# Log rotation

!!! note "Version added: [1.3.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.3.0.md)"

`logrotate` limits how large log files grow. Without rotation, the MySQL error log can fill the data volume. Percona XtraBackup log files can fill the Pod's temporary log directory while the Pod is running.

`logrotate` runs in a `logrotate` sidecar on every MySQL Pod when [persistent logging](persistent-logging.md) is enabled. 
By default, `logrotate` handles two sets of files:

* **MySQL logs** under `/var/lib/mysql/log/*.log`, including `mysqld-error.log`. `mysqld` keeps the error log open, so the sidecar uses `copytruncate`: it copies the file and then empties the original in place. The server keeps writing to the same path.
* **Percona XtraBackup logs** under `/var/log/xtrabackup/*.log`. These files are on an `emptyDir` volume. Rotation limits disk use while the Pod is running. Deleting the Pod deletes the files.

For both sets, the default rules are:

* Rotate once a day, or on the next run when a file is larger than 100 MB.
* Keep up to seven rotated files.
* Skip missing or empty files.
* Leave rotated files uncompressed.

## Configure log rotation

Change retention, size limits, or extra paths in one of these ways:

* Override the default configuration in the Custom Resource
* Add rules from a ConfigMap
* Set a custom schedule

When you change any of these, the Operator updates a configuration hash and restarts the MySQL Pods.

### Override the default configuration

Set `spec.logcollector.logRotate.configuration` to replace the Operator-managed `mysql.conf` snippet. 

You must provide the full configuration because this field replaces the built-in rules. Refer to the [default configuration :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/build/logcollector/logrotate/logrotate.conf) for the built-in rules when you define your snippet.

If the snippet is invalid, the sidecar logs an error and falls back to the built-in configuration.

The cron schedule controls when the sidecar runs. The directives in the file, such as `hourly`, are checked only on that run. Set them to the same interval.

An override replaces the whole default file, including the XtraBackup rules. Include a block for `/var/log/xtrabackup/*.log` if you still want those files rotated.

This example runs every hour and keeps three copies of both default log sets:

```yaml
spec:
  logcollector:
    enabled: true
    image: perconalab/fluentbit:{{fluentbitrecommended}}
    logRotate:
      schedule: "0 * * * *"
      configuration: |
        /var/lib/mysql/log/*.log {
            hourly
            rotate 3
            missingok
            nocompress
            notifempty
            copytruncate
            sharedscripts
        }
        /var/log/xtrabackup/*.log {
            hourly
            rotate 3
            missingok
            nocompress
            notifempty
            copytruncate
            sharedscripts
        }
```

Apply the Custom Resource:

```bash
kubectl apply -f deploy/cr.yaml -n <namespace>
```

### Add extra rules from a ConfigMap

Use `spec.logcollector.logRotate.extraConfig.name` to load more `.conf` files from a ConfigMap in the same namespace. Each key must end with `.conf`. Do not use the key `mysql.conf`. That name is reserved for the Operator-managed configuration. `logrotate` loads these files in addition to the main configuration. An invalid extra file is ignored, and the sidecar logs an error.

This example rotates a slow query log that you have pointed at `/var/lib/mysql/log/slow.log`.

1. Create a ConfigMap. For example, `custom-logrotate.yaml`:

    ```yaml title="custom-logrotate.yaml"
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: my-logrotate-extra
      namespace: <namespace>
    data:
      slow.conf: |
        /var/lib/mysql/log/slow.log {
            daily
            rotate 14
            missingok
            nocompress
            notifempty
            copytruncate
            sharedscripts
        }
    ```

2. Create the ConfigMap:

    ```bash
    kubectl apply -f custom-logrotate.yaml -n <namespace>
    ```

3. Reference it in the Custom Resource:

    ```yaml
    spec:
      logcollector:
        enabled: true
        image: perconalab/fluentbit:{{fluentbitrecommended}}
        logRotate:
          extraConfig:
            name: my-logrotate-extra
    ```

4. Apply the Custom Resource:

    ```bash
    kubectl apply -f deploy/cr.yaml -n <namespace>
    ```

### Set a custom schedule

Set `spec.logcollector.logRotate.schedule` to a [cron :octicons-link-external-16:](https://en.wikipedia.org/wiki/Cron) expression of five fields. The default is `0 0 * * *` (once a day at midnight). The Operator rejects a schedule that is not valid cron or that contains a newline.

This example runs log rotation every six hours:

```yaml
spec:
  logcollector:
    enabled: true
    image: perconalab/fluentbit:{{fluentbitrecommended}}
    logRotate:
      schedule: "0 */6 * * *"
```

Apply the Custom Resource:

```bash
kubectl apply -f deploy/cr.yaml -n <namespace>
```

See [`logcollector.logRotate`](operator.md#logcollectorlogrotateconfiguration) for these fields.
