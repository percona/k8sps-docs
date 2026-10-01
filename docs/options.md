# Changing MySQL Options

You may require a configuration change for your application. MySQL
allows the option to configure the database with a configuration file.
You can pass options from the
[my.cnf :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/option-files.html)
configuration file to be included in the MySQL configuration in one of the
following ways:

* edit the `deploy/cr.yaml` file,

* use a ConfigMap,

* use a Secret object.

Before choosing an approach, note that these aren't independent settings you can freely combine. **Setting any configuration of your own disables the Operator's [automatic configuration tuning](autoconfig.md)**, even if you only set one unrelated option:

| Approach | What controls the configuration | Automatic configuration tuning |
| --- | --- | --- |
| Nothing set | The Operator's basic auto-tuning (`innodb_buffer_pool_size` and `max_connections` only) | N/A — this is the default fallback either way |
| `spec.mysql.autoConfig.enabled: true`, no manual config | The Operator calculates a full configuration from your resources and workload profile | Active |
| `spec.mysql.configuration`, a ConfigMap, or a Secret (any of the methods below) | Your values | Disabled — falls back to basic auto-tuning |

If you want the Operator to fully tune MySQL for you, see [Automatic configuration tuning](autoconfig.md) instead of the manual methods on this page.

## Edit the `deploy/cr.yaml` file

You can add options from the
[my.cnf :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/option-files.html)
configuration file by editing the configuration section of the
`deploy/cr.yaml`. Here is an example:

```yaml
spec:
  secretsName: ps-cluster1-secrets
  mysql:
    ...
      configuration: |
        max_connections=250
```

See the [Custom Resource options, MySQL section](operator.md#operator-mysql-section)
for more details.

## Use a ConfigMap

You can use a configmap and the cluster restart to reset configuration
options. A configmap allows Kubernetes to pass or update configuration
data inside a containerized application.

Use the `kubectl` command to create the configmap from external
resources, for more information see [Configure a Pod to use a
ConfigMap :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#create-a-configmap).

For example, let’s suppose that your application requires more
connections. To increase your `max_connections` setting in MySQL, you
define a `my.cnf` configuration file with the following setting:

```default
max_connections=250
```

You can create a configmap from the `my.cnf` file with the
`kubectl create configmap` command.

You should use the combination of the cluster name with the `-mysql`
suffix as the naming convention for the configmap. To find the cluster
name, you can use the following command:

```bash
kubectl get ps
```

The syntax for `kubectl create configmap` command is:

```bash
kubectl create configmap <cluster-name>-mysql <resource-type=resource-name>
```

The following example defines `ps-cluster1-mysql` as the configmap name and the
`my.cnf` file as the data source:

```bash
kubectl create configmap ps-cluster1-mysql --from-file=my.cnf
```

To view the created configmap, use the following command:

```bash
kubectl describe configmaps ps-cluster1-mysql
```

## Use a Secret Object

The Operator can also store configuration options in [Kubernetes Secrets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/).
This can be useful if you need additional protection for some sensitive data.

You should create a Secret object with a specific name, composed of your cluster
name and the `mysql` suffix.

!!! note

    To find the cluster name, you can use the following command:

    ```bash
    kubectl get ps
    ```

Configuration options should be put inside a specific key inside of the `data`
section. The name of this key is `my.cnf` for Percona Server for MySQL pods.

Actual options should be encoded with [Base64 :octicons-link-external-16:](https://en.wikipedia.org/wiki/Base64).

For example, let’s define a `my.cnf` configuration file and put there a pair
of MySQL options we used in the previous example:

```
max_connections=250
```

You can get a Base64 encoded string from your options via the command line as
follows:

=== "in Linux"

    ```bash
    cat my.cnf | base64 --wrap=0
    ```

=== "in macOS"

    ```bash
    cat my.cnf | base64
    ```

!!! note

    Similarly, you can read the list of options from a Base64 encoded
    string:

    ```bash
    echo "bWF4X2Nvbm5lY3Rpb25zPTI1MAo" | base64 --decode
    ```

Finally, use a yaml file to create the Secret object. For example, you can
create a `deploy/mysql-secret.yaml` file with the following contents:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ps-cluster1-mysql
data:
  my.cnf: "bWF4X2Nvbm5lY3Rpb25zPTI1MAo"
```

When ready, apply it with the following command:

```bash
kubectl create -f deploy/mysql-secret.yaml
```

!!! note

    Do not forget to restart Percona Server for MySQL pods to ensure the
    cluster has updated the configuration. You can do it with the following
    command:

    ```bash
    kubectl rollout restart statefulset ps-cluster1-mysql
    ```

## Auto-tuning MySQL options

The Operator
calculates a few MySQL options automatically based on the memory available to
the MySQL container:

* `innodb_buffer_pool_size` — about 50% of the container memory,
* `innodb_buffer_pool_chunk_size` — set together with `innodb_buffer_pool_size`,
  so the buffer pool size is a valid multiple of the chunk size,
* `max_connections` — one connection per ~12 MiB of container memory.

The Operator uses the memory limit from `mysql.resources.limits`. If no limit
is set, it uses the memory request from `mysql.resources.requests`. If neither
is set, auto-tuning is not done.

The Operator doesn't auto-tune an option you set yourself in
`spec.mysql.configuration`. If you set an option in your own ConfigMap or
Secret, your value takes precedence over the auto-tuned one.

Also, starting from the Operator 0.4.0, there is another way of auto-tuning.
You can use `"{{containerMemoryLimit}}"` as a value in `spec.mysql.configuration`
as follows:

```yaml
mysql:
    configuration: |
    [mysqld]
    innodb_buffer_pool_size={{'{{'}}containerMemoryLimit * 3 / 4{{'}}'}}
    ...
```

Starting with Operator 1.3.0, a more comprehensive form of automatic tuning is
available. See [Automatic configuration tuning](autoconfig.md). 

The tuning of the buffer pool and `max_connections` is what the Operator continues to use
whenever that feature is disabled (`spec.mysql.autoConfig.enabled: false` or
unset). This behavior remains and applies to any cluster that
doesn't opt in.
