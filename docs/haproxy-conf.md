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
        "image": "percona/haproxy:{{ haproxyrecommended }}" }
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

* `cluster1-mysql-proxy` service selects MySQL cluster members to serve queries
    following the Round Robin load balancing algorithm.

When the cluster with HAProxy is upgraded, the following steps
take place. First, reader members are upgraded one by one: the Operator waits
until the upgraded Percona Distribution for MySQL luster member becomes synced,
and then proceeds to upgrade the next member. When the upgrade is finished for
all the readers, then the writer Percona XtraDB Cluster member is finally
upgraded.

## Passing custom configuration options to HAProxy

You can pass custom configuration to HAProxy, adding options from the
[haproxy.cfg](https://www.haproxy.com/blog/the-four-essential-sections-of-an-haproxy-configuration/)
configuration file to the  `haproxy.configuration` Custom Resource option in
the `deploy/cr.yaml` file. Here is an example:

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
        insecure-fork-wanted
        stats socket /var/run/haproxy.sock mode 600 expose-fd listeners level admin
      defaults
        default-server init-addr last,libc,none
        log global
        mode tcp
        retries 10
        timeout client 28800s
        timeout connect 100500
        timeout server 28800s
      frontend mysql-primary-in
        bind *:3309 accept-proxy
        bind *:3306
        mode tcp
        option clitcpka
        default_backend mysql-primary
      frontend mysql-replicas-in
        bind *:3307
        mode tcp
        option clitcpka
        default_backend mysql-replicas
      frontend stats
        bind *:8404
        mode http
        http-request use-service prometheus-exporter if { path /metrics }
```

the actual default configuration file can be found [here](https://github.com/percona/percona-server-mysql-operator/blob/main/build/haproxy-global.cfg).

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
