# Connection secrets

The Operator automatically creates and maintains a Kubernetes Secret for the `root` user that contains all connection details your applications need. This gives developers and administrators a single, reliable source of connection information without manual configuration.

The Secret is owned by the Operator and updated on every reconciliation, so values such as the primary hostname stay current after failover or configuration changes.

## Secret naming

The connection Secret follows this naming pattern:

```
<cluster_name>-psuser-<username>
```

`<cluster_name>` is the [name of your Percona Server for MySQL cluster](operator.md#metadata-name). `<username>` is the MySQL user name. Currently, the Operator creates this Secret only for the `root` user.

For a cluster named `ps-cluster1`, the Secret name is `ps-cluster1-psuser-root`.

## Secret structure

The following example shows the fields the Operator populates in the connection Secret:

```yaml
stringData:
  host: cluster1-mysql-primary.default.svc
  port: "3306"
  user: root
  password: "w3_3ijSd)wulc.b};xwvT?Rj"
  uri: "mysql://root:w3_3ijSd%29wulc.b%7D%3BxwvT%3FRj@cluster1-mysql-primary.default.svc:3306"
  proxy-host: cluster1-haproxy.default.svc
  proxy-port: "3306"
  proxy-uri: "mysql://root:w3_3ijSd%29wulc.b%7D%3BxwvT%3FRj@cluster1-haproxy.default.svc:3306"
  proxy-readonly-host: cluster1-haproxy.default.svc
  proxy-readonly-port: "3307"
  proxy-readonly-uri: "mysql://root:w3_3ijSd%29wulc.b%7D%3BxwvT%3FRj@cluster1-haproxy.default.svc:3307"
  proxy-external-host: 34.118.45.21
  proxy-external-port: "3306"
  proxy-external-uri: "mysql://root:w3_3ijSd%29wulc.b%7D%3BxwvT%3FRj@34.118.45.21:3306"
```

The table below describes each field and when it is present.

| Field | Present | Description |
| ----- | ------- | ----------- |
| `host` | Always | Hostname of the direct MySQL primary Service. Updated to point to the current primary after failover. |
| `port` | Always | Port the primary MySQL instance listens on (typically `3306`). |
| `user` | Always | MySQL user name. |
| `password` | Always | Password for the user. |
| `uri` | Always | Ready-to-use connection URI for the primary MySQL instance. Special characters in the password are URL-encoded. |
| `proxy-host` | When a proxy is enabled | Hostname of the proxy Service for read/write connections. The same field is used with HAProxy or MySQL Router. |
| `proxy-port` | When a proxy is enabled | Port for read/write connections through the HAProxy or MySQL Router, depending on which proxy is enabled. Port `3306` is typically for HAProxy while `6446` is for MySQL Router. |
| `proxy-uri` | When a proxy is enabled | Ready-to-use connection URI for read/write connections through the proxy. The same field is used with HAProxy or MySQL Router. |
| `proxy-readonly-host` | When a proxy is enabled | Hostname of the proxy Service for read-only connections. The same field is used with HAProxy or MySQL Router.|
| `proxy-readonly-port` | When a proxy is enabled | Port for read-only connections through the proxy (typically `3307` for HAProxy or `6447` for MySQL Router). |
| `proxy-readonly-uri` | When a proxy is enabled | Ready-to-use connection URI for read-only connections through the proxy. The same field is used with HAProxy or MySQL Router.|
| `proxy-external-host` | When the proxy Service type is LoadBalancer and an external IP is assigned | External hostname or IP for read/write connections from outside the cluster. The same field is used with HAProxy or MySQL Router.|
| `proxy-external-port` | When the proxy Service type is LoadBalancer and an external IP is assigned | External port for read/write connections. |
| `proxy-external-uri` | When the proxy Service type is LoadBalancer and an external IP is assigned | Ready-to-use external connection URI for read/write connections. |

The `proxy-*` and `proxy-readonly-*` fields are generic. They do not indicate whether HAProxy or MySQL Router is configured underneath.

!!! note

    Passwords for system users used by the Operator itself (backup, monitoring, replication, and so on) remain in the separate Secrets object configured with `spec.secretsName` (for example, `ps-cluster1-secrets`). See [System users](users.md#system-users) for details.

## View connection details

To inspect the connection Secret, list Secrets in your namespace and look for the `<cluster_name>-psuser-root` object:

```bash
kubectl get secrets -n <namespace>
kubectl get secret ps-cluster1-psuser-root -n <namespace> -o yaml
```

To decode individual fields:

```bash
kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath="{.data['proxy-uri']}" | base64 --decode && echo
```

For keys that contain hyphens (such as `proxy-host` or `proxy-readonly-port`), use bracket notation in the jsonpath expression, as shown above.

## Connect to MySQL

Choose the connection fields based on how your application reaches the database.

### Read/write through the proxy (default)

Most clusters run with [HAProxy](haproxy-conf.md) or [MySQL Router](router-conf.md) enabled. For connections from inside the Kubernetes cluster, use the `proxy-*` fields or `proxy-uri`:

```bash
mysql -h $(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath="{.data['proxy-host']}" | base64 --decode) \
  -u$(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath='{.data.user}' | base64 --decode) \
  -p"$(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath='{.data.password}' | base64 --decode)" \
  -P $(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath="{.data['proxy-port']}" | base64 --decode)
```

Or parse the ready-made URI:

```bash
kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath="{.data['proxy-uri']}" | base64 --decode && echo
```

### Read-only through the proxy

Use the `proxy-readonly-*` fields to send read queries to replica nodes. With HAProxy, read-only traffic is routed on port `3307`. See [Configure HAProxy](haproxy-conf.md) for details.

```bash
mysql -h $(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath="{.data['proxy-readonly-host']}" | base64 --decode) \
  -u$(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath='{.data.user}' | base64 --decode) \
  -p"$(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath='{.data.password}' | base64 --decode)" \
  -P $(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath="{.data['proxy-readonly-port']}" | base64 --decode)
```

!!! warning

    Setting only `proxy-readonly-host` without `proxy-readonly-port` does **not** route your session to read-only nodes. If you omit the port, the client falls back to the default MySQL port (`3306`), which connects to the primary in read/write mode. Always set both `proxy-readonly-host` and `proxy-readonly-port` (or use `proxy-readonly-uri`) for read-only connections.

### Direct connection to the primary

To bypass the proxy and connect directly to the current primary Pod, use the `host`, `port`, `user`, and `password` fields, or the `uri` field:

```bash
mysql -h $(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath='{.data.host}' | base64 --decode) \
  -u$(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath='{.data.user}' | base64 --decode) \
  -p"$(kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath='{.data.password}' | base64 --decode)"
```

The `host` value always points to the direct MySQL primary Service and is updated automatically when failover changes the primary.

### External connections

If you have [exposed the proxy with a LoadBalancer Service](expose.md) and an external IP is assigned, use the `proxy-external-*` fields:

```bash
kubectl get secret ps-cluster1-psuser-root -n <namespace> \
  -o jsonpath="{.data['proxy-external-uri']}" | base64 --decode && echo
```

These fields appear only after the LoadBalancer receives an external IP address.

## Use in application Pods

Mount the connection Secret into your application Pod to inject connection details as environment variables. To avoid naming conflicts, add a `prefix`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: app
    image: my-app:latest
    envFrom:
    - prefix: MYSQL_
      secretRef:
        name: ps-cluster1-psuser-root
```

All Secret keys are exposed as environment variables with the same names and your prefix. For example, `MYSQL_host`, `MYSQL_proxy-host`, `MYSQL_proxy-readonly-port` and so on. Your application can read them directly:

```python
import os
import pymysql

connection = pymysql.connect(
    host=os.environ["MYSQL_proxy-host"],
    user=os.environ["MYSQL_user"],
    password=os.environ["MYSQL_password"],
    port=int(os.environ["MYSQL_proxy-port"]),
)
```

### Read-only connections in application code

When connecting to read-only nodes, pass both the read-only host and port:

```python
connection = pymysql.connect(
    host=os.environ["MYSQL_proxy-readonly-host"],
    user=os.environ["MYSQL_user"],
    password=os.environ["MYSQL_password"],
    port=int(os.environ["MYSQL_proxy-readonly-port"]),
)
```

Using only `proxy-readonly-host` without `proxy-readonly-port` connects on the default port and targets the primary. Write operations on that connection succeed; read-only routing requires the read-only port.

Alternatively, use the ready-made `proxy-readonly-uri` field and pass it to a client that accepts connection URIs.
