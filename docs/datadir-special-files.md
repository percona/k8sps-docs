# Special files in the data directory

The `mysql` container of every MySQL Pod checks for several marker files in its data directory, `/var/lib/mysql`. When one of these files exists, the container, its probes, or the Operator change their behavior. For example, the container may not start `mysqld`, or the Pod may skip joining the cluster.

The data directory is on the Pod's Persistent Volume. So these files stay in place when the Pod or the container restarts. They are removed only when you or the Operator delete them.

!!! tip "Use another container if `mysql` keeps crashing"

    The commands on this page use the `mysql` container (`-c mysql`). If this container crashes or restarts in a loop, `kubectl exec` into it can fail. The `xtrabackup` and `logs` containers of the same Pod mount the same data volume at `/var/lib/mysql`, so you can run the commands there instead. The `xtrabackup` container exists when backups are enabled (`backup.enabled`), and the `logs` container exists when [persistent logging](persistent-logging.md) is enabled (`logcollector.enabled`). For example:

    ```bash
    kubectl exec <cluster-name>-mysql-<N> -n <namespace> -c xtrabackup -- touch /var/lib/mysql/sleep-forever
    ```

This page describes:

* [files you can create or remove](#files-you-can-create-or-remove) to debug a Pod: `sleep-forever` and `no-bootstrap`, and the `full-cluster-crash` file that the Operator creates
* the [`percona.com/pitr-sleep-forever` annotation](#pause-a-point-in-time-recovery) to pause a point-in-time recovery
* [files that the Operator manages](#files-managed-by-the-operator), which you must leave alone

## How the files affect the MySQL Pod

Three components of the `mysql` container read the files:

* The entry point script runs when the container starts and then starts `mysqld`.
* The startup probe (`/opt/percona/bootstrap`) configures replication. It clones data from another member if needed and adds the Pod to the cluster.
* The liveness and readiness probes (`/opt/percona/healthcheck`) report the health of `mysqld` to Kubernetes.

The following table shows what each file changes:

| File | `mysqld` runs | Startup probe (clone, join the cluster) | Liveness and readiness probes |
| ---- | ------------- | --------------------------------------- | ----------------------------- |
| `sleep-forever` | No | Skipped | Always pass |
| `no-bootstrap` | Yes, in read-only mode | Skipped | Always pass |
| `full-cluster-crash` | Yes, in read-only mode | Skipped | Liveness always passes. Readiness passes as soon as `mysqld` is ready |

## Files you can create or remove

### `sleep-forever`

Use this file to stop a MySQL Pod from starting `mysqld`, while keeping the container running so that you can exec into it. It works for both asynchronous replication and Group Replication.

**What it does**

The entry point script checks for the file when the container starts, before it starts `mysqld`. If the file exists, the script prints the following messages to the container log and doesn't start `mysqld`:

``` {.text .no-copy}
The /var/lib/mysql/sleep-forever file is detected, node is going to infinity loop
If you want to exit from infinity loop you need to remove /var/lib/mysql/sleep-forever file
```

The script then checks every 3 seconds if the file still exists. When you remove the file, the script exits, and Kubernetes restarts the container. The container then starts as usual.

While the file exists, the startup, liveness, and readiness probes pass right away. The Pod doesn't clone data, join the cluster, or configure replication.

**Who creates or removes it**

You do. The Operator doesn't create this file for MySQL Pods, with one exception: a [paused point-in-time recovery](#pause-a-point-in-time-recovery) creates it on the data volume of the `<cluster-name>-mysql-0` Pod. The [`clusterset-recovery` file](#files-managed-by-the-operator) removes `sleep-forever` from a Pod.

**How to use it**

Creating the file in a running container doesn't stop `mysqld`. It only turns off the probes and the startup bootstrap for this Pod. The container stops before `mysqld` the next time it starts. See [Pause a MySQL Pod for debugging](#pause-a-mysql-pod-for-debugging) for the steps.

Because the readiness probe passes right away, you can also use the file to [unblock a rolling update](#unblock-a-stuck-rolling-update) that waits for an unready Pod.

!!! warning

    * A Pod with the `sleep-forever` file reports `Ready` even though `mysqld` isn't running, because the readiness probe always passes. Kubernetes Services that select `Ready` Pods may list this Pod. Clients that connect to it fail.
    * A rolling update treats this Pod as updated as soon as it reports `Ready` and continues to the next Pod, even though this Pod doesn't run `mysqld`. The cluster has one less working member until you remove the file.

### `no-bootstrap`

Use this file when `mysqld` must run, for example to run SQL statements by hand, but the startup probe must not clone data, join the cluster, or configure replication, and the liveness probe must not restart the container if `mysqld` stops responding. The file doesn't stop the Operator or Orchestrator from managing the cluster. It works for both asynchronous replication and Group Replication.

**What it does**

The entry point script ignores this file, so `mysqld` starts as usual. The probes check the file:

* The startup probe exits right away. The Pod doesn't clone data, join the cluster or the group, or configure replication.
* The liveness and readiness probes always pass. Kubernetes doesn't restart the container because of failed probes. If the `mysqld` process exits, the container still restarts.

**Who creates or removes it**

You do. The Operator neither creates nor removes this file for MySQL Pods.

**How to use it**

1. Create the file:

    ```bash
    kubectl exec <cluster-name>-mysql-<N> -n <namespace> -c mysql -- touch /var/lib/mysql/no-bootstrap
    ```

2. Delete the Pod so that it starts again with the file in place:

    ```bash
    kubectl delete pod <cluster-name>-mysql-<N> -n <namespace>
    ```

3. Do your work in the Pod.

4. Remove the file:

    ```bash
    kubectl exec <cluster-name>-mysql-<N> -n <namespace> -c mysql -- rm /var/lib/mysql/no-bootstrap
    ```

5. Delete the Pod again. The startup probe runs only when the container starts, so the Pod rejoins the cluster only after a restart:

    ```bash
    kubectl delete pod <cluster-name>-mysql-<N> -n <namespace>
    ```

!!! warning

    A Pod with the `no-bootstrap` file reports `Ready` even if `mysqld` doesn't work.

### `full-cluster-crash`

This file is used only in clusters with Group Replication. It marks a Pod that waits for recovery after a [full cluster crash](crash-recovery.md).

**Who creates or removes it**

The startup probe creates the file when it decides that the group must be rebooted with the `dba.rebootClusterFromCompleteOutage()` command. For example, it does so when the Pod can't reach any other member of the cluster, or when the cluster has no `ONLINE` primary. The file contains the `GTID_EXECUTED` value of the Pod. After that, the container restarts.

The Operator removes the file from every Pod when it recovers the cluster automatically. If [automatic recovery](crash-recovery.md#recover-the-cluster-automatically) is turned off, you remove the file yourself as part of the [manual recovery](crash-recovery.md#recover-the-cluster-manually).

**What it does**

While the file exists:

* The entry point script starts `mysqld` in read-only mode. It prints the `GTID_EXECUTED` value of the Pod and the recovery instructions between the `######FULL_CLUSTER_CRASH:<Pod name>######` lines in the container log.
* The startup probe exits right away.
* The liveness probe always passes. The readiness probe passes as soon as `mysqld` is ready, without checking the Group Replication membership. This lets all Pods become `Ready`, so that the Operator can start the recovery.
* The Operator sets the cluster `status.state` to `error` with the `FullClusterCrashDetected` condition reason and records the `FullClusterCrashDetected` event.

See [Recover from a full cluster crash](crash-recovery.md) for how to recover the cluster.

!!! warning

    Remove the file from **every** Pod after the cluster is recovered. If you leave it on a Pod, that Pod starts `mysqld` in read-only mode and skips joining the cluster every time it restarts.

## Pause a MySQL Pod for debugging

Use the `sleep-forever` file to keep a MySQL Pod running without `mysqld`. This helps when `mysqld` crashes at startup and the container restarts in a loop, or when you need to inspect, repair, or copy files from the data directory while `mysqld` is stopped.

1. Create the file in the `mysql` container of the Pod:

    ```bash
    kubectl exec <cluster-name>-mysql-<N> -n <namespace> -c mysql -- touch /var/lib/mysql/sleep-forever
    ```

    If the `mysql` container restarts too often to run the command, run it in the `xtrabackup` or `logs` container instead. See [the tip above](#special-files-in-the-data-directory). The file is on the Persistent Volume, so it stays in place after the next restart.

2. Delete the Pod. Kubernetes recreates it, and the container stops before starting `mysqld`:

    ```bash
    kubectl delete pod <cluster-name>-mysql-<N> -n <namespace>
    ```

3. Check the container log for the `node is going to infinity loop` message:

    ```bash
    kubectl logs <cluster-name>-mysql-<N> -n <namespace> -c mysql
    ```

4. Open a shell in the container and do your work. The data directory is available in `/var/lib/mysql`:

    ```bash
    kubectl exec -it <cluster-name>-mysql-<N> -n <namespace> -c mysql -- bash
    ```

5. Remove the file to resume the Pod:

    ```bash
    kubectl exec <cluster-name>-mysql-<N> -n <namespace> -c mysql -- rm /var/lib/mysql/sleep-forever
    ```

    In a few seconds, the container exits and Kubernetes restarts it. The container then starts `mysqld`, and the Pod rejoins the cluster.

## Unblock a stuck rolling update

When you change the Custom Resource or upgrade the database, the MySQL Pods restart one by one with the new configuration. Both the `SmartUpdate` and the `RollingUpdate` [update strategies](operator.md#updatestrategy) restart the next Pod only when all MySQL Pods are `Ready`. If one Pod is stuck in the unready state, for example because `mysqld` can't join the cluster, the update stops and waits for this Pod. The update may be the fix for the Pod, but it never reaches the Pod.

The `sleep-forever` file makes the readiness probe pass right away, so the update can continue:

1. Find the Pod that isn't `Ready`:

    ```bash
    kubectl get pods -n <namespace> -l app.kubernetes.io/component=mysql
    ```

2. Create the file in the `mysql` container of this Pod:

    ```bash
    kubectl exec <cluster-name>-mysql-<N> -n <namespace> -c mysql -- touch /var/lib/mysql/sleep-forever
    ```

    The Pod becomes `Ready` with the next readiness probe, without a restart. The update continues. When it reaches this Pod, the Pod is recreated with the new configuration and doesn't start `mysqld`.

3. Check that the Pod runs the new configuration. The two commands print the same value when it does:

    ```bash
    kubectl get pod <cluster-name>-mysql-<N> -n <namespace> -o jsonpath='{.metadata.labels.controller-revision-hash}'
    kubectl get sts <cluster-name>-mysql -n <namespace> -o jsonpath='{.status.updateRevision}'
    ```

4. Remove the file right away:

    ```bash
    kubectl exec <cluster-name>-mysql-<N> -n <namespace> -c mysql -- rm /var/lib/mysql/sleep-forever
    ```

    The container restarts, starts `mysqld` with the new configuration, and the Pod rejoins the cluster.

!!! warning

    Remove the file as soon as the Pod runs the new configuration. With the `SmartUpdate` strategy, the Operator updates the primary Pod last. Before that, it switches the primary role to the first `Ready` secondary Pod. The Operator may choose the Pod with the `sleep-forever` file, and the switchover fails because `mysqld` doesn't run there.

## Pause a point-in-time recovery

To debug a [point-in-time recovery](backups-restore-pitr.md), you can pause it after the base backup is restored, but before the binary logs are applied. Use this only for debugging, not for regular restores.

1. Add the `percona.com/pitr-sleep-forever` annotation to the `PerconaServerMySQLRestore` object. The Operator checks only if the annotation exists, not its value:

    ```yaml
    apiVersion: ps.percona.com/v1
    kind: PerconaServerMySQLRestore
    metadata:
      name: restore-pitr
      annotations:
        percona.com/pitr-sleep-forever: "true"
    spec:
      clusterName: ps-cluster1
      backupName: backup1
      pitr:
        type: date
        date: "2026-03-20 09:15:00"
    ```

2. Apply the object. The point-in-time recovery Job starts a temporary `mysqld` on the restored data directory, creates the `/var/lib/mysql/sleep-forever` file, and waits.

3. Find the Pod of the restore Job. The Job is named `pitr-restore-<restore-name>`. Exec into the Pod to inspect the restored data:

    ```bash
    kubectl get pods -n <namespace> -l job-name=pitr-restore-<restore-name>
    kubectl exec -it <restore-pod-name> -n <namespace> -- bash
    ```

4. Remove the file when you are done:

    ```bash
    kubectl exec <restore-pod-name> -n <namespace> -- rm /var/lib/mysql/sleep-forever
    ```

!!! warning

    When you remove the file, the container exits **without applying the binary logs**. The restore still reports `Succeeded`, and the Operator starts the cluster with only the data from the base backup, not the data up to your recovery target. Keep your applications away from the cluster, and run the point-in-time recovery again without the annotation. The new restore overwrites any changes made in the meantime.

!!! warning

    The restore Job uses the data volume of the `<cluster-name>-mysql-0` Pod, so the `sleep-forever` file is created on this volume. Always end the pause by removing the file. If you delete the restore object or the Job instead, remove `/var/lib/mysql/sleep-forever` from the `<cluster-name>-mysql-0` Pod afterwards. Otherwise this Pod doesn't start `mysqld`.

## Files managed by the Operator

You may see the following files in `/var/lib/mysql`. The Operator and its tools create and use them. Don't create, edit, or delete them. The Version column shows the Operator version that added the file. "All" means the file is used in all versions covered by this documentation.

| File | Version | Purpose |
| ---- | ------- | ------- |
| `server-id` | 1.3.0 | Stores the `server_id` of this data directory. **Don't delete it.** Without it, `mysqld` gets a different `server_id` that is based on the Pod number. This can make replication skip transactions without any error. |
| `clusterset-recovery` | 1.2.0 | The Operator creates it when it removes a Group Replication cluster from a ClusterSet. While it exists, the Operator doesn't start the full cluster crash recovery. The next time the startup probe runs, it removes this file and also the `sleep-forever`, `no-bootstrap`, and `full-cluster-crash` files. **Don't create it by hand**, or you lose these files. |
| `bootstrap.lock` | All | Exists while the entry point script initializes the data directory. Starting with version 1.3.0, it also exists while the script updates the system users. The startup probe waits until it is removed. |
| `clone.lock` | All | Created by the startup probe in clusters with asynchronous replication after the Pod clones data from another member, before the container restarts. The startup probe removes it on the next start. |
| `cr-version` | 1.3.0 | Stores the version of the Custom Resource. When it changes, the entry point script updates the system users and their grants. |
| `failover.lock` | 1.3.0 | Used during a failover in clusters with asynchronous replication, so that only one failover runs at a time. Don't open or lock it with other tools. This makes the failover fail. |
| `mysql.state`, `notify.sock` | All | Report the state of `mysqld` to the probes. |
| `source-logs/` | 1.3.0 | Binary logs fetched from the failed primary during a failover in clusters with asynchronous replication. |

### Log files

The following files contain logs that help you troubleshoot a Pod. You can read them safely:

* `bootstrap.log` - the log of the startup probe
* `mysql-state-monitor.log` - the log of the tool that tracks the `mysqld` state
* `pre-stop.log` - the log of the pre-stop hook
* `failover.log` - the log of failover workers in clusters with asynchronous replication, starting with version 1.3.0
* `log/` - the directory for [persistent logs](persistent-logging.md), starting with version 1.3.0

For example:

```bash
kubectl exec <cluster-name>-mysql-<N> -n <namespace> -c mysql -- cat /var/lib/mysql/bootstrap.log
```
