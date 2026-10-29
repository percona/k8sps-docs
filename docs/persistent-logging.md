# Persistent logging

!!! note "Version added: [1.3.0](ReleaseNotes/index.md)"

In a distributed Kubernetes environment, it is often difficult to debug issues because container logs are tied to the lifecycle of individual Pods. If a Pod fails and restarts, its logs in stdout and stderr may be lost, making it hard to identify the root cause.

Percona Operator for MySQL addresses this challenge with **persistent logging**. It keeps the MySQL error log on the data volume of individual Pods so you can still read it after a Pod restarts. A sidecar streams a copy to standard output for `kubectl logs`.

The Operator uses [Fluent Bit :octicons-link-external-16:](https://fluentbit.io/), a lightweight log processor with versatile output plugins and forwarding features, to collect logs. Each MySQL Pod gets two sidecar containers:

* `logs` runs Fluent Bit. It tails the log files and writes each line as JSON to its own standard output.
* `logrotate` rotates those files on a schedule. See [Log rotation](logrotate.md).


## Collect MySQL and backup logs

The collector tails files in two directories.

**MySQL error log.** Fluent Bit tails every `*.log` and `*.err` file in `/var/lib/mysql/log`. The Operator points only the error log at that directory. 

**Percona XtraBackup logs.** During a backup, the `xtrabackup` container writes command output to `/var/log/xtrabackup/<backup-name>.log` and to its own standard error. Fluent Bit tails `*.log` in that directory. The Operator does not rotate these files. They are stored on an `emptyDir` volume and do not survive a restart of the MySQL Pod.


## Availability and requirements

* Persistent logging covers only MySQL Pods. Percona BinaryLog Server, HAProxy, MySQL Router, and Orchestrator still write only to the container's standard output. Those logs are gone when the Pod is deleted.
* Persistent logging requires the `crVersion` set to 1.3.0 or later
* The names `logs` and `logrotate` are reserved. Do not use them for a [custom sidecar](sidecar.md) while the collector is enabled. The Operator rejects the Custom Resource if you do.

## Enable persistent logging

Persistent logging is enabled by default. Set `logcollector.enabled` in the `deploy/cr.yaml` Custom Resource to `true` or `false` to turn it on or off: 

```yaml
spec:
  crVersion: {{release}}
  ....
  logcollector:
    enabled: true
    image: perconalab/fluentbit:{{fluentbitrecommended}}
```

Apply the Custom Resource:

```bash
kubectl apply -f deploy/cr.yaml -n <namespace>
```

## View the logs

List the JSON lines Fluent Bit emits:

```bash
kubectl logs <cluster-name>-mysql-0 -c logs
```

Read the error log file on the data volume:

```bash
kubectl exec <cluster-name>-mysql-0 -c mysql -- cat /var/lib/mysql/log/mysqld-error.log
```

While a backup is running, the XtraBackup log file is on the same Pod:

```bash
kubectl exec <cluster-name>-mysql-0 -c xtrabackup -- ls /var/log/xtrabackup
```

## Customize Fluent Bit

Add additional rules, such as filters or outputs in `logcollector.configuration`. You cannot override the default configuration. Use the [Fluent Bit YAML configuration format :octicons-link-external-16:](https://docs.fluentbit.io/manual/administration/configuring-fluent-bit/yaml/). The classic `.conf` format is not supported. The Operator includes your rules alongside the built-in pipeline.

The built-in pipeline already turns on the Fluent Bit HTTP server on port `2020`. A `tcpSocket` or `httpGet` probe on that port works without extra configuration.

Invalid snippets are ignored when the `logs` container starts. Check that container's output if a filter or output does not appear.

This example adds a field to every record:

```yaml
spec:
  logcollector:
    enabled: true
    image: perconalab/fluentbit:{{fluentbitrecommended}}
    configuration: |
      pipeline:
        filters:
          - name: record_modifier
            match: "*"
            record:
              - cluster_name cluster1
```

You can add Fluent Bit outputs, such as S3, in the same `pipeline.outputs` list. Use `logcollector.envFrom` for credentials and `logcollector.volumeMounts` with `logcollector.volumes` for files such as a CA bundle. See [`logcollector`](operator.md#operator-logcollector-section) for the available fields.

When you change `logcollector.configuration`, log rotation settings, or the extra logrotate ConfigMap, the Operator updates a configuration hash on the MySQL StatefulSet and restarts the MySQL Pods.
