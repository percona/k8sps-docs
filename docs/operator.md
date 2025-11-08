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

* <a name="metadata-name"></a> `name` (`ps-cluster1` by default) sets the name of your Percona Server for
MySQL cluster; it should include only [URL-compatible characters :octicons-link-external-16:](https://datatracker.ietf.org/doc/html/rfc3986#section-2.3),
not exceed 22 characters, start with an alphabetic character, and end with an
alphanumeric character;

* `finalizers` subsection:

    * `percona.com/delete-mysql-pods-in-order` if present, activates the [Finalizer :octicons-link-external-16:](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#finalizers) which controls the proper Pods deletion order in case of the cluster deletion event (on by default).
    * `percona.com/delete-mysql-pvc` if present, activates the [Finalizer :octicons-link-external-16:](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#finalizers) which deletes [Persistent Volume Claims :octicons-link-external-16:](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) for Percona Server for MySQL Pods after the cluster deletion event (off by default). It also triggers deletion of user Secrets.
    * `percona.com/delete-ssl` if present, activates the [Finalizer :octicons-link-external-16:](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#finalizers) which deletes [objects, created for SSL](TLS.md) (Secret, certificate, and issuer) after the cluster deletion event (off by default).


The top-level spec elements of the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) are the following ones:

## Toplevel `spec` elements

The spec part of the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-postgresql-operator/blob/main/deploy/cr.yaml) file contains the following:

### `crVersion`

Version of the Operator the Custom Resource belongs to.

| Value type | Example |
| ---------- | ------- |
| :material-code-string: string | `{{ release }}` |

### `metadata.annotations`

The [Kubernetes annotations  :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) metadata that you can set at a global level for all resources created by the Operator.

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label    | `example-annotation: value` |

### `metadata.labels`

The [Kubernetes labels  :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) metadata that you can set at a global level for all resources created by the Operator.

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label       | `example-label: value` |

### `pause`

Pause/resume: setting it to `true` gracefully stops the cluster, and setting it to `false` after shut down starts the cluster back.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `false` |

### `enableVolumeExpansion`

Enables or disables [automatic storage scaling / volume expansion](scaling.md#storage-resizing-with-volume-expansion-capability).

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `false`  |

### `initContainer.Image`

An alternative init image for the Operator.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}` |

### `initContainer.containerSecurityContext`

A custom [Kubernetes Security Context for a Container :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) used for the initial Operator installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>privileged: false<br>runAsUser: 1001<br>runAsGroup: 1001</pre> |

### `initContainer.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for the initial Operator installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100M` |

### `initContainer.resources.requests.cpu`

[Kubernetes CPU requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for the initial Operator installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100m` |

### `initContainer.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for the initial Operator installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `200M` |

### `initContainer.resources.limits.cpu`

[Kubernetes CPU limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for the initial Operator installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `200m` |

### `secretsName`

A name for [users secrets](users.md#users). When undefined, the Operator creates the Secrets object named in the format `<cluster-name>-secrets`. Otherwise, it uses the provided name.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ps-cluster1-secrets` |

### `sslSecretName`

A secret with TLS certificate generated for *external* communications, see [Transport Layer Security (TLS)](TLS.md) for details. When undefined, the Operator creates the Secrets object named in the format `<cluster-name>-secrets-ssl`. Otherwise, it uses the provided name.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ps-cluster1-ssl`     |

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

## <a name="operator-upgrade-options-section"></a>Upgrade options section

The `upgradeOptions` section in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains various configuration options to control Percona Server for MySQL version choice at the deployment time and during upgrades.

### `upgradeOptions.versionServiceEndpoint`

The Version Service URL used to check versions compatibility for upgrade.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `https://check.percona.com` |

### `upgradeOptions.apply`

Specifies how images are picked up from the version service on initial start by the Operator. `Never` or `Disabled` will completely disable querying version service for images, otherwise it can be set to `Latest` or `Recommended` or to a specific version string of Percona Server for MySQL (e.g. `8.0.32-24`) that is wished to be version-locked (so that the user can control the version running) |

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

### `mysql.vaultSecretName`

Specifies the secret for the [HashiCorp Vault :octicons-link-external-16:](https://developer.hashicorp.com/vault) to carry on [Data at Rest Encryption](encryption.md).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ps-cluster1-vault`     |


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


### `mysql.imagePullPolicy`

The [policy used to update images :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/images/#updating-images).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Always` |

### `mysql.runtimeClassName`

Specifies the name of the [RuntimeClass :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/runtime-class/) resource used to define and select the container runtime configuration.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `image-rc` |

### `mysql.schedulerName`

The name of a [Kubernetes scheduler :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/) used to assign MySQL Pods to Kubernetes nodes. The `default-scheduler` means `kube-scheduler` is used. You can define your custom schedulers here.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `default-scheduler` |

### `mysql.priorityClassName`

The name of the Kubernetes [PriorityClass :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/#priorityclass), which is a way to assign priority levels to pods, helping the scheduler decide which pods to schedule first and which ones to evict last when resources are tight.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `high-priority` |

### `mysql.nodeSelector`

[Kubernetes nodeSelector :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#nodeselector).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `disktype: ssd` |

### `mysql.serviceAccountName`

The [Kubernetes Service Account :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/) for the MySQL Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `percona-server-mysql-operator-orchestrator` |


### `mysql.tolerations`

Specifies the [Kubernetes tolerations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) applied to MySQL Pods allowing them to be scheduled on nodes with matching taints. Tolerations enable the Pod to tolerate specific node conditions, such as temporary unreachability or resource constraints, without being evicted immediately.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | `node.alpha.kubernetes.io/unreachable` |

### `mysql.imagePullSecrets.name`

Specifies the Kubernetes [imagePullSecrets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/#using-imagepullsecrets) for the MySQL image.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-secret-1` | 

### `mysql.initContainer.image`

An alternative init image for Percona Server for MySQL.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}` |

### `mysql.initContainer.containerSecurityContext`

A custom [Kubernetes Security Context for a Container :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) used for the MySQL installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>privileged: false<br>runAsUser: 1001<br>runAsGroup: 1001</pre> |

### `mysql.initContainer.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for the MySQL installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100M` |

### `mysql.initContainer.resources.requests.cpu`

[Kubernetes CPU requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for the MySQL installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100m` |

### `mysql.initContainer.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for the MySQL installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `200M` |

### `mysql.initContainer.resources.limits.cpu`

[Kubernetes CPU limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for the MySQL installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `200m` |


### `mysql.podDisruptionBudget.maxUnavailable`

The number of unavailable Pods your cluster can tolerate during voluntary disruption. It can be either an absolute value or a percentage. 

To learn more, see [podDisruptionBudgets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 1 |

### `mysql.podDisruptionBudget.minAvailable`

The number of Pods that must remain available during voluntary disruption. It can be either an absolute value or a percentage. 

To learn more, see [podDisruptionBudgets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 0 |

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

### `mysql.startupProbe.initialDelaySeconds`

The number of seconds to wait before performing the [startup probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `15` |

### `mysql.startupProbe.timeoutSeconds`

The number of seconds after which the [startup probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `43200` |

### `mysql.startupProbe.periodSeconds`

How often to perform the [startup probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/). Measured in seconds.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `10` |

### `mysql.startupProbe.successThreshold`

The number of successful probes required to mark the container successful.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `mysql.startupProbe.failureThreshold`

The number of failed probes required to mark the container unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `mysql.readinessProbe.initialDelaySeconds`

The number of seconds to wait before performing the first [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `30` |

### `mysql.readinessProbe.timeoutSeconds`

The number of seconds after which the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `10` |

### `mysql.readinessProbe.periodSeconds`

How often to perform the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/). Measured in seconds.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `10` |

### `mysql.readinessProbe.successThreshold`

The number of successful probes required to mark the container successful.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `mysql.readinessProbe.failureThreshold`

The number of failed probes required to mark the container unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `mysql.livenessProbe.initialDelaySeconds`

The number of seconds to wait before performing the first [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `15` |

### `mysql.livenessProbe.timeoutSeconds`

The number of seconds after which the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `10` |

### `mysql.livenessProbe.periodSeconds`

How often to perform the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/). Measured in seconds.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `10` |

### `mysql.livenessProbe.successThreshold`

The number of successful probes required to mark the container successful.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `mysql.livenessProbe.failureThreshold`

The number of failed probes required to mark the container unhealthy.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `mysql.env.name`

Name of an environment variable for MySQL Pods. The `BOOTSTRAP_READ_TIMEOUT` variable controls the timeout for bootstrapping the cluster.

Read more about defining environment variables in [Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `BOOTSTRAP_READ_TIMEOUT` |

### `mysql.env.value`

The value you set for the environment variables for a MySQL container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `"600"` |

### `mysql.envFrom.secretRef.name`

Name of a Secret or a ConfigMap, key/values of which are used as environment variables for MySQL Pods. 

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-env-secret` |

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

### `mysql.exposePrimary.enabled`

Enable or disable exposing Percona Server for MySQL primary node with dedicated IP addresses.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `false` |

### `mysql.exposePrimary.type`

The [Kubernetes Service Type :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) used for exposure.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ClusterIP` |


### `mysql.exposePrimary.annotations`

The [Kubernetes annotations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `service.beta.kubernetes.io/aws-load-balancer-backend-protocol: tcp`, `service.beta.kubernetes.io/aws-load-balancer-type: nlb` |

### `mysql.exposePrimary.externalTrafficPolicy`

Specifies whether Service should [route external traffic :octicons-link-external-16:](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) to cluster-wide (`Cluster`) or node-local (`Local`) endpoints; it can influence the load balancing effectiveness.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Cluster` |

### `mysql.exposePrimary.internalTrafficPolicy`

Specifies whether Service should [route internal traffic :octicons-link-external-16:](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) to cluster-wide (`Cluster`) or node-local (`Local`) endpoints; it can influence the load balancing effectiveness.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Cluster` |

### `mysql.exposePrimary.labels`

[Labels are key-value pairs attached to objects :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `rack: rack-22` |

### `mysql.exposePrimary.loadBalancerSourceRanges`

The range of client IP addresses from which the load balancer should be reachable (if not set, there are no limitations).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `10.0.0.0/8` |


### `mysql.expose.enabled`

Enable or disable exposing Percona Server for MySQL nodes with dedicated IP addresses. This setting exposes every Pod in your cluster.

| Value type  | Example    |
| ----------- | ---------- |
| :material-toggle-switch-outline: boolean     | `true` |

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

### `mysql.volumeSpec.emptyDir`

Starts a Pod with an empty temporary directory on the Kubernetes node. This directory exists as long as the Pod runs. Data is deleted when the Pod is deleted or moved to another node.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `{}` |

### `mysql.volumeSpec.hostPath.path`

Specifies a path on the host node's filesystem that will be mounted into your Pod when the Pod starts. Enables Pods to share files or access the host resources. Data persists as long as it exists on the host, independent of the Pod. Using the [hostPath](https://kubernetes.io/docs/concepts/storage/volumes/#hostpath) volume type presents many security risks.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `/data` |

### `mysql.volumeSpec.hostPath.type`

Specifies a [type](https://kubernetes.io/docs/concepts/storage/volumes/#hostpath-volume-types) for the hostPath volume.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `Directory` |

### `mysql.volumeSpec.persistentVolumeClaim.storageClassName`

Requests a specific storage class for the Persistent Volume Claim. This will cause the PVC to match the right storage class if the cluster has StorageClasses enabled by the admin.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `standard` |

### `mysql.volumeSpec.persistentVolumeClaim.accessModes`

Specify a specific [access mode](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes) for a Persistent Volume. Kubernetes uses volume access modes to match PersistentVolumeClaims and PersistentVolumes.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `"ReadWriteOnce"` |

### `mysql.volumeSpec.persistentVolumeClaim.resources.requests.storage`

The [Kubernetes PersistentVolumeClaim :octicons-link-external-16:](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims) size for the Percona Server for MySQL.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `2Gi` |

### `mysql.gracePeriod`

Specifies the maximum time, in seconds, the Operator allows for a pod to shut down gracefully after receiving a termination signal before it is forcefully killed. This ensures critical cleanup tasks, like flushing data, can complete.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `600` |

### `mysql.configuration`

The `my.cnf` file options to be passed to Percona Server for MySQL instances.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | <pre>`[mysqld]`<br>`max_connections=250`</pre> |

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

The number of the HAProxy Pods [to provide load balancing](expose.md#use-haproxy). Safe configuration should have 2 or more. This setting is required.

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

### `proxy.haproxy.schedulerName`

The name of a [Kubernetes scheduler :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/) used to assign HAProxy Pods to Kubernetes nodes. The `default-scheduler` means `kube-scheduler` is used. You can define your custom schedulers here.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `default-scheduler` |

### `proxy.haproxy.priorityClassName`

The name of the Kubernetes [PriorityClass :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/#priorityclass), which is a way to assign priority levels to pods, helping the scheduler decide which pods to schedule first and which ones to evict last when resources are tight.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `high-priority` |

### `proxy.haproxy.nodeSelector`

[Kubernetes nodeSelector :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#nodeselector). It enables you to define node labels thereby ensuring that Pods will be scheduled onto nodes that have each of the labels you specify.

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `disktype: ssd` |

### `proxy.haproxy.serviceAccountName`

The [Kubernetes Service Account :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/) for the HAProxy Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `percona-server-mysql-operator-orchestrator` |


### `proxy.haproxy.podDisruptionBudget.maxUnavailable`

The number of unavailable Pods your cluster can tolerate during voluntary disruption. It can be either an absolute value or a percentage.

To learn more, see [podDisruptionBudgets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 1 |

### `proxy.haproxy.podDisruptionBudget.minAvailable`

The number of Pods that must remain available during voluntary disruption. It can be either an absolute value or a percentage.

To learn more, see [podDisruptionBudgets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 0 |

### `proxy.haproxy.runtimeClassName`

Specifies the name of the [RuntimeClass :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/runtime-class/) resource used to define and select the container runtime configuration.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `image-rc` |

### `proxy.haproxy.tolerations`

Specifies the [Kubernetes tolerations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) applied to HAProxy Pods allowing them to be scheduled on nodes with matching taints. Tolerations enable the Pod to tolerate specific node conditions, such as resource constraints being temporary unreachable, without being evicted immediately.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | `node.alpha.kubernetes.io/unreachable` |

### `proxy.haproxy.imagePullSecrets.name`

Specifies the Kubernetes [imagePullSecrets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/#using-imagepullsecrets) for the HAProxy image.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-secret-1` |

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

### `proxy.haproxy.startupProbe.initialDelaySeconds`

The number of seconds to wait before performing the [startup probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `15` |

### `proxy.haproxy.startupProbe.timeoutSeconds`

The number of seconds after which the [startup probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `43200` |

### `proxy.haproxy.startupProbe.periodSeconds`

How often to perform the [startup probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/). Measured in seconds.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `10` |

### `proxy.haproxy.startupProbe.successThreshold`

The number of successful probes required to mark the container successful.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `proxy.haproxy.startupProbe.failureThreshold`

The number of failed probes required to mark the container unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `proxy.haproxy.readinessProbe.timeoutSeconds`

Number of seconds after which the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `proxy.haproxy.readinessProbe.periodSeconds`

How often (in seconds) to perform the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `5` |

### `proxy.haproxy.readinessProbe.successThreshold`

Minimum consecutive successes for the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) to be considered successful after having failed.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `proxy.haproxy.readinessProbe.failureThreshold`

When the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) fails, Kubernetes will try this number of times before marking the Pod Unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `proxy.haproxy.livenessProbe.timeoutSeconds`

Number of seconds after which the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `proxy.haproxy.livenessProbe.periodSeconds`

How often (in seconds) to perform the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `5` |

### `proxy.haproxy.livenessProbe.successThreshold`

Minimum consecutive successes for the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) to be considered successful after having failed.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `proxy.haproxy.livenessProbe.failureThreshold`

When the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) fails, Kubernetes will try this number of times before marking the Pod Unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `proxy.haproxy.gracePeriod`

Specifies the maximum time, in seconds, the Operator allows for a pod to shut down gracefully after receiving a termination signal before it is forcefully killed. This ensures critical cleanup tasks, like flushing data, can complete.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `30` |

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

The static IP-address for the load balancer. This field is deprecated in Kubernetes 1.24+ and removed from the Operator starting with version 0.10.0. If you have defined it, refer to the [Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) for recommendations. 

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `127.0.0.1` |

### `proxy.haproxy.expose.loadBalancerSourceRanges`

The range of client IP addresses from which the load balancer should be reachable (if not set, there is no limitations) |

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `10.0.0.0/8` |

### `proxy.haproxy.containerSecurityContext`

A custom [Kubernetes Security Context for a Container :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) used for the HAProxy installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>privileged: false<br>runAsUser: 1001<br>runAsGroup: 1001</pre> |

### `proxy.haproxy.podSecurityContext`

A custom [Kubernetes Security Context for a Pod :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) to be used instead of the default one.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>fsGroup: 1001<br>supplementalGroups: [1001, 1002, 1003]</pre> |

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

### `proxy.router.runtimeClassName`

Specifies the name of the [RuntimeClass :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/runtime-class/) resource used to define and select the container runtime configuration.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `image-rc` |

### `proxy.router.tolerations`

Specifies the [Kubernetes tolerations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) applied to Router Pods allowing them to be scheduled on nodes with matching taints. Tolerations enable the Pod to tolerate specific node conditions, such as temporary unreachability or resource constraints, without being evicted immediately.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | `node.alpha.kubernetes.io/unreachable` |

### `proxy.router.imagePullSecrets.name`

Specifies the Kubernetes [imagePullSecrets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/#using-imagepullsecrets) for the Router image.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-secret-1` |

### `proxy.router.initContainer.image`

An alternative init image for MySQL Router Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}` |

### `proxy.router.initContainer.containerSecurityContext`

A custom [Kubernetes Security Context for a Container :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) for the image used for MySQL Router Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>privileged: false<br>runAsUser: 1001<br>runAsGroup: 1001</pre> |

### `proxy.router.initContainer.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for MySQL Router Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100M` |

### `proxy.router.initContainer.resources.requests.cpu`

[Kubernetes CPU requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for MySQL Router Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100m` |

### `proxy.router.initContainer.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for MySQL Router Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `200M` |

### `proxy.router.initContainer.resources.limits.cpu`

[Kubernetes CPU limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for MySQL Router Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `200m` |

### `proxy.router.env.name`

Name of an environment variable for MySQL Router Pods. Read more about defining environment variables in [Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `MY_ENV` |

### `proxy.router.env.value`

Value of an environment variable for MySQL Router Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `"1000"` |

### `proxy.router.envFrom.secretRef.name`

Name of a Secret or a ConfigMap, key/values of which are used as environment variables for MySQL Router Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-env-secret` |

### `proxy.router.podDisruptionBudget.maxUnavailable`

The number of unavailable Pods your cluster can tolerate during voluntary disruption. It can be either an absolute value or a percentage.

To learn more, see [podDisruptionBudgets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 1 |

### `proxy.router.podDisruptionBudget.minAvailable`

The number of Pods that must remain available during voluntary disruption. It can be either an absolute value or a percentage.

To learn more, see [podDisruptionBudgets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 0 |

### `proxy.router.ports.name`

The name for a custom or an existing port for the MySQL Router Service. 

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `http` |

### `proxy.router.ports.port`

The port exposed by the MySQL Router service to the outside world or other components.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `8443` |

### `proxy.router.ports.targetPort`

The port inside the Pod/container where MySQL Router is actually listening. When a client connects to the external port, Kubernetes forwards that traffic to the `targetPort` value on the backend Pod. A zero (0) value means Kubernetes uses the default internal port or does not do the remapping.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `0` |

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

### `proxy.router.gracePeriod`

Specifies the maximum time, in seconds, the Operator allows for a pod to shut down gracefully after receiving a termination signal before it is forcefully killed. This ensures critical cleanup tasks, like flushing data, can complete.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `30` |

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

The static IP-address for the load balancer. This field is deprecated in Kubernetes 1.24+ and removed from the Operator starting with version 0.10.0. If you have defined it, refer to the [Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) for recommendations.

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

### `orchestrator.runtimeClassName`

Specifies the name of the [RuntimeClass :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/runtime-class/) resource used to define and select the container runtime configuration.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `image-rc` |

### `orchestrator.schedulerName`

The name of a [Kubernetes scheduler :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/) used to assign Orchestrator Pods to Kubernetes nodes. The `default-scheduler` means `kube-scheduler` is used. You can define your custom schedulers here.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `default-scheduler` |

### `orchestrator.priorityClassName`

The name of the Kubernetes [PriorityClass :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/#priorityclass), which is a way to assign priority levels to pods, helping the scheduler decide which pods to schedule first and which ones to evict last when resources are tight.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `high-priority` |

### `orchestrator.nodeSelector`

[Kubernetes nodeSelector :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#nodeselector). It enables you to define node labels thereby ensuring that Pods will be scheduled onto nodes that have each of the labels you specify.

| Value type  | Example    |
| ----------- | ---------- |
| :material-label-outline: label     | `disktype: ssd` |

### `orchestrator.startupProbe.initialDelaySeconds`

The number of seconds to wait before performing the [startup probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `15` |

### `orchestrator.startupProbe.timeoutSeconds`

The number of seconds after which the [startup probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `43200` |

### `orchestrator.startupProbe.periodSeconds`

How often to perform the [startup probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/). Measured in seconds.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `10` |

### `orchestrator.startupProbe.successThreshold`

The number of successful probes required to mark the container successful.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `orchestrator.startupProbe.failureThreshold`

The number of failed probes required to mark the container unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `orchestrator.readinessProbe.timeoutSeconds`

Number of seconds after which the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `orchestrator.readinessProbe.periodSeconds`

How often (in seconds) to perform the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `5` |

### `orchestrator.readinessProbe.successThreshold`

Minimum consecutive successes for the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) to be considered successful after having failed.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `orchestrator.readinessProbe.failureThreshold`

When the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) fails, Kubernetes will try this number of times before marking the Pod Unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `orchestrator.livenessProbe.timeoutSeconds`

Number of seconds after which the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `orchestrator.livenessProbe.periodSeconds`

How often (in seconds) to perform the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `5` |

### `orchestrator.livenessProbe.successThreshold`

Minimum consecutive successes for the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) to be considered successful after having failed.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

### `orchestrator.livenessProbe.failureThreshold`

When the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) fails, Kubernetes will try this number of times before marking the Pod Unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `orchestrator.env.name`

Name of an environment variable for Orchestrator Pods. Read more about defining environment variables in [Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `MY_ENV` |

### `orchestrator.env.value`

Value of an environment variable for Orchestrator Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `"1000"` |

### `orchestrator.envFrom.secretRef.name`

Name of a Secret or a ConfigMap, key/values of which are used as environment variables for Orchestrator Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-env-secret` |

### `orchestrator.tolerations`

Specifies the [Kubernetes tolerations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) applied to Orchestrator Pods allowing them to be scheduled on nodes with matching taints. Tolerations enable the Pod to tolerate specific node conditions, such as temporary unreachability or resource constraints, without being evicted immediately.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | `node.alpha.kubernetes.io/unreachable` |

### `orchestrator.imagePullSecrets.name`

Specifies the Kubernetes [imagePullSecrets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/#using-imagepullsecrets) for the Orchestrator image.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-secret-1` |


### `orchestrator.serviceAccountName`

The [Kubernetes Service Account :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/) for the Orchestrator Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `percona-server-mysql-operator-orchestrator` |

### `orchestrator.initContainer.image`

An alternative init image for Orchestrator Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}` |

### `orchestrator.initContainer.containerSecurityContext`

A custom [Kubernetes Security Context for a Container :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) for the image used for Orchestrator Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>privileged: false<br>runAsUser: 1001<br>runAsGroup: 1001</pre> |

### `orchestrator.initContainer.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for Orchestrator Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100M` |

### `orchestrator.initContainer.resources.requests.cpu`

[Kubernetes CPU requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for Orchestrator Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100m` |

### `orchestrator.initContainer.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for Orchestrator Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `200M` |

### `orchestrator.initContainer.resources.limits.cpu`

[Kubernetes CPU limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for Orchestrator Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `200m` |

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

### `orchestrator.gracePeriod`

Specifies the maximum time, in seconds, the Operator allows for a pod to shut down gracefully after receiving a termination signal before it is forcefully killed. This ensures critical cleanup tasks, like flushing data, can complete.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `30` |


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

### `orchestrator.containerSecurityContext`

A custom [Kubernetes Security Context for a Container :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) used for the Orchestrator installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>privileged: false<br>runAsUser: 1001<br>runAsGroup: 1001</pre> |

### `orchestrator.podSecurityContext`

A custom [Kubernetes Security Context for a Pod :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) to be used instead of the default one.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>fsGroup: 1001<br>supplementalGroups: [1001, 1002, 1003]</pre> |

### `orchestrator.podDisruptionBudget.maxUnavailable`

The number of unavailable Pods your cluster can tolerate during voluntary disruption. It can be either an absolute value or a percentage.

To learn more, see [podDisruptionBudgets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 1 |

### `orchestrator.podDisruptionBudget.minAvailable`

The number of Pods that must remain available during voluntary disruption. It can be either an absolute value or a percentage.

To learn more, see [podDisruptionBudgets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | 0 |

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

### `pmm.readinessProbes.initialDelaySeconds`

The number of seconds to wait before performing the first [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `15` |

### `pmm.readinessProbes.timeoutSeconds`

The number of seconds after which the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `15` |

### `pmm.readinessProbes.periodSeconds`

How often to perform the [readiness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/). Measured in seconds.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `30` |

### `pmm.readinessProbes.successThreshold`

The number of successful probes required to mark the container successful.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `pmm.readinessProbes.failureThreshold`

The number of failed probes required to mark the container unready.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `5` |

### `pmm.livenessProbes.initialDelaySeconds`

The number of seconds to wait before performing the first [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `300` |

### `pmm.livenessProbes.timeoutSeconds`

The number of seconds after which the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) times out.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `5` |

### `pmm.livenessProbes.periodSeconds`

How often to perform the [liveness probe :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/). Measured in seconds.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `10` |

### `pmm.livenessProbes.successThreshold`

The number of successful probes required to mark the container successful.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `1` |

### `pmm.livenessProbes.failureThreshold`

The number of failed probes required to mark the container unhealthy.

| Value type  | Example    |
| ----------- | ---------- |
| :material-numeric-1-box: int     | `3` |

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

### `backup.sourcePod`

Specifies the MySQL instance Pod to take a backup from. When defined, takes precedence, regardless of the cluster type (async or group-replication) and topology. Applies both to scheduled and on-demand backups.

Asynchronous replication clusters that consist of more than one Pod and have the Orchestrator disabled must have the `sourcePod` defined for the Operator to make backups. Otherwise, the Operator fails to start a backup and reports an error.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `ps-cluster1-mysql-0` |

### `backup.image`

The Percona XtraBackup Docker image to use for the backup.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `percona/percona-server-mysql-operator:{{ release }}-backup` |

### `backup.imagePullPolicy`

The [policy used to update images :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/images/#updating-images).

| **Value**       | string  |
| **Example**     | `Always` |

### `backup.imagePullSecrets.name`

The [Kubernetes ImagePullSecret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/#using-imagepullsecrets).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-secret-1` |

### `backup.initContainer.image`

An alternative init image for Percona XtraBackup Pods.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `perconalab/percona-server-mysql-operator:{{ release }}` |

### `backup.initContainer.containerSecurityContext`

A custom [Kubernetes Security Context for a Container :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) for the image used for Percona XtraBackup Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>privileged: false<br>runAsUser: 1001<br>runAsGroup: 1001</pre> |

### `backup.initContainer.resources.requests.memory`

The [Kubernetes memory requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for Percona XtraBackup Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100M` |

### `backup.initContainer.resources.requests.cpu`

[Kubernetes CPU requests :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for Percona XtraBackup Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `100m` |

### `backup.initContainer.resources.limits.memory`

[Kubernetes memory limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for Percona XtraBackup Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `200M` |

### `backup.initContainer.resources.limits.cpu`

[Kubernetes CPU limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an image used for Percona XtraBackup Pods installation.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `200m` |

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

### `backup.storages.STORAGE-NAME.runtimeClassName`

Specifies the name of the [RuntimeClass :octicons-link-external-16:](https://kubernetes.io/docs/concepts/containers/runtime-class/) resource used to define and select the container runtime configuration for backup and restore jobs associated with the specific storage.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `image-rc` |

### `backup.storages.STORAGE-NAME.containerOptions.env`

The [environment variables set as key-value pairs :octicons-link-external-16:](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/) for the backup container.

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>- name: CUSTOM_ENV<br>  value: "some-value"</pre> |

### `backup.storages.STORAGE-NAME.containerOptions.args.xtrabackup`

Custom [command line options :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/innovation-release/xtrabackup-option-reference.html) for the [`xtrabackup` Percona XtraBackup tool :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/8.0/xtrabackup-binary-overview.html).

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>- "--someflag=abc"</pre> |

### `backup.storages.STORAGE-NAME.containerOptions.args.xbcloud`

Custom [command line options :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/innovation-release/xbcloud-options.html) for the [`xbcloud` Percona XtraBackup tool :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/8.0/xbcloud-binary-overview.html).

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>- "--someflag=abc"</pre> |

### `backup.storages.STORAGE-NAME.containerOptions.args.xbstream`

Custom [command line options :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/innovation-release/xbstream-options.html) for the [`xbstream` Percona XtraBackup tool :octicons-link-external-16:](https://docs.percona.com/percona-xtrabackup/8.0/xbstream-binary-overview.html)

| Value type  | Example    |
| ----------- | ---------- |
| :material-text-long: subdoc     | <pre>- "--someflag=abc"</pre> |

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

The endpoint URL of the S3-compatible storage to be used (not needed for the original Amazon S3 cloud) 

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | |

### `backup.storages.STORAGE-NAME.azure.container`

The name of the [Microsoft Azure blob container :octicons-link-external-16:](https://learn.microsoft.com/en-us/azure/storage/blobs/blob-containers-portal#create-a-container) for backups.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `""` |

### `backup.storages.STORAGE-NAME.azure.prefix`

The path (sub-folder) to the backups inside the [container :octicons-link-external-16:](https://learn.microsoft.com/en-us/azure/storage/blobs/blob-containers-portal).

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `""` |

### `backup.storages.STORAGE-NAME.azure.endpointUrl`

The endpoint URL of the S3-compatible storage to be used (not needed for the original Amazon S3 cloud) 

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `https://accountName.blob.core.windows.net`|

### `backup.storages.STORAGE-NAME.azure.credentialsSecret`

The [Kubernetes secret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/) for backups. It should contain the `AZURE_STORAGE_ACCOUNT_NAME` and the `AZURE_STORAGE_ACCOUNT_KEY` keys.

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `my-cluster-name-backup-azure` |

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

[Kubernetes CPU limits :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Toolkit container 

| Value type  | Example    |
| ----------- | ---------- |
| :material-code-string: string     | `400m` |


