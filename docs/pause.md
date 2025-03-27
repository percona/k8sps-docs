# Pause/resume the cluster

There may be external situations when it is needed to shutdown the Percona
Server for MySQL cluster for a while and then start it back up (some works
related to the maintenance of the enterprise infrastructure, etc.).

The `deploy/cr.yaml` file contains a special `spec.pause` key for this.
Setting it to `true` gracefully stops the cluster:

```yaml
spec:
  .......
  pause: true
```

Pausing the cluster may take some time, and when the process is over, you will
see only the Operator Pod running:

``` {.bash data-prompt="$" }
$ kubectl get pods
NAME                                             READY   STATUS    RESTARTS   AGE
percona-server-mysql-operator-7ff9cff46f-6dtgs   1/1     Running   0          9m19s
```

To start the cluster after it was shut down just revert the `spec.pause` key
to `false`.

Starting the cluster will take time. The process is over when all Pods have
reached their Running status:

``` {.text .no-copy}
NAME                                             READY   STATUS    RESTARTS   AGE
cluster1-mysql-0                                 2/2     Running   0          3m43s
cluster1-mysql-1                                 2/2     Running   0          3m3s
cluster1-mysql-2                                 2/2     Running   0          2m27s
cluster1-router-c89b8487-bbtqm                   1/1     Running   0          89s
cluster1-router-c89b8487-cll6l                   1/1     Running   0          89s
cluster1-router-c89b8487-q6mnl                   1/1     Running   0          89s
percona-server-mysql-operator-7ff9cff46f-6dtgs   1/1     Running   0          13m
```

!!! note

    Clusters with Group Replication undergo crash recovery on each unpause. This is caused by the specifics of Group Replication, which supposes continuous availability of the database service by design. See [upstream documentation :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/group-replication-restarting-group.html) for more details.
