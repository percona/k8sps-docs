> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Scale Percona Distribution for MySQL on Kubernetes

One of the great advantages brought by Kubernetes platform is the ease of an application scaling. Scaling an application results in adding or removing the Pods and scheduling them to available Kubernetes nodes.

Scaling can be [vertical](#vertical-scaling) and [horizontal](#horizontal-scaling). Vertical scaling adds more compute or storage resources to MySQL nodes; horizontal scaling is about adding more nodes to the cluster. [High availability](https://docs.percona.com/percona-operator-for-mysql/1.3.0/architecture.html#high-availability) looks technically similar, because it also involves additional nodes, but the reason is maintaining liveness of the system in case of server or network failures.

## Vertical scaling

### Scale compute resources

The Operator deploys and manages multiple components, such as Percona Server for MySQL, Orchestrator, HAProxy or MySQL Router and others. You can manage CPU or memory for every component separately by editing corresponding sections in the Custom Resource. We follow the structure for `requests` and `limits` that [Kubernetes provides](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) .

For example, you can add more resources to your HAProxy nodes by editing the following section in the Custom Resource:

```
spec:
  ...
  proxy:
    haproxy:
      ...
      resources:
        requests:
          memory: 4G
          cpu: 2
        limits:
          memory: 4G
          cpu: 2
```

Use our reference documentation for the [Custom Resource options](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html) for more details about other components.

Note

Changing compute resources for MySQL Pods (`mysql.resources`) triggers a recalculation of the MySQL configuration, when the [automatic configuration tuning](https://docs.percona.com/percona-operator-for-mysql/1.3.0/autoconfig.html) is enabled (`mysql.autoConfig.enabled: true`). The settings that usually change because of that are buffer pool and redo log. Since they can only be set at startup, this causes a rolling restart of the MySQL StatefulSet. Plan a resize of `mysql.resources` as a change-management event.

### Scale storage

Kubernetes manages storage with the following components:

- a PersistentVolume (PV) - a segment of storage supplied by the Kubernetes administrator,
- a PersistentVolumeClaim (PVC) - a request for storage from a user.

Starting with Kubernetes v1.11, you can increase the size of an existing PVC object (considered stable since Kubernetes v1.24). Note that you **cannot shrink** the size of an existing PVC object.

Use storage scaling to keep up with growing data while keeping the cluster online. The Operator supports the following scaling options:

- automatic scaling - Starting with Operator version 1.2.0, the Operator monitors storage usage and scales the storage automatically
- storage resizing with Volume Expansion capability - Starting with the Operator version 0.11.0, you can instruct the Operator to scale the storage by updating the Custom Resource manifest
- manual scaling - scale the storage manually.

You can also use an external autoscaler with the Operator. Enabling an external autoscaler disables the Operator’s internal logic for automatic storage resizing. Choose one method based on your environment and requirements; using both simultaneously is not supported.

For either option, the volume type must support PVCs expansion.

#### Check expansion capability for your volume type

Certain volume types support PVCs expansion by default. You can run the following command to check if your storage supports the expansion capability:

```
kubectl describe sc <storage class name> | grep AllowVolumeExpansion
```

Expected output

```
AllowVolumeExpansion: true
```

Find exact details about PVCs and the supported volume types in [Kubernetes documentation](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#expanding-persistent-volumes-claims) .

#### Automatic storage resizing

Starting with version 1.2.0, the Operator can automatically resize Persistent Volume Claims (PVCs) for Percona Server for MySQL Pods based on your configured thresholds. The Operator monitors storage usage of MySQL PVCs. When the usage exceeds the defined threshold, the Operator triggers resizing until the storage size reaches the maximum limit.

This feature gives you:

- fewer outages from full disks because storage grows with demand
- less guesswork on capacity planning and fewer last-minute fixes
- lower operational effort for developers and platform engineers
- cost control by expanding only when needed
- a more predictable environment so teams can focus on delivery

Important

Keep in mind that some storage providers may have specific limitations when it comes to expanding storage. Review your provider’s documentation and sett thresholds that work well for your environment to get the best results.

To enable automatic storage resizing, edit the `deploy/cr.yaml` Custom Resource manifest as follows:

1. Make sure the MySQL component has a storage size set.

   Example:

   ```
   spec:
     mysql:
       volumeSpec:
         persistentVolumeClaim:
           resources:
             requests:
               storage: 6Gi
   ```

1. Configure autoscaling thresholds in the [`storageScaling`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#storage-scaling-section) subsection:

   - `enableVolumeScaling` - set to `true`.
   - `autoscaling.enabled` - set to `true`
   - `autoscaling.triggerThresholdPercent` - specify the usage percentage (50–95, default `80`). When usage exceeds this threshold, autoscaling is triggered
   - `autoscaling.growthStep` - specify how much storage to add on each resize (default `2Gi`)
   - `autoscaling.maxSize` - specify the upper limit for storage growth (minimum `1Gi`). When this limit is reached, scaling stops

   Example configuration:

   ```
   spec:
     storageScaling:
       enableVolumeScaling: true
       autoscaling:
         enabled: true
         triggerThresholdPercent: 80
         growthStep: 2Gi
         maxSize: 10Gi
   ```

1. Apply the configuration:

   ```
   kubectl apply -f deploy/cr.yaml -n <namespace>
   ```

When the Operator changes the storage size, it updates the Custom Resource status as follows:

- adds the `pvc-resize-in-progress` annotation. The annotation contains the timestamp of the resize start and indicates that the resize operation is running. After the resize finishes, the Operator deletes this annotation

- records the new size in the `currentSize` field

- updates the `resizeCount` field

- records any errors in the `lastError` field

- Check the current cluster state:

  ```
  kubectl get ps <cluster-name> -o yaml -n <namespace>
  ```

  Sample output

  ```
  storageAutoscaling:
    datadir-ps-cluster1-mysql-0:
      currentSize: 4194304Ki
      lastResizeTime: "2026-01-23T15:08:59Z"
      resizeCount: 2
  ```

The `storageAutoscaling` section appears under the `.status` in the Custom Resource. See [Custom resource statuses](https://docs.percona.com/percona-operator-for-mysql/1.3.0/cr-statuses.html#storage-autoscaling-status) for field meanings.

When the storage size reaches the limit, no further resizing is done and this event is recorded in the logs. You can either clean up the data or set a new limit based on your organization’s policies and requirements. For help with common issues, see [Operator logs](https://docs.percona.com/percona-operator-for-mysql/1.3.0/debug-logs.html).

#### Storage resizing with Volume Expansion capability

In this document we’re using the default Percona Server for MySQL cluster name `ps-cluster1`. If you have a different name, replace `ps-cluster1` with it in the commands.

To enable storage resizing via volume expansion, do the following:

1. Set the [`storageScaling.enableVolumeScaling`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#storagescalingenablevolumescaling) Custom Resource option to `true` (it is turned off by default). When enabled, the Operator automatically expands storage when you increase the size in the Custom Resource

1. Change the `mysql.volumeSpec.persistentVolumeClaim.resources.requests.storage` option in the `deploy/cr.yaml` file to the desired storage size.

   Here’s the example configuration:

   ```
   spec:
     ...
     storageScaling:
       enableVolumeScaling: true
     mysql:
       ...
       volumeSpec:
         ...
         persistentVolumeClaim:
           resources:
             requests:
               storage: <NEW STORAGE SIZE>
   ```

1. Apply the new configuration:

   ```
   kubectl apply -f cr.yaml
   ```

The storage size change takes some time. When it starts, the Operator automatically adds the `pvc-resize-in-progress` annotation to the `PerconaServerMySQL` Custom Resource. The annotation contains the timestamp of the resize start and indicates that the resize operation is running. After the resize finishes, the Operator deletes this annotation.

#### Manual resizing

To increase the storage size manually, do the following:

1. Extract and backup the cluster configuration

   ```
   kubectl get ps ps-cluster1 -o yaml > CR_backup.yaml
   ```

1. Now you should delete the cluster.

   You can use the following command to delete the cluster:

   ```
   kubectl delete ps ps-cluster1
   ```

1. For each node, edit the yaml to resize the PVC object.

   ```
   kubectl edit pvc datadir-ps-cluster1-mysql-0
   ```

   In the yaml, edit the spec.resources.requests.storage value.

   ```
   spec:
     accessModes:
     - ReadWriteOnce
     resources:
       requests:
         storage: 6Gi
   ```

   Perform the same operation on the other nodes.

   ```
   kubectl edit pvc datadir-ps-cluster1-mysql-1
   kubectl edit pvc datadir-ps-cluster1-mysql-2
   ```

1. In the CR configuration file, use vim or another text editor to edit the PVC size.

   ```
   vim CR_backup.yaml
   ```

1. Set the new storage size for the `mysql.volumeSpec.persistentVolumeClaim.resources.requests.storage` option:

   ```
   mysql:
   volumeSpec:
     persistentVolumeClaim:
       resources:
         requests:
           storage: 6Gi
   ```

   The size of the storage must match the size you defined for the PVC object on the cluster nodes.

1. Apply the updated configuration to the cluster.

   ```
   kubectl apply -f CR_backup.yaml
   ```

The storage size change takes some time. When it starts, the Operator automatically adds the `pvc-resize-in-progress` annotation to the `PerconaServerMySQL` Custom Resource. The annotation contains the timestamp of the resize start and indicates that the resize operation is running. After the resize finishes, the Operator deletes this annotation.

## Horizontal scaling

Size of the cluster is controlled by a [size key](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#mysqlsize) in the [Custom Resource options](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html) configuration. That’s why scaling the cluster needs nothing more but changing this option and applying the updated configuration file. This may be done in a specifically saved config, or on the fly, using the following command:

```
kubectl patch ps ps-cluster1 --type='json' -p='[{"op": "replace", "path": "/spec/mysql/size", "value": 5 }]'
```

In this example we have changed the size of the Percona Server for MySQL Cluster to `5` instances.

The Operator validates `mysql.size` against the cluster type. For **asynchronous** replication, you can scale to 2, 4, 6, or any larger count without extra flags. Scaling to **1** requires [`unsafeFlags.mysqlSize: true`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#unsafeflagsmysqlsize). For **group replication**, keep an odd count between 3 and 9. ,Setting an even count or for more than 9 instances is not recommended and requires setting [`unsafeFlags.mysqlSize: true`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#unsafeflagsmysqlsize).
