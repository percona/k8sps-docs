# Restore the cluster from a previously saved backup

You can restore from a backup as follows:

* On the same Kubernetes cluster and in the same namespace where you made the backup
* On a [new cluster deployed in a different Kubernetes-based environment](backups-restore-to-new-cluster.md).

This document focuses on the restore to the same cluster.

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

## Restore steps

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

## View restore details 

When you start the restore, the restore job is created. You can check the job details using these commands:

```bash
kubectl get job
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