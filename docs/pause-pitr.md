# Pause a point-in-time recovery

To debug a [point-in-time recovery](backups-restore-pitr.md), pause it after the base backup is restored and before the binary logs are applied. Use this only for debugging, not for regular restores. If the recovery fails, see [Point-in-time recovery](debug-backup-restore.md#point-in-time-recovery) in Troubleshoot backups and restores.

The restore Job creates the [`sleep-forever`](datadir-special-files.md#sleep-forever) file on the restored data directory and waits until you remove it.

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
