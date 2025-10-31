# Scale Percona Distribution for MySQL on Kubernetes

One of the great advantages brought by Kubernetes
platform is the ease of an application scaling. Scaling an application
results in adding or removing the Pods and scheduling them to available
Kubernetes nodes.

Scaling can be [vertical](#vertical-scaling) and [horizontal](#horizontal-scaling). Vertical scaling adds more compute or
storage resources to MySQL nodes; horizontal scaling is about adding more
nodes to the cluster. [High availability](architecture.md#high-availability)
looks technically similar, because it also involves additional nodes, but the
reason is maintaining liveness of the system in case of server or network
failures.

## Vertical scaling

### Scale compute resources

The Operator deploys and manages multiple components, such as Percona 
Server for MySQL, Orchestrator, HAProxy or MySQL Router and others. You can manage CPU or memory for every component separately by editing corresponding sections in the Custom Resource. We follow 
the structure for `requests` and `limits` that [Kubernetes provides :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/).

For example, you can add more resources to your HAProxy nodes by editing the
following section in the Custom Resource:

```yaml
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

Use our reference documentation for the [Custom Resource options](operator.md) 
for more details about other components.

### Scale storage

Kubernetes manages storage with a PersistentVolume (PV), a segment of
storage supplied by the administrator, and a PersistentVolumeClaim
(PVC), a request for storage from a user. 

Starting with Kubernetes v1.11, a user can increase the size of an existing
PVC object (considered stable since Kubernetes v1.24).
The user cannot shrink the size of an existing PVC object.

Starting from the Operator version 0.11.0, you can scale Percona Server for MySQL storage automatically by configuring the Custom Resource manifest. Alternatively, you can scale the storage manually. For either way, the volume type must support PVCs expansion.

#### Check expansion capability for your volume type

Certain volume types support PVCs expansion by default.  You can run the following command to check if your storage supports the expansion capability:

``` {.bash data-prompt="$" }
$ kubectl describe sc <storage class name> | grep AllowVolumeExpansion
```

??? example "Expected output"

    ``` {.text .no-copy}
    AllowVolumeExpansion: true
    ```

Find exact details about
PVCs and the supported volume types in [Kubernetes
documentation  :octicons-link-external-16:](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#expanding-persistent-volumes-claims).

#### Storage resizing with Volume Expansion capability

In this document we're using the default Percona Server for MySQL cluster name `ps-cluster1`. If you have a different name, replace `ps-cluster1` with it in the commands.

To enable storage resizing via volume expansion, do the following:

1. Set the [enableVolumeExpansion](operator.md#enablevolumeexpansion) Custom Resource option to `true` (it is turned off by default). When enabled, the Operator will automatically expand the storage for you when you define a new size in the Custom Resource
2. Change the
`mysql.volumeSpec.persistentVolumeClaim.resources.requests.storage` option in the `deploy/cr.yaml` file to the desired storage size.

    Here's the example configuration:

    ```yaml
    spec:
      ...
      enableVolumeExpansion: true
        ...
      mysql:
        ...
        volumeSpec:
          ...
          persistentVolumeClaim:
            resources:
              requests:
                storage: <NEW STORAGE SIZE>
    ```

3. Apply the new configuration:
    
    ``` {.bash data-prompt="$" }
    $ kubectl apply -f cr.yaml
    ```

The storage size change takes some time. When it starts, the Operator automatically adds the `pvc-resize-in-progress` annotation to the `PerconaServerMySQL` Custom Resource. The annotation contains the timestamp of the resize start and indicates that the resize operation is running. After the resize finishes, the Operator deletes this annotation.

#### Manual resizing

To increase the storage size manually, do the following:
{.power-number}

1. Extract and backup the cluster configuration

    ```{.bash data-prompt="$"}
    $ kubectl get ps ps-cluster1 -o yaml > CR_backup.yaml
    ```

2. Now you should delete the cluster.

    <!-- UNCOMMENT THIS WHEN FINALIZERS GET WORKING
    warning Make sure that :ref:`delete-pxc-pvc<finalizers-pxc>` finalizer
    is not set in your custom resource, **otherwise
    all cluster data will be lost!** -->
    You can use the following command to delete the cluster:

    ```{.bash data-prompt="$"}
    $ kubectl delete ps ps-cluster1
    ```

3. For each node, edit the yaml to resize the PVC object.

    ```{.bash data-prompt="$"}
    $ kubectl edit pvc datadir-ps-cluster1-mysql-0
    ```

    In the yaml, edit the spec.resources.requests.storage value.

    ```yaml
    spec:
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 6Gi
    ```

    Perform the same operation on the other nodes.

    ```{.bash data-prompt="$"}
    $ kubectl edit pvc datadir-ps-cluster1-mysql-1
    $ kubectl edit pvc datadir-ps-cluster1-mysql-2
    ```

4. In the CR configuration file, use vim or another text editor to edit
    the PVC size. 

    ```{.bash data-prompt="$"}
    $ vim CR_backup.yaml
    ```

5. Set the new storage size for the `mysql.volumeSpec.persistentVolumeClaim.resources.requests.storage` option:

    ```yaml
    mysql:
    volumeSpec:
      persistentVolumeClaim:
        resources:
          requests:
            storage: 6Gi
    ```

    The size of the storage must match the size you defined for the PVC object on the cluster nodes.

6. Apply the updated configuration to the cluster.

    ```{.bash data-prompt="$"}
    $ kubectl apply -f CR_backup.yaml
    ```

The storage size change takes some time. When it starts, the Operator automatically adds the `pvc-resize-in-progress` annotation to the `PerconaServerMySQL` Custom Resource. The annotation contains the timestamp of the resize start and indicates that the resize operation is running. After the resize finishes, the Operator deletes this annotation. 

## Horizontal scaling

Size of the cluster is controlled by a [size key](operator.md#mysqlsize) in the
[Custom Resource options](operator.md)
configuration. That’s why scaling the cluster needs nothing more but changing
this option and applying the updated configuration file. This may be done in a
specifically saved config, or on the fly, using the following command:

```{.bash data-prompt="$"}
$ kubectl patch ps ps-cluster1 --type='json' -p='[{"op": "replace", "path": "/spec/mysql/size", "value": 5 }]'
```

In this example we have changed the size of the Percona Server for MySQL
Cluster to `5` instances.

