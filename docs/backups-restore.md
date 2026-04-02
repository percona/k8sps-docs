# Restore the cluster from a previously saved backup

You can restore from a backup as follows:

* On the same Kubernetes cluster and in the same namespace where you made the backup
* On a [new cluster deployed in a different Kubernetes-based environment](backups-restore-to-new-cluster.md).

This document focuses on the restore to the same cluster.

## Restore scenarios

## Restore scenarios

Select how you wish to restore:

* [Without point-in-time recovery](#restore-from-a-backup-without-point-in-time-recovery)
* [Make a point-in-time recovery](#restore-with-point-in-time-recovery)

To restore from a backup, you create a Restore object using a special restore configuration file. The example of such file is [deploy/backup/restore.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/restore.yaml). 

You can check available options in the [restore options reference](restore-cr.md).
  
## Before you begin

To restore from a backup on the same cluster and namespace, do the following:

1. Export the namespace as an environment variable. Replace the `<namespace>` placeholder with your value:

    ```bash
    export NAMESPACE = <namespace>
    ```

2. Make sure that the cluster is running. Use this command to check it:

    ```bash
    kubectl get ps <cluster-name> -n $NAMESPACE
    ```

3. List backups with the following command:

    ```bash
    kubectl get ps-backup -n $NAMESPACE
    ```

## Restore from a backup without point-in-time recovery

When the correct names for the backup and the cluster are known,configure the `PerconaServerMySQLRestore` Custom Resource. Specify the following keys:

* set `spec.clusterName` key to the name of the target cluster to restore the backup on
* set `spec.backupName` key to the name of your backup. This is the value from the output of the `kubectl get ps-backup` command.

Pass this information to the Operator

=== "via the YAML manifest"

    1. Edit the `deploy/backup/restore.yaml` file:
       
        ```yaml
        apiVersion: ps.percona.com/v1
        kind: PerconaServerMySQLRestore
        metadata:
          name: restore1
        spec: 
          clusterName: ps-cluster1
          backupName: backup1
        ```
        
    2. Start the restore process:

        ```bash
        kubectl apply -f deploy/backup/restore.yaml -n $NAMESPACE
        ```

=== "via the command line"

    Instead of storing restore settings in a separate file, you can pass them directly to the `kubectl apply` command as follows:

    ```bash
    cat <<EOF | kubectl apply -n $NAMESPACE  -f-
    apiVersion: "ps.percona.com/v1"
    kind: "PerconaServerMySQLRestore"
    metadata:
      name: "restore1"
    spec:
      clusterName: "ps-cluster1"
      backupName: "backup1"
    EOF
    ```

## Restore with point-in-time recovery

Before performing a point-in-time recovery, ensure you have:

* Enabled binlog collection in your cluster configuration
* Identified a base backup to restore from
* Determined either the GTID set (for restoring up to a specific transaction) or the exact timestamp (for restoring up to a specific time)
* Configured the backup storage appropriately

### Example 1. Restore to a specific transaction

1. Edit the [deploy/backup/restore.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/restore.yaml) and specify the following options:
    
    * `spec.clusterName` - the name of your cluster
    * `spec.backupName` - the name of a backup 
    * configure point-in-time recovery in the `spec.pitr` subsection:
  
        * `type` - specify `time`
        * `date` - specify the timestamp to restore the database to
  
    Here's the example configuration:

    ```yaml
    apiVersion: ps.percona.com/v1
    kind: PerconaServerMySQLRestore
    metadata:
      name: restore-pitr-date
    spec:
      clusterName: ps-cluster1
      backupName: backup1
      pitr:
        type: date
        date: "2026-03-20 09:15:00"
    ```

2. Apply the configuration:

    ```bash
    kubectl apply -f deploy/backup/restore.yaml -n <namespace>
    ```

### Example 2. Restore to a specific timestamp

1. Edit the [deploy/backup/restore.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/restore.yaml) and specify the following options:

    * `spec.clusterName` - the name of your cluster
    * `spec.backupName` - the name of a backup
    * configure point-in-time recovery in the `spec.pitr` subsection:
  
        * `type` - specify `gtid`
        * `gtid` - specify the GTID set to restore the database to. It has the format `source_id:transaction_id`
  
    Here's the example configuration:

    ```yaml
    apiVersion: ps.percona.com/v1
    kind: PerconaServerMySQLRestore
    metadata:
      name: restore-pitr-gtid
    spec:
      clusterName: ps-cluster1
      backupName: backup1
      pitr:
        type: gtid
        gtid: "cc5e06e7-241e-11f1-a165-522d36bd0c5e:225"
    ```

2. Apply the configuration:

    ```bash
    kubectl apply -f deploy/backup/restore.yaml -n <namespace>
    ```

## View restore details 

When you start the restore, the restore job is created. You can check the job details using these commands:

```bash
kubectl get job -n <namespace>
```

??? example  "Sample output"

    ```
    xb-restore-restore2                                Running    0/1                      0s
    xb-restore-restore2                                Complete             1/1           25s        25s
    ```

You can check the restore progress with this command:

```bash
kubectl get ps-restore -n $NAMESPACE
```

## Troubleshooting

If you face issues with restore, refer to our [Restore troubleshooting guide](debug-backup-restore.md#restores) for help.
