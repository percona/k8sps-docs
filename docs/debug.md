# Initial troubleshooting

Percona Operator for MySQL uses [Custom Resources :octicons-link-external-16:](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) to manage options for the various components of the cluster.

* `PerconaServerMySQL` Custom Resource with Percona Server for MySQL cluster options (it has handy `ps` shortname also),

* `PerconaServerMySQLBackup` and `PerconaServerMySQLRestore` Custom Resources contain options for Percona XtraBackup used to backup Percona Server for MySQL and to restore it from backups (`ps-backup` and `ps-restore` shortnames are available for them).

The first thing you can check for the Custom Resource is to query it with `kubectl get` command:


``` {.bash data-prompt="$" }
$ kubectl get ps
```

??? example "Expected output"

    ``` {.text .no-copy}
    NAME       REPLICATION         ENDPOINT                   STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
    cluster1   group-replication   cluster1-haproxy.default   ready   3                                3        20m
    ```

The Custom Resource should have `ready` state.

!!! note

    You can check which Percona’s Custom Resources are present and get some information about them as follows:

    ``` {.bash data-prompt="$" }
    $ kubectl api-resources | grep -i percona
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

``` {.bash data-prompt="$" }
$ kubectl get pods
```

???+ example "Expected output"

    --8<-- "./docs/assets/code/kubectl-get-pods-response.txt"

The above command provides the following insights:

* `READY` indicates how many containers in the Pod are ready to serve the
    traffic. In the above example, `cluster1-haproxy-0` container has all two
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

``` {.bash data-prompt="$" }
$ kubectl describe pods cluster1-mysql-0
```

??? example "Expected output"

    ``` {.text .no-copy}
    ...
    Name:         cluster1-mysql-0
    Namespace:    default
    ...
    Controlled By:  StatefulSet/cluster1-mysql
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
