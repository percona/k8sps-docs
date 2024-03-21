       # Configuring Load Balancing with HAProxy

Percona Operator for MySQL provides load balancing and proxy service with
[HAProxy :octicons-link-external-16:](https://haproxy.org) (enabled by default). HAProxy is the only
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
[haproxy.cfg :octicons-link-external-16:](https://www.haproxy.com/blog/the-four-essential-sections-of-an-haproxy-configuration/)
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

the actual default configuration file can be found [here :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/build/haproxy-global.cfg).

## Enabling the Proxy protocol

The Proxy protocol [allows :octicons-link-external-16:](https://docs.percona.com/percona-server/innovation-release/proxy-protocol-support.html)
HAProxy to provide a real client address to Percona Server for MySQL.

Normally Proxy protocol is disabled, and MySQL instances see the IP
address of the proxying server (HAProxy) instead of the real client address.
But there are scenarios when making real client IP-address visible for MySQL
instances is important: e.g. it allows to have privilege grants based on
client/application address, and significantly enhance auditing.

You can enable Proxy protocol on Percona Server for MySQL  by adding
[proxy_protocol_networks :octicons-link-external-16:](https://docs.percona.com/percona-server/innovation-release/proxy-protocol-support.html#proxy_protocol_networks)
option to [mysql.configuration](operator.md#mysql-configuration) key in the
`deploy/cr.yaml` configuration file.

!!! note

    Depending on the load balancer of your cloud provider, you may also
    need setting [haproxy.externaltrafficpolicy](operator.md#haproxy-externaltrafficpolicy) option in `deploy/cr.yaml`.

There are two ways to set proper addresses with `proxy_protocol_networks` with
their pros and cons:

1. List HAProxy Pod IP addresses explicitly

    * it is easier to configure
    * it will require manual reconfiguration if one of the HAProxy Pods gets
        deleted and obtains a new IP

2. Make HAProxy Pods run in a different subnet than MySQL Pods, and use CIDR
    notation of that subnet
    
    * it is harder to configure 
    * the result is resilient against IP changes
    
=== "Listing HAProxy Pod IPs explicitly"

    1. find out HAProxy Pods addresses:
    
       ```{.bash data-prompt="$"}
       $ kubectl get pod -o wide
       ```
       
       ??? example "Expected output"

        ```{.text .no-copy}
        NAME                   READY   STATUS    RESTARTS   AGE   IP           NODE                                       NOMINATED NODE   READINESS GATES
        cluster1-haproxy-0     2/2     Running   0          69m   10.24.1.6    gke-sdf-31268-default-pool-fa50783b-czhs   <none>           <none>
        cluster1-haproxy-1     2/2     Running   0          69m   10.24.2.7    gke-sdf-31268-default-pool-b267c069-59gj   <none>           <none>
        cluster1-haproxy-2     2/2     Running   0          69m   10.24.0.16   gke-sdf-31268-default-pool-e4c7fa4b-d247   <none>           <none>
        cluster1-mysql-0       2/2     Running   0          58m   10.24.1.9    gke-sdf-31268-default-pool-fa50783b-czhs   <none>           <none>
        cluster1-mysql-1       2/2     Running   0          57m   10.24.2.9    gke-sdf-31268-default-pool-b267c069-59gj   <none>           <none>
        cluster1-mysql-2       2/2     Running   0          59m   10.24.0.18   gke-sdf-31268-default-pool-e4c7fa4b-d247   <none>           <none>
        ...

    2. Set proper addresses to `mysql.configuration` key in the `deploy/cr.yaml`
       Custom Resource manifest:
       
       ```yaml
       ...
       mysql:
         configuration: |
           proxy_protocol_networks=10.24.1.6/32,10.24.2.7/32,10.24.0.16/32
         ...
       ```

       Don't forget to apply changes as usual, with the
       `kubectl apply -f deploy/cr.yaml` command.
    
=== "Running HAProxy Pods on a different node"

    You can make HAProxy Pods running in a separate node than MySQL Pods by
    configuring affinity. This way the cluster will be resilient against IP
    changes. It is only necessary to ensure that no MySQL Pods run on the same
    Node as HAProxy.

    !!! note
    
        A safe setup would require at least 6 Kubernetes Nodes.
    
    1. Check Pod CIDRs (pools of IP addresses which can be assigned to Pods)
       for your Nodes. It should look something like this:

       ```{.bash data-prompt="$"}
       $ kubectl get node -l topology.kubernetes.io/zone=europe-west3-a -o jsonpath={.items[].spec.podCIDR} && \
       kubectl get node -l topology.kubernetes.io/zone=europe-west3-b -o jsonpath={.items[].spec.podCIDR} && \
       kubectl get node -l topology.kubernetes.io/zone=europe-west3-c -o jsonpath={.items[].spec.podCIDR}
       ```
       
       ??? example "Expected output"

        ```{.text .no-copy}
        10.24.1.0/24
        10.24.2.0/24
        10.24.0.0/24
        ...

    2. Set proper [affinity constraints](affinity.md) and `mysql.configuration`
       value in the `deploy/cr.yaml` Custom Resource manifest:

       ```yaml
       mysql:
         ...
         affinity:
           advanced:
             nodeAffinity:
               requiredDuringSchedulingIgnoredDuringExecution:
                 nodeSelectorTerms:
                 - matchExpressions:
                   - key: topology.kubernetes.io/zone
                     operator: In
                     values:
                     - europe-west3-a
                     - europe-west3-b
         ...
         configuration: |
           proxy_protocol_networks=10.24.0.0/24
         ...
         proxy:
           ...
           haproxy:
             ...
             affinity:
               advanced:
                 nodeAffinity:
                   requiredDuringSchedulingIgnoredDuringExecution:
                     nodeSelectorTerms:
                     - matchExpressions:
                       - key: topology.kubernetes.io/zone
                  operator: In
                  values:
                  - europe-west3-c
             ...

       Don't forget to apply changes as usual, with the
       `kubectl apply -f deploy/cr.yaml` command.

!!! warning

    If Proxy protocol is enabled for an IP address, MySQL requires PROXY headers
    in each connection from that IP. Therefore `proxy_protocol_networks` should
    be set to HAProxy IPs only. If it is set to a value that includes MySQL Pod
    IPs (or even `proxy_protocol_networks=*`), the cluster will crash. 

More information about Proxy protocol can be found in the [official HAProxy documentation](https://www.haproxy.com/blog/using-haproxy-with-the-proxy-protocol-to-better-secure-your-database/).
