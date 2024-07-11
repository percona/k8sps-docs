# Scale Percona Distribution for MySQL on Kubernetes

One of the great advantages brought by Kubernetes
platform is the ease of an application scaling. Scaling an application
results in adding or removing the Pods and scheduling them to available
Kubernetes nodes.

Scaling can be vertical and horizontal. Vertical scaling adds more compute or
storage resources to Percona Server for MySQL nodes; horizontal scaling is about adding more
nodes to the cluster. [High availability](architecture.md#high-availability)
looks technically similar, because it also involves additional nodes, but the
reason is maintaining liveness of the system in case of server or network
failures.

## Vertical scaling

### Scale compute

There are multiple components that Operator deploys and manages: Percona 
Server for MySQL, Orchestrator, HAProxy or MySQL Router, etc. To add or reduce CPU or Memory 
you need to edit corresponding sections in the Custom Resource. We follow 
the structure for `requests` and `limits` that Kubernetes [provides :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/).

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
(PVC), a request for storage from a user. In Kubernetes v1.11 the
feature was added to allow a user to increase the size of an existing
PVC object. The user cannot shrink the size of an existing PVC object.
Certain volume types support, by default, expanding PVCs (details about
PVCs and the supported volume types can be found in [Kubernetes
documentation :octicons-link-external-16:](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#expanding-persistent-volumes-claims))

The following are the steps to increase the size:

1. Extract and backup the yaml file for the cluster

    ```{.bash data-prompt="$"}
    kubectl get ps cluster1 -o yaml --export > CR_backup.yaml
    ```

2. Now you should delete the cluster.

    <!-- UNCOMMENT THIS WHEN FINALIZERS GET WORKING
    warining Make sure that :ref:`delete-pxc-pvc<finalizers-pxc>` finalizer
    is not set in your custom resource, **otherwise
    all cluster data will be lost!** -->
    You can use the following command to delete the cluster:

    ```{.bash data-prompt="$"}
    $ kubectl delete -f CR_backup.yaml
    ```

3. For each node, edit the yaml to resize the PVC object.

    ```{.bash data-prompt="$"}
    $ kubectl edit pvc datadir-cluster1-mysql-0
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
    $ kubectl edit pvc datadir-cluster1-mysql-1
    $ kubectl edit pvc datadir-cluster1-mysql-2
    ```

4. In the CR configuration file, use vim or another text editor to edit
    the PVC size.

    ```{.bash data-prompt="$"}
    $ vim CR_backup.yaml
    ```

5. Apply the updated configuration to the cluster.

    ```{.bash data-prompt="$"}
    $ kubectl apply -f CR_backup.yaml
    ```

## Horizontal scaling

Size of the cluster is controlled by a [size key](operator.md#mysqlsize) in the
[Custom Resource options](operator.md)
configuration. That’s why scaling the cluster needs nothing more but changing
this option and applying the updated configuration file. This may be done in a
specifically saved config, or on the fly, using the following command:

```{.bash data-prompt="$"}
$ kubectl patch ps cluster1 --type='json' -p='[{"op": "replace", "path": "/spec/mysql/size", "value": 5 }]'
```

In this example we have changed the size of the Percona Server for MySQL
Cluster to `5` instances.

