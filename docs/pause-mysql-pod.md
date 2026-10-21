# Pause a MySQL Pod

Use the `sleep-forever` file in `/var/lib/mysql` when you need the MySQL container to stay up without `mysqld`, or when an unready Pod must report `Ready` so a rolling update can continue. See [`sleep-forever`](datadir-special-files.md#sleep-forever) for what the file changes.

!!! tip "Use another container if `mysql` keeps crashing"

    The commands on this page use the `mysql` container (`-c mysql`). If this container crashes or restarts in a loop, `kubectl exec` into it can fail. The `xtrabackup` and `logs` containers of the same Pod mount the same data volume at `/var/lib/mysql`, so you can run the commands there instead. The `xtrabackup` container exists when backups are enabled (`backup.enabled`), and the `logs` container exists when [persistent logging](persistent-logging.md) is enabled (`logcollector.enabled`). For example:

    ```bash
    kubectl exec <cluster-name>-mysql-<N> -n <namespace> -c xtrabackup -- touch /var/lib/mysql/sleep-forever
    ```

## Pause a Pod for debugging

Use the `sleep-forever` file to keep a MySQL Pod running without `mysqld`. This helps when `mysqld` crashes at startup and the container restarts in a loop, or when you need to inspect, repair, or copy files from the data directory while `mysqld` is stopped.

1. Create the file in the `mysql` container of the Pod:

    ```bash
    kubectl exec <cluster-name>-mysql-<N> -n <namespace> -c mysql -- touch /var/lib/mysql/sleep-forever
    ```

    If the `mysql` container restarts too often to run the command, run it in the `xtrabackup` or `logs` container instead. Those containers mount the same data volume. The file is on the Persistent Volume, so it stays in place after the next restart.

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
