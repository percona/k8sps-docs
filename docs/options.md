# Changing MySQL Options

You may require a configuration change for your application. MySQL
allows the option to configure the database with a configuration file.
You can pass options from the
[my.cnf](https://dev.mysql.com/doc/refman/8.0/en/option-files.html)
configuration file to be included in the MySQL configuration in one of the
following ways:

* edit the `deploy/cr.yaml` file,

* use a ConfigMap,

* use a Secret object.

## Edit the `deploy/cr.yaml` file

You can add options from the
[my.cnf](https://dev.mysql.com/doc/refman/8.0/en/option-files.html)
configuration file by editing the configuration section of the
`deploy/cr.yaml`. Here is an example:

```yaml
spec:
  secretsName: cluster1-secrets
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
ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#create-a-configmap).

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

```default
kubectl create configmap <cluster-name>-mysql <resource-type=resource-name>
```

The following example defines `cluster1-mysql` as the configmap name and the
`my.cnf` file as the data source:

```bash
kubectl create configmap cluster1-mysql --from-file=my.cnf
```

To view the created configmap, use the following command:

```bash
kubectl describe configmaps cluster1-mysql
```

## Use a Secret Object

The Operator can also store configuration options in [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/).
This can be useful if you need additional protection for some sensitive data.

You should create a Secret object with a specific name, composed of your cluster
name and the `mysql` suffix.

!!! note

    To find the cluster name, you can use the following command:

    ```bash
    $ kubectl get ps
    ```

Configuration options should be put inside a specific key inside of the `data`
section. The name of this key is `my.cnf` for Percona Server for MySQL pods.

Actual options should be encoded with [Base64](https://en.wikipedia.org/wiki/Base64).

For example, let’s define a `my.cnf` configuration file and put there a pair
of MySQL options we used in the previous example:

```default
max_connections=250
```

You can get a Base64 encoded string from your options via the command line as
follows:

```bash
$ cat my.cnf | base64
```

!!! note

    Similarly, you can read the list of options from a Base64 encoded
    string:

    ```bash
    $ echo "bWF4X2Nvbm5lY3Rpb25zPTI1MAo" | base64 --decode
    ```

Finally, use a yaml file to create the Secret object. For example, you can
create a `deploy/mysql-secret.yaml` file with the following contents:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cluster1-mysql
data:
  my.cnf: "bWF4X2Nvbm5lY3Rpb25zPTI1MAo"
```

When ready, apply it with the following command:

```bash
$ kubectl create -f deploy/mysql-secret.yaml
```

!!! note

    Do not forget to restart Percona Server for MySQL pods to ensure the
    cluster has updated the configuration. You can do it with the following
    command:

    ```bash
    $ kubectl rollout restart statefulset cluster1-mysql
    ```
