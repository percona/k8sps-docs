# Configuring Load Balancing with HAProxy

Percona Operator for MySQL provides load balancing and proxy service with
[HAProxy](https://haproxy.org) (enabled by default). HAProxy is the only
solution proxy when asynchronous replication between MySQL instances is enabled,
while group replication can be used either with HAProxy or [MySQL Router](router-conf.md).
You can control whether to use HAProxy or not by enabling or disabling it via
the `haproxy.enabled` option in the `deploy/cr.yaml` configuration file.

!!! note

    When enabling HAProxy, make sure MySQL Router is disabled
    (`proxy.router.enabled` option should be set to `false`).

For example, you can use the following command to enable HAProxy for existing
cluster:

```bash
$ kubectl patch ps cluster1 --type=merge --patch '{
  "spec": {
     "proxy": {
       "haproxy": {
          "enabled": true,
          "size": 3,
          "image": "percona/haproxy:{{ haproxyrecommended }}" }
       "router": {
          "enabled": false }
       }
  }}'
```

The resulting HAPproxy setup will contain the `cluster1-haproxy` service
listening on ports 3306 (MySQL cluster zero member) and 3307 (other members).

This service is pointing to the MySQL cluster member number zero
(`cluster1-mysql-0`) on the default 3306 port when this member is available. If
a zero member is not available, members are selected in descending order of
their numbers (e.g. `cluster1-mysql-2`, then `cluster1-mysql-1`, etc.). It can
be used for both read and write load, or it can also be used just for write load
(single writer mode) in setups with split write and read loads. On 3307 port
this service selects MySQL cluster members to serve queries following the Round
Robin load balancing algorithm. 

When the cluster with HAProxy is upgraded, the following steps
take place. First, reader members are upgraded one by one: the Operator waits
until the upgraded Percona Distribution for MySQL cluster member becomes synced,
and then proceeds to upgrade the next member. When the upgrade is finished for
all the readers, then the writer MySQL cluster member is finally upgraded.

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

