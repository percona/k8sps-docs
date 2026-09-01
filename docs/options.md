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

The Operator applies your configuration to all MySQL Pods as follows:

* **Dynamic variables** — These variables are applied at runtime with the `SET GLOBAL` command. The Operator doesn't restart the MySQL StatefulSet. See [Dynamic configuration](#dynamic-configuration) for details.
* **Static variables** are variables that MySQL cannot change while the server is running. Applying them requires a rolling restart of the MySQL StatefulSet.
* If any variable is **removed**, the Operator applies the changes with a rolling restart of
  the MySQL StatefulSet.

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

You can use a ConfigMap to pass configuration options. A ConfigMap allows
Kubernetes to pass or update configuration data inside a containerized
application.

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

    The Operator applies Secret changes automatically. [Dynamic variables](#dynamic-configuration) take
    effect without a restart. Static variables or variables you remove from
    the Secret trigger a rolling restart. 

## Dynamic configuration

!!! note "Version added: [1.3.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.3.0.md)"

Some MySQL system
are [dynamic :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.4/en/dynamic-system-variables.html) and you can change them at runtime while
the server is running. 

Use dynamic updates when you need to tune a live cluster without a rolling
restart. Typical cases include raising `max_connections` during peak traffic,
adjusting I/O-related settings or enabling query logging to investigate an
incident.

### How the Operator treats dynamic options

When you change the Custom Resource, ConfigMap, or Secret, the Operator
compares the new configuration with the last configuration it applied.

* If the values already match, the Operator does nothing.
* If you add or change a dynamic variable, the Operator runs the `SET GLOBAL` command on
  every ready MySQL Pod. Pods keep running.
* If MySQL rejects the change because the variable is read-only or cannot be
  modified while Group Replication is running, the Operator rolls the MySQL
  StatefulSet so Pods reload the configuration file.
* If you remove a variable, the Operator restarts Pods so MySQL falls back to
  the server default.

The Operator waits until all MySQL Pods are ready before it runs `SET GLOBAL`.
If a variable name is unknown to MySQL, the Operator logs an error and does
not restart Pods. Check the Operator logs and fix the configuration.

The Operator does not watch live `GLOBAL` values on the server. If you connect
to a Pod and define a dynamic variable by running the `SET GLOBAL` command yourself, the Operator leaves that change in
place until you update the declared configuration. A later Pod restart reloads
the configuration file, so a manual change that is not in the Custom Resource,
ConfigMap, or a Secret is lost.

To keep a value you already set with `SET GLOBAL`, add it to the Custom
Resource, ConfigMap or a Secret. The Operator applies `SET GLOBAL` again and
does not restart Pods.

## Auto-tuning MySQL options

Few configuration options for MySQL can be calculated and set by the Operator
automatically based on the available Pod memory resource limits
**if constant values for these options are not specified by the user** (either
in cr.yaml or in ConfigMap).

Options which can be set automatically are the following ones:

* `innodb_buffer_pool_size`

* `max_connections`

If Percona Server for MySQL container resource limits are defined, then limits
values are used to calculate these options. If Percona Server for MySQL
container resource limits are not defined, auto-tuning is not done.

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
