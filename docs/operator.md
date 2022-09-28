# <a name="operator-custom-resource-options"></a>Custom Resource options

Percona Server for MySQL managed by the Operator is configured via the spec section
of the [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
file.

The metadata part of this file contains the following keys:


* `name` (`cluster1` by default) sets the name of your Percona Server for
MySQL cluster; it should include only [URL-compatible characters](https://datatracker.ietf.org/doc/html/rfc3986#section-2.3),
not exceed 22 characters, start with an alphabetic character, and end with an
alphanumeric character;

* `finalizers.delete-mysql-pods-in-order` if present, activates the [Finalizer](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#finalizers) which controls the proper Pods deletion order in case of the cluster deletion event (on by default).

The spec part of the [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains the following sections:

| Key             | Value type         | Default            | Description                                |
| --------------- | ------------------ | ------------------ | ------------------------------------------ |
| mysql           | subdoc             |                    | Percona Server for MySQL general section   |
| orchestrator    | subdoc             |                    | Orchestrator section                       |
| pmm             | subdoc             |                    | Percona Monitoring and Management section  |
| secretsName     | string             | `cluster1-secrets` | A name for [users secrets](users.md#users) |
| sslSecretName   | string             | `cluster1-ssl`     | A secret with TLS certificate generated for *external* communications, see [Transport Layer Security (TLS)](TLS.md#tls) for details |

## <a name="operator-mysql-section"></a>Percona Server for MySQL section

The `mysql` section in the [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains general
configuration options for the Percona Server for MySQL.

|                 | |
|-----------------|-|
| **Key**         | {{ optionlink('mysql.clusterType') }} |
| **Value**       | int |
| **Example**     | `async` |
| **Description** | The cluster type: `async` for [Asynchronous replication](https://dev.mysql.com/doc/refman/8.0/en/replication.html), `group-replication` for [Group Replication](https://dev.mysql.com/doc/refman/8.0/en/group-replication.html) |
|                 | |
| **Key**         | {{ optionlink('mysql.size') }} |
| **Value**       | int |
| **Example**     | `3` |
| **Description** | The number of the Percona Server for MySQL instances |
|                 | |
| **Key**         | {{ optionlink('mysql.image') }} |
| **Value**       | string |
| **Example**     | `percona/percona-server:{{ ps80recommended }}` |
| **Description** | The Docker image of the Percona Server for MySQL used (actual image names for Percona Server for MySQL 8.0 and Percona Server for MySQL 5.7 can be found [in the list of certified images](images.md#custom-registry-images)) |
|                 | |
| **Key**         | {{ optionlink('mysql.imagePullSecrets.name') }} |
| **Value**       | string |
| **Example**     | `private-registry-credentials` |
| **Description** | The [Kubernetes ImagePullSecret](https://kubernetes.io/docs/concepts/configuration/secret/#using-imagepullsecrets) |
|                 | |
| **Key**         | {{ optionlink('mysql.sizeSemiSync') }} |
| **Example**     | `0` |
| **Description** | The number of the Percona Server for MySQL [semi-sync](https://dev.mysql.com/doc/refman/8.0/en/replication-semisync.html) replicas |
|                 | |
| **Key**         | {{ optionlink('mysql.primaryServiceType') }} |
| **Value**       | string |
| **Example**     | `LoadBalancer` |
| **Description** | Specifies the type of [Kubernetes Service](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) to be used for Primary instance if the asyncronous replication is turned on |
|                 | |
| **Key**         | {{ optionlink('mysql.replicasServiceType') }} |
| **Value**       | string |
| **Example**     | `ClusterIP` |
| **Description** | Specifies the type of [Kubernetes Service](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) to be used for Replica instances if the asyncronous replication is turned on |
|                 | |
| **Key**         | {{ optionlink('mysql.resources.requests.memory') }} |
| **Value**       | string |
| **Example**     | `512M` |
| **Description** | The [Kubernetes memory requests](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Server for MySQL container |
|                 | |
| **Key**         | {{ optionlink('mysql.resources.limits.memory') }} |
| **Value**       | string |
| **Example**     | `1G` |
| **Description** | [Kubernetes memory limits](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Server for MySQL container |
|                 | |
| **Key**         | {{ optionlink('mysql.affinity.antiAffinityTopologyKey') }} |
| **Value**       | string |
| **Example**     | `kubernetes.io/hostname` |
| **Description** | The Operator [topology key](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) node anti-affinity constraint |
|                 | |
| **Key**         | {{ optionlink('mysql.affinity.advanced') }} |
| **Value**       | subdoc |
| **Example**     | |
| **Description** | In cases where the Pods require complex tuning the advanced option turns off the `topologyKey` effect. This setting allows the [standard Kubernetes affinity constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#node-affinity) of any complexity to be used |
|                 | |
| **Key**         | {{ optionlink('mysql.expose.enabled') }} |
| **Value**       | boolean |
| **Example**     | `true` |
| **Description** | Enable or disable exposing Percona Server for MySQL nodes with dedicated IP addresses |
|                 | |
| **Key**         | {{ optionlink('mysql.expose.type') }} |
| **Value**       | string |
| **Example**     | `ClusterIP` |
| **Description** | The [Kubernetes Service Type](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) used for exposure |
|                 | |
| **Key**         | {{ optionlink('mysql.volumeSpec.persistentVolumeClaim.resources.requests.storage') }} |
| **Value**       | string |
| **Example**     | `2Gi` |
| **Description** | The [Kubernetes PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims) size for the Percona Server for MySQL |
|                 | |
| **Key**         | {{ optionlink('mysql.configuration') }} |
| **Value**       | string |
| **Example**     | <pre>&#124;<br>`[mysqld]`<br>`max_connections=250`</pre> |
| **Description** | The `my.cnf` file options to be passed to Percona Server for MySQL instances |
|                 | |
| **Key**         | {{ optionlink('mysql.sidecars.image') }} |
| **Value**       | string |
| **Example**     | `busybox` |
| **Description** | Image for the [custom sidecar container](sidecar.md#operator-sidecar) for Percona Server for MySQL Pods |
|                 | |
| **Key**         | {{ optionlink('mysql.sidecars.command') }} |
| **Value**       | array |
| **Example**     | `["sleep", "30d"]` |
| **Description** | Command for the [custom sidecar container](sidecar.md#operator-sidecar) for Percona Server for MySQL Pods |
|                 | |
| **Key**         | {{ optionlink('mysql.sidecars.name') }} |
| **Value**       | string |
| **Example**     | `my-sidecar-1` |
| **Description** | Name of the [custom sidecar container](sidecar.md#operator-sidecar) for Percona Server for MySQL Pods |
|                 | |
| **Key**         | {{ optionlink('mysql.sidecars.volumeMounts.mountPath') }} |
| **Value**       | string |
| **Example**     | `/volume1` |
| **Description** | Mount path of the [custom sidecar container](sidecar.md#operator-sidecar) volume for Replica Set Pods |
|                 | |
| **Key**         | {{ optionlink('mysql.sidecars.resources.requests.memory') }} |
| **Value**       | string |
| **Example**     | `16M` |
| **Description** | The [Kubernetes memory requests](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona Server for MySQL sidecar container |
|                 | |
| **Key**         | {{ optionlink('mysql.sidecars.volumeMounts.name') }} |
| **Value**       | string |
| **Example**     | `sidecar-volume-claim` |
| **Description** | Name of the [custom sidecar container](sidecar.md#operator-sidecar) volume for Replica Set Pods |
|                 | |
| **Key**         | {{ optionlink('mysql.sidecarVolumes') }} |
| **Value**       | subdoc |
| **Example**     | |
| **Description** | [Volume specification](https://kubernetes.io/docs/concepts/storage/volumes/) for the [custom sidecar container](sidecar.md#operator-sidecar) volume for Percona Server for MySQL Pods |
|                 | |
| **Key**         | {{ optionlink('mysql.sidecarPVCs') }} |
| **Value**       | subdoc |
| **Example**     | |
| **Description** | [Persistent Volume Claim](https://v1-20.docs.kubernetes.io/docs/concepts/storage/persistent-volumes/) for the [custom sidecar container](sidecar.md#operator-sidecar) volume for Replica Set Pods |

## <a name="operator-router-section"></a>Router section

The `router` section in the [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains configuration options for the [MySQL Router](https://dev.mysql.com/doc/mysql-router/8.0/en/), which acts as a proxy for Group replication.

|                 | |
|-----------------|-|
| **Key**         | {{ optionlink('router.size') }} |
| **Value**       | int |
| **Example**     | `3` |
| **Description** | The number of the Router Pods to provide routing to MySQL Servers |
|                 | |
| **Key**         | {{ optionlink('router.image') }} |
| **Value**       | string |
| **Example**     | `perconalab/percona-server-mysql-operator:{{ release }}-router` |
| **Description** | Router Docker image to use |
|                 | |
| **Key**         | {{ optionlink('router.imagePullPolicy') }} |
| **Value**       | string |
| **Example**     | `Always` |
| **Description** | The [policy used to update images](https://kubernetes.io/docs/concepts/containers/images/#updating-images) |
|                 | |
| **Key**         | {{ optionlink('router.affinity.antiAffinityTopologyKey') }} |
| **Value**       | string |
| **Example**     | `kubernetes.io/hostname` |
| **Description** | The Operator [topology key](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) node anti-affinity constraint |
|                 | |
| **Key**         | {{ optionlink('router.affinity.advanced') }} |
| **Value**       | subdoc |
| **Example**     | |
| **Description** | In cases where the Pods require complex tuning the advanced option turns off the
`topologyKey` effect. This setting allows the
[standard Kubernetes affinity constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#node-affinity)
of any complexity to be used |
|                 | |
| **Key**         | {{ optionlink('router.resources.requests.memory') }} |
| **Value**       | string |
| **Example**     | `256M` |
| **Description** | The [Kubernetes memory requests](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for MySQL Router container |
|                 | |
| **Key**         | {{ optionlink('router.resources.limits.memory') }} |
| **Value**       | string |
| **Example**     | `256M` |
| **Description** | [Kubernetes memory limits](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for MySQL Router container |
|                 | |
| **Key**         | {{ optionlink('router.expose.type') }} |
| **Value**       | string |
| **Example**     | `ClusterIP` |
| **Description** | The [Kubernetes Service Type](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) used for MySQL Router instances exposure |

## <a name="operator-orchestrator-section"></a>Orchestrator section

The `orchestrator` section in the [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains
configuration options for the Orchestrator - a replication topology manager, used if asynchronous replication is turned on.

|                 | |
|-----------------|-|
| **Key**         | {{ optionlink('orchestrator.size') }} |
| **Value**       | int |
| **Example**     | `3` |
| **Description** | The number of the Orchestrator Pods to provide load balancing |
|                 | |
| **Key**         | {{ optionlink('orchestrator.image') }} |
| **Value**       | string |
| **Example**     | `perconalab/percona-server-mysql-operator:{{ release }}-orchestrator` |
| **Description** | Orchestrator Docker image to use |
|                 | |
| **Key**         | {{ optionlink('orchestrator.imagePullPolicy') }} |
| **Value**       | string |
| **Example**     | `Always` |
| **Description** | The [policy used to update images](https://kubernetes.io/docs/concepts/containers/images/#updating-images) |
|                 | |
| **Key**         | {{ optionlink('orchestrator.affinity.antiAffinityTopologyKey') }} |
| **Value**       | string |
| **Example**     | `kubernetes.io/hostname` |
| **Description** | The Operator [topology key](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) node anti-affinity constraint |
|                 | |
| **Key**         | {{ optionlink('orchestrator.affinity.advanced') }} |
| **Value**       | subdoc |
| **Example**     | |
| **Description** | In cases where the Pods require complex tuning the advanced option turns off the `topologyKey` effect. This setting allows the [standard Kubernetes affinity constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#node-affinity) of any complexity to be used |
|                 | |
| **Key**         | {{ optionlink('orchestrator.expose.type') }} |
| **Value**       | string |
| **Example**     | `ClusterIP` |
| **Description** | The [Kubernetes Service Type](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) used for Orchestrator instances exposure |
|                 | |
| **Key**         | {{ optionlink('orchestrator.resources.requests.memory') }} |
| **Value**       | string |
| **Example**     | `128M` |
| **Description** | The [Kubernetes memory requests](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an Orchestrator container |
|                 | |
| **Key**         | {{ optionlink('orchestrator.resources.limits.memory') }} |
| **Value**       | string |
| **Example**     | `256M` |
| **Description** | [Kubernetes memory limits](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for an Orchestrator container |
|                 | |
| **Key**         | {{ optionlink('orchestrator.volumeSpec.persistentVolumeClaim.resources.requests.storage') }} |
| **Value**       | string |
| **Example**     | `1Gi` |
| **Description** | The [Kubernetes PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims) size for the Orchestrator |

## <a name="operator-pmm-section"></a>PMM section

The `pmm` section in the [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) file contains configuration
options for Percona Monitoring and Management.

|                 | |
|-----------------|-|
| **Key**         | {{ optionlink('pmm.enabled') }} |
| **Value**       | boolean |
| **Example**     | `false` |
| **Description** | Enables or disables [monitoring Percona Server for MySQL with PMM](https://www.percona.com/doc/percona-xtradb-cluster/5.7/manual/monitoring.html) |
|                 | |
| **Key**         | {{ optionlink('pmm.image') }} |
| **Value**       | string |
| **Example**     | `percona/pmm-client:{{ pmm2recommended }}` |
| **Description** | PMM client Docker image to use |
|                 | |
| **Key**         | {{ optionlink('pmm.imagePullPolicy') }} |
| **Value**       | string |
| **Example**     | `Always` |
| **Description** | The [policy used to update images](https://kubernetes.io/docs/concepts/containers/images/#updating-images) |
|                 | |
| **Key**         | {{ optionlink('pmm.serverHost') }} |
| **Value**       | string |
| **Example**     | `monitoring-service` |
| **Description** | Address of the PMM Server to collect data from the cluster |
|                 | |
| **Key**         | {{ optionlink('pmm.serverUser') }} |
| **Value**       | string |
| **Example**     | `admin` |
| **Description** | The [PMM Serve_User](https://www.percona.com/doc/percona-monitoring-and-management/glossary.option.html). The PMM Server password should be configured using Secrets |

## <a name="operator-backup-section"></a>Backup section

The `backup` section in the [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
file contains the following configuration options for the regular Percona XtraDB Cluster backups.

|                 | |
|-----------------|-|
| **Key**         | {{ optionlink('backup.enabled') }} |
| **Value**       | boolean |
| **Example**     | `true` |
| **Description** | Enables or disables making backups |
|                 | |
| **Key**         | {{ optionlink('backup.image') }} |
| **Value**       | string |
| **Example**     | `percona/percona-server-mysql-operator:{{ release }}-backup` |
| **Description** | The Percona XtraBackup Docker image to use for the backup |
|                 | |
| **Key**         | {{ optionlink('backup.imagePullPolicy') }} |
| **Value**       | string  |
| **Example**     | `Always` |
| **Description** | The [policy used to update images](https://kubernetes.io/docs/concepts/containers/images/#updating-images) |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.type') }} |
| **Value**       | string |
| **Example**     | `s3` |
| **Description** | The cloud storage type used for backups. Only `s3` and `azure` types are supported |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.verifyTLS') }} |
| **Value**       | boolean |
| **Example**     | `true` |
| **Description** | Enable or disable verification of the storage server TLS certificate. Disabling it may be useful e.g. to skip TLS verification for private S3-compatible storage with a self-issued certificate |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.nodeSelector') }} |
| **Value**       | label |
| **Example**     | `disktype: ssd` |
| **Description** | [Kubernetes nodeSelector](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#nodeselector) |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.resources.requests.memory') }} |
| **Value**       | string |
| **Example**     | `1G` |
| **Description** | The [Kubernetes memory requests](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona XtraBackup container |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.resources.requests.cpu') }} |
| **Value**       | string |
| **Example**     | `600m` |
| **Description** | [Kubernetes CPU requests](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#resource-requests-and-limits-of-pod-and-container) for a Percona XtraBackup container |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.affinity.nodeAffinity') }} |
| **Value**       | subdoc |
| **Example**     | |
| **Description** | The Operator [node affinity](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) constraint |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.tolerations') }} |
| **Value**       | subdoc |
| **Example**     | |
| **Description** | [Kubernetes Pod tolerations](https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/) |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.schedulerName') }} |
| **Value**       | string |
| **Example**     | `mycustom-scheduler` |
| **Description** | The [Kubernetes Scheduler](https://kubernetes.io/docs/tasks/administer-cluster/configure-multiple-schedulers) |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.priorityClassName') }} |
| **Value**       | string |
| **Example**     | `high-priority` |
| **Description** | The [Kubernetes Pod priority class](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/#priorityclass) |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.containerSecurityContext') }} |
| **Value**       | subdoc |
| **Example**     | `privileged: true` |
| **Description** | A custom [Kubernetes Security Context for a Container](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) to be used instead of the default one |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.podSecurityContext') }} |
| **Value**       | subdoc |
| **Example**     | <pre>fsGroup: 1001<br>supplementalGroups: [1001, 1002, 1003]</pre> |
| **Description** | A custom [Kubernetes Security Context for a Pod](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) to be used instead of the default one |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.annotations') }} |
| **Value**       | label |
| **Example**     | `testName: scheduled-backup` |
| **Description** | The [Kubernetes annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.labels') }} |
| **Value**       | label |
| **Example**     | `backupWorker: 'True'` |
| **Description** | [Labels are key-value pairs attached to objects](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.s3.bucket') }} |
| **Value**       | string  |
| **Example**     | |
| **Description** | The [Amazon S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html) name for backups |
|                 | |
| **Key**         | {{ optionlink('backup.storages.s3.&lt;storage-name&gt;.region') }} |
| **Value**       | string |
| **Example**     | `us-west-2` |
| **Description** | The [AWS region](https://docs.aws.amazon.com/general/latest/gr/rande.html) to use. Please note **this option is mandatory** for Amazon and all S3-compatible storages |
|                 | |
| **Key**         | {{ optionlink('backup.storages.s3.&lt;storage-name&gt;.prefix') }} |
| **Value**       | string |
| **Example**     | `""` |
| **Description** | The path (sub-folder) to the backups inside the [bucket](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html) |
|                 | |
| **Key**         | {{ optionlink('backup.storages.&lt;storage-name&gt;.s3.credentialsSecret') }} |
| **Value**       | string |
| **Example**     | `my-cluster-name-backup-s3` |
| **Description** | The [Kubernetes secret](https://kubernetes.io/docs/concepts/configuration/secret/) for backups. It should contain `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` keys |
|                 | |
| **Key**         | {{ optionlink('backup.storages.s3.&lt;storage-name&gt;.endpointUrl') }} |
| **Value**       | string |
| **Example**     | |
| **Description** | The endpoint URL of the S3-compatible storage to be used (not needed for the original Amazon S3 cloud) |
