# Delete unneeded backups

You can delete backups in the following ways:

* Configure the retention policy for full backups and have the Operator delete them according to this policy rules.
* Delete backups of any type manually. However, deleting incremental backups has rules. To learn more, see [Deleting incremental backup chains](#deleting-incremental-backup-chains).

## How the Operator handles backup deletion

The `percona.com/delete-backup` [Kubernetes finalizer](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#finalizers) defined within a `PerconaServerMySQLBackup` backup object controls its deletion lifecycle. This is done to prevent orphaned backup data.

**How it works**:

* To start a backup, the Operator creates a backup object. Scheduled backups include the `percona.com/delete-backup` finalizer in the `metadata.finalizers` section by default. For on-demand backups, you can choose to add or remove this finalizer during configuration. This finalizer controls whether the Operator cleans up the backup data from the storage before deletion.
* While the finalizer is present, Kubernetes does not fully remove the `PerconaServerMySQLBackup` object after a delete request. The resource stays until every finalizer is cleared.
* After you run `kubectl delete ps-backup …`, the Operator marks the specified backup object for deletion  by setting the `metadata.deletionTimestamp` value. The Operator’s backup controller sees this and, if `percona.com/delete-backup` finalizer is listed, deletes backup data in a remote storage.
* When cleanup finishes, the Operator removes the `percona.com/delete-backup` finalizer. Kubernetes then completes deletion of the backup resource.

You can force the deletion of a backup by manually removing the `percona.com/delete-backup` finalizer from the backup object. Be aware that doing this bypasses the Operator's cleanup steps and may leave backup data or resources orphaned. Only do this if you fully understand the consequences and are certain it is safe.

## Configure retention for full scheduled backups 

In the cluster Custom Resource, each entry under `backup.schedule`  with the type `full` can include an optional `keep` field. This field specifies how many most recent successful backups of that schedule to keep. When the count exceeds the `keep` value, the Operator deletes older backup objects.

| Setting | Behavior |
| ------- | -------- |
| `keep: N` (positive integer) | Keep the **N** newest backups for that schedule; older ones are removed automatically. |
| `keep: 0` or **omit** `keep` | **No automatic deletion** for that schedule. Backups accumulate until you delete them manually. |

Configure schedules in the [`deploy/cr.yaml` :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml) as described in [Make scheduled backups](backups-scheduled.md). 

This example configuration instructs the Operator to keep the last three full backups from a weekly job:

```yaml
backup:
  schedule:
    - name: "weekly-full-backup"
      schedule: "0 2 * * 0"
      type: "full"
      keep: 3
      storageName: s3-us-west
```

See also [`backup.schedule.keep`](operator.md#backupschedulekeep) in the Custom Resource reference.

### Full vs incremental backup schedules

* Retention policy applies to **scheduled full backups** in the usual way: the Operator keeps only the specified number of newest full backups for that schedule. Note that retention is subject to the [limitations when multiple schedules share one storage](backups-scheduled.md#managing-multiple-backup-schedules-in-the-same-storage).
* **For scheduled incremental backups**, `keep` is ignored. There is no automatic retention that trims old increments. You can delete **only the latest increment** or **the whole chain** by deleting the base full backup.

## Deleting incremental backup chains

Incremental backups depend on a **chain**: one **full** backup plus **increments** on the same storage. See [Incremental backups](backups-incremental.md) for how chains are built.

Retention works differently than for standalone full backups, if the `percona.com/delete-backup` finalizer exists in the backup object:

* **Deleting the base full backup** removes the **entire** incremental chain that derives from it (the Operator does not leave orphaned increments).
* You **cannot** delete an increment **in the middle** of a chain as that would break continuity. You may delete only:
  
  * the **last** increment in the chain (the tip), or  
  * the **full** backup at the base (which removes the whole chain).

If you use scheduled incremental jobs, plan cleanup: either rotate by deleting the **latest** increment when appropriate, or delete the **base** full backup when you want to drop the whole chain and start fresh (after taking a new full backup, if you still need recovery points).

## Delete a backup manually

1. List backups in the namespace:

    ```bash
    kubectl get ps-backup -n <namespace>
    ```

2. When you know the name, delete the `PerconaServerMySQLBackup` object:

    ```bash
    kubectl delete ps-backup <backup-name> -n <namespace>
    ```

The Operator reconciles storage and related objects for that backup. For **incremental** backups, follow the [chain rules](#deleting-incremental-backup-chains) above: prefer deleting `ps-backup` objects that represent the last increment or the base full backup.
