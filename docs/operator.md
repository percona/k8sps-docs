# Custom Resource options reference

Percona Operator for MySQL uses [Custom Resources :octicons-link-external-16:](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) to manage options for the various components of the cluster.

* `PerconaServerMySQL` Custom Resource with options for the cluster,
* `PerconaServerMySQLBackup` Custom Resource contains options for Percona XtraBackup used to backup Percona Server for MySQL
* `PerconaServerMySQLRestore` Custom Resource contains options for restoring Percona Server for MySQL from backups.

## PerconaServerMySQL Custom Resource options

Percona Server for MySQL managed by the Operator is configured via the spec section
of the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
file.

The metadata part of PerconaServerMySQL Custom Resource contains the following keys:

* <a name="metadata-name"></a> `name` (`cluster1` by default) sets the name of your Percona Server for
MySQL cluster; it should include only [URL-compatible characters :octicons-link-external-16:](https://datatracker.ietf.org/doc/html/rfc3986#section-2.3),
not exceed 22 characters, start with an alphabetic character, and end with an
alphanumeric character;
* `finalizers` subsection:
    * `percona.com/delete-mysql-pods-in-order` if present, activates the [Finalizer :octicons-link-external-16:](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#finalizers) which controls the proper Pods deletion order in case of the cluster deletion event (on by default).
    * `percona.com/delete-mysql-pvc` if present, activates the [Finalizer :octicons-link-external-16:](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#finalizers) which deletes [Persistent Volume Claims :octicons-link-external-16:](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) for Percona Server for MySQL Pods after the cluster deletion event (off by default).
    * `percona.com/delete-ssl` if present, activates the [Finalizer :octicons-link-external-16:](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#finalizers) which deletes [objects, created for SSL](TLS.md) (Secret, certificate, and issuer) after the cluster deletion event (off by default).

The toplevel spec elements of the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) are the following ones:

### `initImage`

An alternative init image for the Operator.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}` |

### `secretsName`

A name for [users secrets](users.md#users).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `cluster1-secrets` |

### `sslSecretName`

A secret with TLS certificate generated for *external* communications, see [Transport Layer Security (TLS)](TLS.md) for details.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `cluster1-ssl`     |

### `ignoreAnnotations`

The list of annotations [to be ignored](annotations.md#annotations-ignore) by the Operator.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc      | `service.beta.kubernetes.io/aws-load-balancer-backend-protocol` |

### `ignoreLabels`

The list of labels [to be ignored](annotations.md#annotations-ignore) by the Operator.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc      | `rack`             |

### `updateStrategy`

A strategy the Operator uses for [upgrades](update.md).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `SmartUpdate` |

### `pause`

Pause/resume: setting it to `true` gracefully stops the cluster, and setting it to `false` after shut down starts the cluster back.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `false`    |

### `allowUnsafeConfigurations`

Prevents users from configuring a cluster with unsafe parameters such as starting a group replication cluster with less than 3 or more than 9 Percona Server for MySQL instances. **This option is deprecated and will be removed in future releases**. Use `unsafeFlags` subsection instead. Setting `allowUnsafeConfigurations` won’t have any effect with the Operator version 0.8.0 and newer, and upgrading existing clusters with `allowUnsafeConfigurations=true` will cause everything under the [unsafeFlags](#operator-unsafeflags-section) subsection set to `true`. 

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `false`  |

## <a name="operator-unsafeflags-section"></a>Unsafe flags section

The `unsafeFlags` section in the [deploy/cr.yaml  :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains various configuration options to prevent users from configuring a cluster with unsafe parameters. *After switching to unsafe configurations permissive mode you will not be able to switch the cluster back by setting same keys to `false`, the flags will be ignored*.

### `unsafeFlags.mysqlSize`

Allows users to start the cluster with less than 3 MySQL instances or with more than 9 (the maximum safe size).

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     |`false` |

### `unsafeFlags.proxy`

Allows users to configure a cluster with disabled proxy (both HAProxy and Router).

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     |`false` |

### `unsafeFlags.proxySize`

Allows users to set proxy (HAProxy or Router) size to a value less than 2 Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     |`false` |

### `unsafeFlags.orchestrator`

Allows users to configure a cluster with disabled Orchestrator even if asynchronous replication is turned on.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     |`false` |

### `unsafeFlags.orchestratorSize`

Allows users to set [orchestrator.size](#orchestratorsize) option to a value less than the minimum safe size (3).

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     |`false` |

## <a name="operator-issuerconf-section"></a>Extended cert-manager configuration section

The `tls` section in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains various configuration options for additional customization of the [TLS cert-manager](TLS.md#install-and-use-the-cert-manager).

### `tls.SANs`

Additional domains (SAN) to be added to the TLS certificate within the extended cert-manager configuration.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | |

### `tls.issuerConf.name`

A [cert-manager issuer name :octicons-link-external-16:](https://cert-manager.io/docs/concepts/issuer/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `special-selfsigned-issuer` |

### `tls.issuerConf.kind`

A [cert-manager issuer type :octicons-link-external-16:](https://cert-manager.io/docs/configuration/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ClusterIssuer` |

### `tls.issuerConf.group`

A [cert-manager issuer group :octicons-link-external-16:](https://cert-manager.io/docs/configuration/). Should be `cert-manager.io` for built-in cert-manager certificate issuers |

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `cert-manager.io` |

## <a name="operator-upgradeoptions-section"></a>Upgrade options section

The `upgradeOptions` section in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains various configuration options to control Percona Server for MySQL version choice at the deployment time and during upgrades.

### `upgradeOptions.versionServiceEndpoint`

The Version Service URL used to check versions compatibility for upgrade.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `https://check.percona.com` |

### `upgradeOptions.apply`

Specifies how images are picked up from the version service on initial start by the Operator. `Never` or `Disabled` will completely disable quering version service for images, otherwise it can be set to `Latest` or `Recommended` or to a specific version string of Percona Server for MySQL (e.g. `8.0.32-24`) that is wished to be version-locked (so that the user can control the version running) |

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Disabled` |

## <a name="operator-mysql-section"></a>Percona Server for MySQL section

The `mysql` section in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains general
configuration options for the Percona Server for MySQL.

### `mysql.clusterType`

The cluster type: `async` for [Asynchronous replication :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/replication.html), `group-replication` for [Group Replication :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/group-replication.html).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `group-replication` |

### `mysql.autoRecovery`

Enables or disables the Operator from attempting to fix the issue in the event of a full cluster crash .

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `true` |

### `mysql.size`

The number of the Percona Server for MySQL instances. This setting is required.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `mysql.image`

The Docker image of the Percona Server for MySQL used (actual image names for Percona Server for MySQL 8.0 and Percona Server for MySQL 5.7 can be found [in the list of certified images](images.md)).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `percona/percona-server:{{ ps80recommended }}` |

### `mysql.imagePullSecrets.name`

The [Kubernetes ImagePullSecret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/#using-imagepullsecrets).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `private-registry-credentials` |

### `mysql.imagePullPolicy`

The [policy used to update images :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/images/#updating-images).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Always` |


### `mysql.initImage`

An alternative init image for MySQL Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}` |

### `mysql.env.name`

The name of an environment variable for a MySQL container. The `BOOTSTRAP_READ_TIMEOUT` variable controls the timeout for bootstrapping the cluster.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `BOOTSTRAP_READ_TIMEOUT` |

### `mysql.env.value`

The value you set for the environment variables for a MySQL container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | "600" |


### `mysql.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Server for MySQL container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `512M` |

### `mysql.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Server for MySQL container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `1G` |

### `mysql.affinity.antiAffinityTopologyKey`

The Operator [topology key :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) node anti-affinity constraint.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `kubernetes.io/hostname` |

### `mysql.affinity.advanced`

In cases where the Pods require complex tuning the advanced option turns off the `topologyKey` effect. This setting allows the [standard Kubernetes affinity constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#node-affinity) of any complexity to be used.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | |

### `mysql.topologySpreadConstraints.labelSelector.matchLabels`

The Label selector for the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `app.kubernetes.io/name: percona-server` |

### `mysql.topologySpreadConstraints.maxSkew`

The degree to which Pods may be unevenly distributed under the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 1 |

### `mysql.topologySpreadConstraints.topologyKey`

The key of node labels for the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `kubernetes.io/hostname` |

### `mysql.topologySpreadConstraints.whenUnsatisfiable`

What to do with a Pod if it doesn't satisfy the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `DoNotSchedule` |

### `mysql.expose.enabled`

Enable or disable exposing Percona Server for MySQL nodes with dedicated IP addresses.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `false` |

### `mysql.expose.type`

The [Kubernetes Service Type :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) used for exposure.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ClusterIP` |

### `mysql.expose.annotations`

The [Kubernetes annotations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `service.beta.kubernetes.io/aws-load-balancer-backend-protocol: tcp` |

### `mysql.expose.externalTrafficPolicy`

Specifies whether Service should [route external traffic :octicons-link-external-16:](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) to cluster-wide (`Cluster`) or node-local (`Local`) endpoints; it can influence the load balancing effectiveness.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Cluster` |

### `mysql.expose.internalTrafficPolicy`

Specifies whether Service should [route internal traffic :octicons-link-external-16:](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) to cluster-wide (`Cluster`) or node-local (`Local`) endpoints; it can influence the load balancing effectiveness.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Cluster` |

### `mysql.expose.labels`

[Labels are key-value pairs attached to objects :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `rack: rack-22` |

### `mysql.expose.loadBalancerSourceRanges`

The range of client IP addresses from which the load balancer should be reachable (if not set, there are no limitations).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `10.0.0.0/8` |

### `mysql.volumeSpec.persistentVolumeClaim.resources.requests.storage`

The [Kubernetes PersistentVolumeClaim :octicons-link-external-16:](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims) size for the Percona Server for MySQL.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `2Gi` |

### `mysql.configuration`

The `my.cnf` file options to be passed to Percona Server for MySQL instances.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | <pre>&#124;<br>`[mysqld]`<br>`max_connections=250`</pre> |

### `mysql.sidecars.image`

Image for the [custom sidecar container](sidecar.md) for Percona Server for MySQL Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `busybox` |

### `mysql.sidecars.command`

Command for the [custom sidecar container](sidecar.md) for Percona Server for MySQL Pods.

| Value type  | Example    |
| ----------- | ---------- |
|:material-application-array-outline: array     | `["sleep", "30d"]` |

### `mysql.sidecars.name`

Name of the [custom sidecar container](sidecar.md) for Percona Server for MySQL Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-sidecar-1` |

### `mysql.sidecars.volumeMounts.mountPath`

Mount path of the [custom sidecar container](sidecar.md) volume for Replica Set Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `/volume1` |

### `mysql.sidecars.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Server for MySQL sidecar container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `16M` |

### `mysql.sidecars.volumeMounts.name`

Name of the [custom sidecar container](sidecar.md) volume for Replica Set Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `sidecar-volume-claim` |

### `mysql.sidecarVolumes`

[Volume specification :octicons-link-external-16:](https://kubernetes.io/docs/concepts/storage/volumes/) for the [custom sidecar container](sidecar.md) volume for Percona Server for MySQL Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | |

### `mysql.sidecarPVCs`

[Persistent Volume Claim :octicons-link-external-16:](https://v1-20.docs.kubernetes.io/docs/concepts/storage/persistent-volumes/) for the [custom sidecar container](sidecar.md) volume for Replica Set Pods |

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | |

## <a name="operator-haproxy-section"></a>HAProxy subsection

The `proxy.haproxy` subsection in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
file contains configuration options for the HAProxy service.

### `proxy.haproxy.enabled`

Enables or disables [load balancing with HAProxy :octicons-link-external-16:](https://haproxy.org) [Services :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `true` |

### `proxy.haproxy.size`

The number of the HAProxy Pods [to provide load balancing](expose.md#exposing-cluster-with-haproxy). Safe configuration should have 2 or more. This setting is required.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `proxy.haproxy.image`

HAProxy Docker image to use.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `percona/perconalab-xtradb-cluster-operator:{{ release }}-haproxy` |

### `proxy.haproxy.imagePullPolicy`

The [policy used to update images :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/images/#updating-images).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Always` |

### `proxy.haproxy.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for the main HAProxy container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `1G` |

### `proxy.haproxy.resources.requests.cpu`

[Kubernetes CPU requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for the main HAProxy container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `600m` |

### `proxy.haproxy.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for the main HAProxy container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `1G` |

### `proxy.haproxy.resources.limits.cpu`

[Kubernetes CPU limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for the main HAProxy container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `700m` |

### `proxy.haproxy.env.name`

Name of an environment variable for HAProxy.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `HA_CONNECTION_TIMEOUT` |

### `proxy.haproxy.env.value`

Value of an environment variable for HAProxy.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `"1000"` |

### `proxy.haproxy.envFrom.secretRef.name`

Name of a Secret with environment variables for HAProxy.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `haproxy-env-secret` |

### `proxy.haproxy.readinessProbes.timeoutSeconds`

Number of seconds after which the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `proxy.haproxy.readinessProbes.periodSeconds`

How often (in seconds) to perform the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `5` |

### `proxy.haproxy.readinessProbes.successThreshold`

Minimum consecutive successes for the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) to be considered successful after having failed.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `proxy.haproxy.readinessProbes.failureThreshold`

When the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) fails, Kubernetes will try this number of times before marking the Pod Unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `proxy.haproxy.livenessProbes.timeoutSeconds`

Number of seconds after which the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `proxy.haproxy.livenessProbes.periodSeconds`

How often (in seconds) to perform the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `5` |

### `proxy.haproxy.livenessProbes.successThreshold`

Minimum consecutive successes for the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) to be considered successful after having failed.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `proxy.haproxy.readinessProbes.failureThreshold`

When the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) fails, Kubernetes will try this number of times before marking the Pod Unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `proxy.haproxy.configuration`

The [custom HAProxy configuration file](haproxy-conf.md#passing-custom-configuration-options-to-haproxy) contents.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | |

### `proxy.haproxy.antiAffinityTopologyKey`

The Operator [topology key :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) node anti-affinity constraint.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `kubernetes.io/hostname` |

### `proxy.haproxy.affinity.advanced`

If available it makes a [topologyKey :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#inter-pod-affinity-and-anti-affinity-beta-feature) node affinity constraint to be ignored.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | |

### `proxy.haproxy.topologySpreadConstraints.labelSelector.matchLabels`

The Label selector for the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `app.kubernetes.io/name: percona-server` |

### `proxy.haproxy.topologySpreadConstraints.maxSkew`

The degree to which Pods may be unevenly distributed under the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 1 |

### `proxy.haproxy.topologySpreadConstraints.topologyKey`

The key of node labels for the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `kubernetes.io/hostname` |

### `proxy.haproxy.topologySpreadConstraints.whenUnsatisfiable`

What to do with a Pod if it doesn't satisfy the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `DoNotSchedule` |

### `proxy.haproxy.expose.type`

The [Kubernetes Service Type :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) used for HAProxy exposure.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ClusterIP` |

### `proxy.haproxy.expose.annotations`

The [Kubernetes annotations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) for HAProxy.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `service.beta.kubernetes.io/aws-load-balancer-backend-protocol: tcp` |

### `proxy.haproxy.expose.externalTrafficPolicy`

Specifies whether Service for HAProxy should [route external traffic :octicons-link-external-16:](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) to cluster-wide (`Cluster`) or node-local (`Local`) endpoints; it can influence the load balancing effectiveness.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Cluster` |

### `proxy.haproxy.expose.internalTrafficPolicy`

Specifies whether Service for HAProxy should [route internal traffic :octicons-link-external-16:](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) to cluster-wide (`Cluster`) or node-local (`Local`) endpoints; it can influence the load balancing effectiveness.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Cluster` |

### `proxy.haproxy.expose.labels`

[Labels are key-value pairs attached to objects :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) for HAProxy.

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `rack: rack-22` |

### `proxy.haproxy.expose.loadBalancerIP`

The static IP-address for the load balancer. This field is deprecated in Kuberntetes 1.24+ and removed from the Operator starting with version 0.10.0. If you have defined it, refer to the [Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) for recommendations. 

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `127.0.0.1` |

### `proxy.haproxy.expose.loadBalancerSourceRanges`

The range of client IP addresses from which the load balancer should be reachable (if not set, there is no limitations) |

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `10.0.0.0/8` |

## <a name="operator-router-section"></a>Router subsection

The `proxy.router` subsection in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains configuration options for the [MySQL Router :octicons-link-external-16:](https://dev.mysql.com/doc/mysql-router/8.0/en/), which can act as a proxy for Group replication.

### `proxy.router.enabled`

Enables or disables MySQL Router.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `false` |

### `proxy.router.size`

The number of the Router Pods to provide routing to MySQL Servers. This setting is required.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `proxy.router.image`

Router Docker image to use.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}-router` |

### `proxy.router.imagePullPolicy`

The [policy used to update images :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/images/#updating-images).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Always` |

### `proxy.router.initImage`

An alternative init image for MySQL Router Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}` |

### `proxy.router.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for MySQL Router container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `256M` |

### `proxy.router.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for MySQL Router container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `256M` |

### `proxy.router.affinity.antiAffinityTopologyKey`

The Operator [topology key :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) node anti-affinity constraint.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `kubernetes.io/hostname` |

### `proxy.router.affinity.advanced`

In cases where the Pods require complex tuning the advanced option turns off the
`topologyKey` effect. This setting allows the
[standard Kubernetes affinity constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#node-affinity)
of any complexity to be used.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | |


### `proxy.router.topologySpreadConstraints.labelSelector.matchLabels`

The Label selector for the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `app.kubernetes.io/name: percona-server` |

### `proxy.router.topologySpreadConstraints.maxSkew`

The degree to which Pods may be unevenly distributed under the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 1 |

### `proxy.router.topologySpreadConstraints.topologyKey`

The key of node labels for the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `kubernetes.io/hostname` |

### `proxy.router.topologySpreadConstraints.whenUnsatisfiable`

What to do with a Pod if it doesn't satisfy the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `DoNotSchedule` |

### `proxy.router.configuration`

Custom configuration options to be passed to MySQL Router.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | <pre>&#124;<br>`[default]`<br>`logging_folder=/tmp/router/log`<br>`[logger]`<br>`level=DEBUG`</pre> |

### `proxy.router.expose.type`

The [Kubernetes Service Type :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) used for MySQL Router instances exposure.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ClusterIP` |

### `proxy.router.expose.annotations`

The [Kubernetes annotations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) for MySQL Router.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `service.beta.kubernetes.io/aws-load-balancer-backend-protocol: tcp` |

### `proxy.router.expose.externalTrafficPolicy`

Specifies whether Service for MySQL Router should [route external traffic :octicons-link-external-16:](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) to cluster-wide (`Cluster`) or node-local (`Local`) endpoints; it can influence the load balancing effectiveness.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Cluster` |

### `proxy.router.expose.internalTrafficPolicy`

Specifies whether Service for MySQL Router should [route internal traffic :octicons-link-external-16:](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) to cluster-wide (`Cluster`) or node-local (`Local`) endpoints; it can influence the load balancing effectiveness.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Cluster` |

### `proxy.router.expose.labels`

[Labels are key-value pairs attached to objects :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) for MySQL Router.

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `rack: rack-22` |

### `proxy.router.expose.loadBalancerIP`

The static IP-address for the load balancer. This field is deprecated in Kuberntetes 1.24+ and removed from the Operator starting with version 0.10.0. If you have defined it, refer to the [Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) for recommendations.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `127.0.0.1` |

### `proxy.router.expose.loadBalancerSourceRanges`

The range of client IP addresses from which the load balancer should be reachable (if not set, there is no limitations) |

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `10.0.0.0/8` |

## <a name="operator-orchestrator-section"></a>Orchestrator section

The `orchestrator` section in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains
configuration options for the Orchestrator - a replication topology manager, used if asynchronous replication is turned on.

### `orchestrator.enabled`

Enables or disables the Orchestrator.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `true` |

### `orchestrator.size`

The number of the Orchestrator Pods to provide load balancing. This setting is required.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `orchestrator.image`

Orchestrator Docker image to use.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}-orchestrator` |

### `orchestrator.imagePullPolicy`

The [policy used to update images :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/images/#updating-images).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Always` |

### `orchestrator.serviceAccountName`

The [Kubernetes Service Account :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/) for the Orchestrator Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ercona-server-mysql-operator-orchestrator` |

### `orchestrator.initImage`

An alternative init image for Orchestrator Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}` |

### `orchestrator.affinity.antiAffinityTopologyKey`

The Operator [topology key :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) node anti-affinity constraint.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `kubernetes.io/hostname` |

### `orchestrator.affinity.advanced`

In cases where the Pods require complex tuning the advanced option turns off the `topologyKey` effect. This setting allows the [standard Kubernetes affinity constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#node-affinity) of any complexity to be used.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | |

### `orchestrator.topologySpreadConstraints.labelSelector.matchLabels`

The Label selector for the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `app.kubernetes.io/name: percona-server` |

### `orchestrator.topologySpreadConstraints.maxSkew`

The degree to which Pods may be unevenly distributed under the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 1 |

### `orchestrator.topologySpreadConstraints.topologyKey`

The key of node labels for the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `kubernetes.io/hostname` |

### `orchestrator.topologySpreadConstraints.whenUnsatisfiable`

What to do with a Pod if it doesn't satisfy the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `DoNotSchedule` |

### `orchestrator.expose.type`

The [Kubernetes Service Type :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) used for Orchestrator instances exposure.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ClusterIP` |

### `orchestrator.expose.annotations`

The [Kubernetes annotations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) for the Orchestrator.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `service.beta.kubernetes.io/aws-load-balancer-backend-protocol: tcp` |

### `orchestrator.expose.externalTrafficPolicy`

Specifies whether Service for the Orchestrator should [route external traffic :octicons-link-external-16:](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) to cluster-wide (`Cluster`) or node-local (`Local`) endpoints; it can influence the load balancing effectiveness.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Cluster` |

### `orchestrator.expose.internalTrafficPolicy`

Specifies whether Service for the Orchestrator should [route internal traffic :octicons-link-external-16:](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) to cluster-wide (`Cluster`) or node-local (`Local`) endpoints; it can influence the load balancing effectiveness.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Cluster` |

### `orchestrator.expose.labels`

[Labels are key-value pairs attached to objects :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) for the Orchestrator.

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `rack: rack-22` |

### `orchestrator.expose.loadBalancerSourceRanges`

The range of client IP addresses from which the load balancer should be reachable (if not set, there is no limitations).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `10.0.0.0/8` |

### `orchestrator.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an Orchestrator container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `128M` |

### `orchestrator.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an Orchestrator container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `256M` |

### `orchestrator.volumeSpec.persistentVolumeClaim.resources.requests.storage`

The [Kubernetes PersistentVolumeClaim :octicons-link-external-16:](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims) size for the Orchestrator |

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `1Gi` |

## <a name="operator-pmm-section"></a>PMM section

The `pmm` section in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains configuration
options for Percona Monitoring and Management.

### `pmm.enabled`

Enables or disables [monitoring Percona Server for MySQL with PMM](monitoring.md).

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `false` |

### `pmm.image`

PMM client Docker image to use.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `percona/pmm-client:{{ pmm3recommended }}` |

### `pmm.imagePullPolicy`

The [policy used to update images :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/images/#updating-images).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Always` |

### `pmm.mysqlParams`

Enables to pass MySQL parameters to PMM. For example, to change the number of tables (from the default of 1000) beyond which per-table statistics collection is disabled.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `"--disable-tablestats-limit=2000"` |

### `pmm.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a PMM container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `150M` |

### `pmm.resources.requests.cpu`

[Kubernetes CPU requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a PMM container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `300m` |

### `pmm.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a PMM container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `256M` |

### `pmm.resources.limits.cpu`

[Kubernetes CPU limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a PMM container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `400m` |

### `pmm.serverHost`

Address of the PMM Server to collect data from the cluster.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `monitoring-service` |

## <a name="operator-backup-section"></a>Backup section

The `backup` section in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
file contains the following configuration options for the regular Percona XtraDB Cluster backups.

### `backup.enabled`

Enables or disables making backups.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `true` |

### `backup.image`

The Percona XtraBackup Docker image to use for the backup.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `percona/percona-server-mysql-operator:{{ release }}-backup` |

### `backup.imagePullPolicy`

The [policy used to update images :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/images/#updating-images).

| **Value**       | string  |
| **Example**     | `Always` |

### `backup.initImage`

An alternative init image for Percona XtraBackup Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}` |

### `backup.containerSecurityContext`

A custom [Kubernetes Security Context :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) for the `xtrabackup` container to be used instead of the default one.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | `privileged: true` |

### `backup.backoffLimit`

The number of retries to make a backup (by default, 6 retries are made).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `6` |

### `backup.storages.STORAGE-NAME.type`

The cloud storage type used for backups. Only `s3` and `azure` types are supported.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `s3` |

### `backup.storages.STORAGE-NAME.verifyTLS`

Enable or disable verification of the storage server TLS certificate. Disabling it may be useful e.g. to skip TLS verification for private S3-compatible storage with a self-issued certificate.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `true` |

### `backup.storages.STORAGE-NAME.nodeSelector`

[Kubernetes nodeSelector :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#nodeselector).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `disktype: ssd` |

### `backup.storages.STORAGE-NAME.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona XtraBackup container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `1G` |

### `backup.storages.STORAGE-NAME.resources.requests.cpu`

[Kubernetes CPU requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona XtraBackup container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `600m` |

### `backup.storages.STORAGE-NAME.affinity.nodeAffinity`

The Operator [node affinity :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) constraint.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | |

### `backup.storages.STORAGE-NAME.topologySpreadConstraints.labelSelector.matchLabels`

The Label selector for the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `app.kubernetes.io/name: percona-server` |

### `backup.storages.STORAGE-NAME.topologySpreadConstraints.maxSkew`

The degree to which Pods may be unevenly distributed under the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 1 |

### `backup.storages.STORAGE-NAME.topologySpreadConstraints.topologyKey`

The key of node labels for the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `kubernetes.io/hostname` |

### `backup.storages.STORAGE-NAME.topologySpreadConstraints.whenUnsatisfiable`

What to do with a Pod if it doesn't satisfy the [Kubernetes Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `DoNotSchedule` |

### `backup.storages.STORAGE-NAME.tolerations`

[Kubernetes Pod tolerations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | |

### `backup.storages.STORAGE-NAME.schedulerName`

The [Kubernetes Scheduler :octicons-link-external-16:](https://kubernetes.io/docs/tasks/administer-cluster/configure-multiple-schedulers).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `mycustom-scheduler` |

### `backup.storages.STORAGE-NAME.priorityClassName`

The [Kubernetes Pod priority class :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/#priorityclass).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `high-priority` |

### `backup.storages.STORAGE-NAME.containerSecurityContext`

A custom [Kubernetes Security Context for a Container :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) to be used instead of the default one.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | `privileged: true` |

### `backup.storages.STORAGE-NAME.podSecurityContext`

A custom [Kubernetes Security Context for a Pod :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) to be used instead of the default one.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>fsGroup: 1001<br>supplementalGroups: [1001, 1002, 1003]</pre> |

### `backup.storages.STORAGE-NAME.annotations`

The [Kubernetes annotations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `testName: scheduled-backup` |

### `backup.storages.STORAGE-NAME.labels`

[Labels are key-value pairs attached to objects :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `backupWorker: 'True'` |

### `backup.storages.STORAGE-NAME.s3.bucket`

The [Amazon S3 bucket :octicons-link-external-16:](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html) name for backups.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     |  |

### `backup.storages.STORAGE-NAME.s3.region`

The [AWS region :octicons-link-external-16:](https://docs.aws.amazon.com/general/latest/gr/rande.html) to use. Please note **this option is mandatory** for Amazon and all S3-compatible storages.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `us-west-2` |

### `backup.storages.STORAGE-NAME.s3.prefix`

The path (sub-folder) to the backups inside the [bucket :octicons-link-external-16:](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `""` |

### `backup.storages.STORAGE-NAME.s3.credentialsSecret`

The [Kubernetes secret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/) for backups. It should contain `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` keys.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-cluster-name-backup-s3` |

### `backup.storages.STORAGE-NAME.s3.endpointUrl`

The endpoint URL of the S3-compatible storage to be used (not needed for the original Amazon S3 cloud) |

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | |

### `backup.schedule.name`

Name of the scheduled backup.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `sat-night-backup` |

### `backup.schedule.schedule`

Scheduled time of the backup, specified in the [crontab format :octicons-link-external-16:](https://en.wikipedia.org/wiki/Cron).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `0 0 \* \* 6` |

### `backup.schedule.keep`

The amount of most recent backups to store. Older backups are automatically deleted. Set `keep` to zero or completely remove it to disable automatic deletion of backups.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `backup.schedule.storageName`

The name of the storage for the backups configured in the `storages` subsection.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `s3-us-west` |

## <a name="operator-pt-section"></a>Percona Toolkit section

The `toolkit` section in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains configuration
options for [Percona Toolkit :octicons-link-external-16:](https://docs.percona.com/percona-toolkit/).

### `toolkit.image`

Percona Toolkit client Docker image to use.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `percona/pmm-client:{{ pmm3recommended }}` |

### `toolkit.imagePullPolicy`

The [policy used to update images :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/images/#updating-images).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Always` |

### `toolkit.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Toolkit container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `150M` |

### `toolkit.resources.requests.cpu`

[Kubernetes CPU requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Toolkit container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100m` |

### `toolkit.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Toolkit container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `256M` |

### `toolkit.resources.limits.cpu`

[Kubernetes CPU limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Toolkit container |

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `400m` |

## <a name="operator-backupsource-section"></a> PerconaServerMySQLRestore Custom Resource options

[Percona Server for MySQL Restore](backups-restore.md) options are managed by the Operator via the 
`PerconaServerMySQLRestore` [Custom Resource :octicons-link-external-16:](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) and can be configured via the
[deploy/backup/restore.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/restore.yaml)
configuration file. This Custom Resource contains the following options:

| Key              | Value type        | Description                                    | Required |
| ---------------- | ----------------- | ---------------------------------------------- | -------- |
| metadata.name    | string            | The name of the restore                        | true     |
| spec.clusterName | string            | MySQL Cluster name (the name of your running cluster) | true |
| spec.backupName  | string            | The name of the backup which should be restored| false    |
| spec.backupSource| [subdoc](operator.md#operator-restore-backupsource-options-section)| Defines configuration for different restore sources | false |

### <a name="operator-restore-backupsource-options-section"></a>backupSource section

| Key              | Value type        | Description                                    | Required |
| ---------------- | ----------------- | ---------------------------------------------- | -------- |
| destination      | string            | Path to the backup                             | false    |
| storageName      | string            | The storage name from CR `spec.backup.storages`| false    |
| s3               | [subdoc](operator.md#operator-restore-s3-options-section)    | Define configuration for s3 compatible storages | false |
| azure            | [subdoc](operator.md#operator-restore-azure-options-section) | Define configuration for azure blob storage     | false |

### <a name="operator-restore-s3-options-section"></a>backupSource.s3 subsection

| Key              | Value type        | Description                                    | Required |
| ---------------- | ----------------- | ---------------------------------------------- | -------- |
| bucket           | string            | The bucket with a backup                       | true     |
| credentialsSecret| string            | The Secret name for the backup                 | true     |
| endpointUrl      | string            | A valid endpoint URL                           | false    |
| region           | string            | The region corresponding to the S3 bucket      | false    |

### <a name="operator-restore-azure-options-section"></a>backupSource.azure subsection

| Key              | Value type        | Description                                    | Required |
| ---------------- | ----------------- | ---------------------------------------------- | -------- |
| credentialsSecret| string            | The Secret name for the azure blob storage     | true     |
| container        | string            | The container name of the azure blob storage   | true     |
| endpointUrl      | string            | A valid endpoint URL                           | false    |
| storageClass     | string            | The storage class name of the azure storage    | false    |

