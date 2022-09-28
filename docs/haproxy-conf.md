# Configuring Load Balancing with HAProxy

Percona Operator for MySQL provides load balancing and proxy service with
[HAProxy](https://haproxy.org) (enabled by default).
You can control whether to use it or not by enabling or disabling it via the
`haproxy.enabled` option in the `deploy/cr.yaml` configuration file.

For example, you can use the following command to enable HAProxy for existing
cluster:

```bash
$ kubectl patch ps cluster1 --type=merge --patch '{
  "spec": {
     "haproxy": {
        "enabled": true,
        "size": 3,
        "image": "perconalab/percona-xtradb-cluster-operator:{{ release }}-haproxy" }
  }}'
```

The resulting HAPproxy setup will contain two services:

* `cluster1-haproxy` service listening on ports 3306 (MySQL) and 3309 (the [proxy protocol](https://www.haproxy.com/blog/haproxy/proxy-protocol/)).
    This service is pointing to the MySQL cluster member number zero 
    (`cluster1-mysql-0`) by default when this member is available. If a zero
    member is not available, members are selected in descending order of their
    numbers (e.g. `cluster1-mysql-2`, then `cluster1-mysql-1`, etc.). This
    service can be used for both read and write load, or it can also be used
    just for write load (single writer mode) in setups with split write and read
    loads.

* `cluster1-haproxy-replicas` listening on port 3307 (MySQL).
    This service selects MySQL cluster members to serve queries following
    the Round Robin load balancing algorithm.

When the cluster with HAProxy is upgraded, the following steps
take place. First, reader members are upgraded one by one: the Operator waits
until the upgraded Percona Distribution for MySQL luster member becomes synced,
and then proceeds to upgrade the next member. When the upgrade is finished for
all the readers, then the writer Percona XtraDB Cluster member is finally
upgraded.

## Passing custom configuration options to HAProxy

You can pass custom configuration to HAProxy in one of the following ways:

* edit the `deploy/cr.yaml` file,
* use a ConfigMap,
* use a Secret object.

!!! note

    If you specify a custom HAProxy configuration in this way, the
    Operator doesn’t provide its own HAProxy configuration file. That’s why you
    should specify either a full set of configuration options or nothing.

### Edit the `deploy/cr.yaml` file

You can add options from the [haproxy.cfg](https://www.haproxy.com/blog/the-four-essential-sections-of-an-haproxy-configuration/)
configuration file by editing  `haproxy.configuration` key in the
`deploy/cr.yaml` file. Here is an example:

```yaml
...
haproxy:
    enabled: true
    size: 3
    image: perconalab/percona-xtradb-cluster-operator:{{ release }}-haproxy
    configuration: |
      global
        maxconn 2048
        external-check
        stats socket /var/run/haproxy.sock mode 600 expose-fd listeners level user
      defaults
        log global
        mode tcp
        retries 10
        timeout client 10000
        timeout connect 100500
        timeout server 10000
      frontend galera-in
        bind *:3309 accept-proxy
        bind *:3306
        mode tcp
        option clitcpka
        default_backend galera-nodes
      frontend galera-replica-in
        bind *:3309 accept-proxy
        bind *:3307
        mode tcp
        option clitcpka
        default_backend galera-replica-nodes
```

### Use a ConfigMap

You can use a ConfigMap and the cluster restart to reset configuration
options. A ConfigMap allows Kubernetes to pass or update configuration
data inside a containerized application.

Use the `kubectl` command to create the ConfigMap from external
resources, for more information see [Configure a Pod to use a
ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#create-a-configmap).

For example, you define a `haproxy.cfg` configuration file with the following
setting:

```default
global
  maxconn 2048
  external-check
  stats socket /var/run/haproxy.sock mode 600 expose-fd listeners level user
defaults
  log global
  mode tcp
  retries 10
  timeout client 10000
  timeout connect 100500
  timeout server 10000
frontend galera-in
  bind *:3309 accept-proxy
  bind *:3306
  mode tcp
  option clitcpka
  default_backend galera-nodes
frontend galera-replica-in
  bind *:3309 accept-proxy
  bind *:3307
  mode tcp
  option clitcpka
  default_backend galera-replica-nodes
```

You can create a ConfigMap from the `haproxy.cfg` file with the
`kubectl create configmap` command.

You should use the combination of the cluster name with the `-haproxy`
suffix as the naming convention for the ConfigMap. To find the cluster
name, you can use the following command:

```bash
$ kubectl get ps
```

The syntax for `kubectl create configmap` command is:

```default
kubectl create configmap <cluster-name>-haproxy <resource-type=resource-name>
```

The following example defines `cluster1-haproxy` as the ConfigMap name and
the `haproxy.cfg` file as the data source:

```bash
$ kubectl create configmap cluster1-haproxy --from-file=haproxy.cfg
```

To view the created ConfigMap, use the following command:

```bash
$ kubectl describe configmaps cluster1-haproxy
```

### Use a Secret Object

The Operator can also store configuration options in [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/).
This can be useful if you need additional protection for some sensitive data.

You should create a Secret object with a specific name, composed of your cluster
name and the `haproxy` suffix.

!!! note

    To find the cluster name, you can use the following command:

    ```bash
    $ kubectl get ps
    ```

Configuration options should be put inside a specific key inside of the `data`
section. The name of this key is `haproxy.cfg` for HAProxy Pods.

Actual options should be encoded with [Base64](https://en.wikipedia.org/wiki/Base64).

For example, let’s define a `haproxy.cfg` configuration file and put there
options we used in the previous example:

```default
global
  maxconn 2048
  external-check
  stats socket /var/run/haproxy.sock mode 600 expose-fd listeners level user
defaults
  log global
  mode tcp
  retries 10
  timeout client 10000
  timeout connect 100500
  timeout server 10000
frontend galera-in
  bind *:3309 accept-proxy
  bind *:3306
  mode tcp
  option clitcpka
  default_backend galera-nodes
frontend galera-replica-in
  bind *:3309 accept-proxy
  bind *:3307
  mode tcp
  option clitcpka
  default_backend galera-replica-nodes
```

You can get a Base64 encoded string from your options via the command line as
follows:

```bash
$ cat haproxy.cfg | base64 --wrap=0
```

!!! note

    Similarly, you can read the list of options from a Base64 encoded string:

    ```bash
    $ echo "IGdsb2JhbAogICBtYXhjb25uIDIwNDgKICAgZXh0ZXJuYWwtY2hlY2sKICAgc3RhdHMgc29ja2V0\
      IC92YXIvcnVuL2hhcHJveHkuc29jayBtb2RlIDYwMCBleHBvc2UtZmQgbGlzdGVuZXJzIGxldmVs\
      IHVzZXIKIGRlZmF1bHRzCiAgIGxvZyBnbG9iYWwKICAgbW9kZSB0Y3AKICAgcmV0cmllcyAxMAog\
      ICB0aW1lb3V0IGNsaWVudCAxMDAwMAogICB0aW1lb3V0IGNvbm5lY3QgMTAwNTAwCiAgIHRpbWVv\
      dXQgc2VydmVyIDEwMDAwCiBmcm9udGVuZCBnYWxlcmEtaW4KICAgYmluZCAqOjMzMDkgYWNjZXB0\
      LXByb3h5CiAgIGJpbmQgKjozMzA2CiAgIG1vZGUgdGNwCiAgIG9wdGlvbiBjbGl0Y3BrYQogICBk\
      ZWZhdWx0X2JhY2tlbmQgZ2FsZXJhLW5vZGVzCiBmcm9udGVuZCBnYWxlcmEtcmVwbGljYS1pbgog\
      ICBiaW5kICo6MzMwOSBhY2NlcHQtcHJveHkKICAgYmluZCAqOjMzMDcKICAgbW9kZSB0Y3AKICAg\
      b3B0aW9uIGNsaXRjcGthCiAgIGRlZmF1bHRfYmFja2VuZCBnYWxlcmEtcmVwbGljYS1ub2Rlcwo=" | base64 --decode
    ```

Finally, use a yaml file to create the Secret object. For example, you can
create a `deploy/my-haproxy-secret.yaml` file with the following contents:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cluster1-haproxy
data:
  my.cnf: "IGdsb2JhbAogICBtYXhjb25uIDIwNDgKICAgZXh0ZXJuYWwtY2hlY2sKICAgc3RhdHMgc29ja2V0\
     IC92YXIvcnVuL2hhcHJveHkuc29jayBtb2RlIDYwMCBleHBvc2UtZmQgbGlzdGVuZXJzIGxldmVs\
     IHVzZXIKIGRlZmF1bHRzCiAgIGxvZyBnbG9iYWwKICAgbW9kZSB0Y3AKICAgcmV0cmllcyAxMAog\
     ICB0aW1lb3V0IGNsaWVudCAxMDAwMAogICB0aW1lb3V0IGNvbm5lY3QgMTAwNTAwCiAgIHRpbWVv\
     dXQgc2VydmVyIDEwMDAwCiBmcm9udGVuZCBnYWxlcmEtaW4KICAgYmluZCAqOjMzMDkgYWNjZXB0\
     LXByb3h5CiAgIGJpbmQgKjozMzA2CiAgIG1vZGUgdGNwCiAgIG9wdGlvbiBjbGl0Y3BrYQogICBk\
     ZWZhdWx0X2JhY2tlbmQgZ2FsZXJhLW5vZGVzCiBmcm9udGVuZCBnYWxlcmEtcmVwbGljYS1pbgog\
     ICBiaW5kICo6MzMwOSBhY2NlcHQtcHJveHkKICAgYmluZCAqOjMzMDcKICAgbW9kZSB0Y3AKICAg\
     b3B0aW9uIGNsaXRjcGthCiAgIGRlZmF1bHRfYmFja2VuZCBnYWxlcmEtcmVwbGljYS1ub2Rlcwo="
```

When ready, apply it with the following command:

```bash
$ kubectl create -f deploy/my-haproxy-secret.yaml
```

!!! note

    Do not forget to restart your cluster to ensure it has updated the
    configuration.

## Enabling the Proxy protocol

The Proxy protocol [allows](https://www.percona.com/doc/percona-server/LATEST/flexibility/proxy_protocol_support.html)
HAProxy to provide a real client address to the Percona Distribution for MySQL
Cluster.

Normally Proxy protocol is disabled, and MySQL sees the IP address of the
proxying server (HAProxy) instead of the real client address.
But there are scenarios when making real client IP-address visible for MySQL
is important: e.g. it allows to have privilege grants based on
client/application address, and significantly enhance auditing.

You can enable Proxy protocol on your cluster by adding
[proxy_protocol_networks](https://www.percona.com/doc/percona-server/LATEST/flexibility/proxy_protocol_support.html#proxy_protocol_networks)
option to [mysql.configuration](operator.md#mysql-configuration) key in the
`deploy/cr.yaml` configuration file.

More information about Proxy protocol can be found in the [official HAProxy documentation](https://www.haproxy.com/blog/using-haproxy-with-the-proxy-protocol-to-better-secure-your-database/).
