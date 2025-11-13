# Initial troubleshooting

Percona Operator for MySQL uses [Custom Resources :octicons-link-external-16:](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) to manage options for the various components of the cluster.

* `PerconaServerMySQL` Custom Resource with Percona Server for MySQL cluster options (it has handy `ps` shortname also),

* `PerconaServerMySQLBackup` and `PerconaServerMySQLRestore` Custom Resources contain options for Percona XtraBackup used to backup Percona Server for MySQL and to restore it from backups (`ps-backup` and `ps-restore` shortnames are available for them).

The first thing you can check for the Custom Resource is to query it with `kubectl get` command:


```bash
kubectl get ps
```

??? example "Expected output"

    ``` {.text .no-copy}
    NAME       REPLICATION         ENDPOINT                   STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
    ps-cluster1   group-replication   ps-cluster1-haproxy.default   ready   3                                3        20m
    ```

The Custom Resource should have `ready` state.

!!! note

    You can check which Percona’s Custom Resources are present and get some information about them as follows:

    ```bash
    kubectl api-resources | grep -i percona
    ```

    ??? example "Expected output"

        ``` {.text .no-copy}
        perconaservermysqlbackups         ps-backup,ps-backups   ps.percona.com/v1alpha1                true         PerconaServerMySQLBackup
        perconaservermysqlrestores        ps-restore             ps.percona.com/v1alpha1                true         PerconaServerMySQLRestore
        perconaservermysqls               ps                     ps.percona.com/v1alpha1                true         PerconaServerMySQL
        ```

## Check the Pods

If Custom Resource is not getting `ready` state, it makes sense to check
individual Pods. You can do it as follows:

```bash
kubectl get pods
```

??? example "Expected output"

    ``` {.text .no-copy}
    NAME                                            READY   STATUS    RESTARTS      AGE
    cluster1-haproxy-0                              2/2     Running   0             44m
    cluster1-haproxy-1                              2/2     Running   0             44m
    cluster1-haproxy-2                              2/2     Running   0             44m
    cluster1-mysql-0                                3/3     Running   0             46m
    cluster1-mysql-1                                3/3     Running   2 (44m ago)   45m
    cluster1-mysql-2                                3/3     Running   2 (42m ago)   43m
    cluster1-orc-0                                  2/2     Running   0             46m
    cluster1-orc-1                                  2/2     Running   0             45m
    cluster1-orc-2                                  2/2     Running   0             44m
    percona-server-mysql-operator-7c984f7c9-mgwh4   1/1     Running   0             47m
    ```

The above command provides the following insights:

* `READY` indicates how many containers in the Pod are ready to serve the
    traffic. In the above example, `ps-cluster1-haproxy-0` container has all two
    containers ready (2/2). For an application to work properly, all containers
    of the Pod should be ready.
* `STATUS` indicates the current status of the Pod. The Pod should be in a
    `Running` state to confirm that the application is working as expected. You
    can find out other possible states in the [official Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase).
* `RESTARTS` indicates how many times containers of Pod were restarted. This is
    impacted by the [Container Restart Policy :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy).
    In an ideal world, the restart count would be zero, meaning no issues from
    the beginning. If the restart count exceeds zero, it may be reasonable to
    check why it happens.
* `AGE`: Indicates how long the Pod is running. Any abnormality in this value
    needs to be checked.

You can find more details about a specific Pod using the
`kubectl describe pods <pod-name>` command.

```bash
kubectl describe pods ps-cluster1-mysql-0
```

??? example "Expected output"

    ``` {.text .no-copy}
    ...
    Name:         ps-cluster1-mysql-0
    Namespace:    default
    ...
    Controlled By:  StatefulSet/ps-cluster1-mysql
    Init Containers:
     mysql-init:
    ...
    Containers:
     mysql:
    ...
       Restart Count:  0
       Limits:
         memory:  2G
       Requests:
         memory:   2G
       Liveness:   exec [/opt/percona/healthcheck liveness] delay=15s timeout=30s period=10s #success=1 #failure=3
       Readiness:  exec [/opt/percona/healthcheck readiness] delay=30s timeout=3s period=5s #success=1 #failure=3
       Startup:    exec [/opt/percona/bootstrap] delay=15s timeout=300s period=10s #success=1 #failure=1
       Environment:
    ...
       Mounts:
    ...
    Volumes:
    ...
    Events:                      <none>
    ```

This gives a lot of information about containers, resources, container status
and also events. So, describe output should be checked to see any abnormalities.
