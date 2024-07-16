# Check the Events

[Kubernetes Events :octicons-link-external-16:](https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/event-v1/) always provide a wealth of information and should always be checked while troubleshooting issues.

Events can be checked by the following command

```{.bash data-prompt="$"}
$ kubectl get events
```

???+ example "Expected output"

    ``` {.text .no-copy}
    LAST SEEN   TYPE      REASON                   OBJECT                                                MESSAGE
    3s          Normal    Provisioning             persistentvolumeclaim/datadir-cluster1-mysql-2        External provisioner is provisioning volume for claim "default/datadir-cluster1-mysql-2"
    3s          Normal    ProvisioningSucceeded    persistentvolumeclaim/datadir-cluster1-mysql-2        Successfully provisioned volume pvc-fbd347c2-adf7-413b-86bb-b5e381313cc0
    ...
    ```

Events capture many information happening at Kubernetes level and provide valuable information. By default, the ordering of events cannot be guaranteed.
Use the following command to sort the output in a reverse chronological fashion.

```{.bash data-prompt="$"}
$ kubectl get events --sort-by=".lastTimestamp"
```

???+ example "Expected output"

    ``` {.text .no-copy}
    LAST SEEN   TYPE      REASON                   OBJECT                                                MESSAGE
    33m         Warning   FailedScheduling           pod/cluster1-mysql-0                                  0/1 nodes are available: pod has unbound immediate PersistentVolumeClaims. preemption: 0/1 nodes are available: 1 Preemption is not helpful for scheduling.
    33m         Normal    Provisioning               persistentvolumeclaim/datadir-cluster1-mysql-0        External provisioner is provisioning volume for claim "default/datadir-cluster1-mysql-0"
    33m         Normal    ProvisioningSucceeded      persistentvolumeclaim/datadir-cluster1-mysql-0        Successfully provisioned volume pvc-aad3d7cf-2bd4-4823-8e6f-38b9a8528aaa
    ...
    ```

When there are too many events and there is a need of filtering output, tools like [yq :octicons-link-external-16:](https://github.com/mikefarah/yq), [jq :octicons-link-external-16:](https://github.com/jqlang/jq) can be used to filter specific items or know the structure of the events.

Example:

```{.bash data-prompt="$"}
$ kubectl get events -oyaml | yq .items[11]
```

??? example "Expected output"

    ``` {.text .no-copy}
    apiVersion: v1
    count: 1
    eventTime: null
    firstTimestamp: "2024-07-16T08:57:32Z"
    involvedObject:
      apiVersion: v1
      kind: Pod
      name: cluster1-mysql-0
      namespace: default
      resourceVersion: "623"
      uid: 689338c7-d5f7-4bfb-9f7e-ca1d13e782a3
    kind: Event
    lastTimestamp: "2024-07-16T08:57:32Z"
    message: '0/1 nodes are available: pod has unbound immediate PersistentVolumeClaims. preemption: 0/1 nodes are available: 1 Preemption is not helpful for scheduling.'
    metadata:
      creationTimestamp: "2024-07-16T08:57:32Z"
      name: cluster1-mysql-0.17e2a5c04f66588f
      namespace: default
      resourceVersion: "625"
      uid: 6d4a0eeb-8eea-4e1d-91f5-91fb795bd743
    reason: FailedScheduling
    reportingComponent: default-scheduler
    reportingInstance: ""
    source:
      component: default-scheduler
    type: Warning
    ```

Flag `--field-selector` can be used to filter out the output as well.
For example, the following command provides events of Pod only:

```{.bash data-prompt="$"}
$ kubectl get events --field-selector involvedObject.kind=Pod
```

More fields can be added to the field-selector flag for filtering events further. For example, the following command provides events of the `cluster1-mysql-0` Pod:

```{.bash data-prompt="$"}
$ kubectl get events --field-selector involvedObject.kind=Pod,involvedObject.name=cluster1-mysql-0
```

???+ example "Expected output"

    ``` {.text .no-copy}
    LAST SEEN   TYPE      REASON            OBJECT                 MESSAGE
    53m         Normal    Created           pod/cluster1-mysql-0   Created container mysql
    53m         Normal    Started           pod/cluster1-mysql-0   Started container mysql
    53m         Normal    Pulling           pod/cluster1-mysql-0   Pulling image "percona/percona-server-mysql-operator:0.8.0-backup"
    ...
    ```

Save way you can query events for other Kubernetes object (StatefulSet, Custom Resource, etc.) to investigate any problems to them:

```{.bash data-prompt="$"}
$ kubectl get events --field-selector involvedObject.kind=PerconaServerMySQL,involvedObject.name=cluster1
```

???+ example "Expected output"

    ``` {.text .no-copy}
    LAST SEEN   TYPE      REASON                     OBJECT                        MESSAGE
    10m         Warning   AsyncReplicationNotReady   perconaservermysql/cluster1   cluster1-mysql-1: [not_replicating]
    ...
    ```

Alternatively, you can see events for a specific object in the output of `kubectl describe` command:

```{.bash data-prompt="$"}
$ kubectl describe ps cluster1
```

??? example "Expected output"

    ``` {.text .no-copy}
    Name:         cluster1
    ...
    Events:
      Type     Reason                    Age                From           Message
      ----     ------                    ----               ----           -------
      Warning  AsyncReplicationNotReady  10m (x23 over 13m)    ps-controller  cluster1-mysql-1: [not_replicating]
    ...

Check `kubectl get events --help` to know about more options.

!!! note

    It is important to note that events are stored in the [etcd :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/components/#etcd) for only 60 minutes. Ensure that events are checked within 60 minutes of the issue. Kubernetes cluster administrators might also use event exporters for storing the events.

