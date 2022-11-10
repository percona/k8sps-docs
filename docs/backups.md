# Providing Backups

The Operator stores MySQL backups outside the
Kubernetes cluster: on [Amazon S3 or S3-compatible storage](https://en.wikipedia.org/wiki/Amazon_S3#S3_API_and_competing_services),
or on [Azure Blob Storage](https://azure.microsoft.com/en-us/services/storage/blobs/).

![image](assets/images/backup-s3.svg)

The Operator currently allows doing cluster backup *on-demand* (i.e. manually at
any moment). It uses the [Percona XtraBackup](https://docs.percona.com/percona-xtrabackup/latest/) tool.

Backups are controlled by the `backup` section of the
[deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
file. This section contains [backup.enabled](operator.md#backup-enabled) key (it should
be set to `true` to enable backups), and the number of options in the
`storages` subsection, needed to access cloud to store backups.

## Backups on Amazon S3 or S3-compatible storage

Since backups are stored separately on the Amazon S3, a secret with
`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` should be present on
the Kubernetes cluster. The secrets file with these base64-encoded keys should
be created: for example `deploy/backup-s3.yaml` file with the following
contents.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cluster1-s3-credentials
type: Opaque
data:
  AWS_ACCESS_KEY_ID: UkVQTEFDRS1XSVRILUFXUy1BQ0NFU1MtS0VZ
  AWS_SECRET_ACCESS_KEY: UkVQTEFDRS1XSVRILUFXUy1TRUNSRVQtS0VZ
```

!!! note

    The following command can be used to get a base64-encoded string from
    a plain text one:

    === "in Linux"

        ```bash
        $ echo -n 'plain-text-string' | base64 --wrap=0
        ```

    === "in macOS"

        ```bash
        $ echo -n 'plain-text-string' | base64
        ```

The `name` value is the [Kubernetes
secret](https://kubernetes.io/docs/concepts/configuration/secret/)
name which will be used further, and `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` are the keys to access S3 storage (and
obviously they should contain proper values to make this access
possible). To have effect secrets file should be applied with the
appropriate command to create the secret object,
e.g. `kubectl apply -f deploy/backup-s3.yaml` (for Kubernetes).

All the data needed to access the S3-compatible cloud to store backups should be
put into the `backup.storages` subsection. Here is an example
of [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
which uses Amazon S3 storage for backups:

```yaml
...
backup:
  enabled: true
  ...
  storages:
    s3-us-west:
      type: s3
      s3:
        bucket: S3-BACKUP-BUCKET-NAME-HERE
        region: us-west-2
        credentialsSecret: cluster1-s3-credentials
```

If you use some S3-compatible storage instead of the original
Amazon S3, the [endpointURL](https://docs.min.io/docs/aws-cli-with-minio.html) is needed in the `s3` subsection which points to the actual cloud used for backups and
is specific to the cloud provider. For example, using [Google Cloud](https://cloud.google.com) involves the [following](https://storage.googleapis.com) endpointUrl:

```yaml
endpointUrl: https://storage.googleapis.com
```

Also you can use [prefix](operator.md#backup-storages-s3-prefix) option to
specify the path (sub-folder) to the backups inside the S3 bucket. If prefix is
not set, backups are stored in the root directory.

The options within this subsection are further explained in the
[Operator Custom Resource options](operator.md#operator-backup-section).

One option which should be mentioned separately is
`credentialsSecret` which is a [Kubernetes
secret](https://kubernetes.io/docs/concepts/configuration/secret/)
for backups. Value of this key should be the same as the name used to
create the secret object (`cluster1-s3-credentials` in the last
example).

## Backups on Microsoft Azure Blob storage

Since backups are stored separately on [Azure Blob Storage](https://azure.microsoft.com/en-us/services/storage/blobs/),
a secret with `AZURE_STORAGE_ACCOUNT_NAME` and `AZURE_STORAGE_ACCOUNT_KEY` should be present on
the Kubernetes cluster. The secrets file with these base64-encoded keys should
be created: for example `deploy/backup-azure.yaml` file with the following
contents.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cluster1-azure-credentials
type: Opaque
data:
  AZURE_STORAGE_ACCOUNT_NAME: UkVQTEFDRS1XSVRILUFXUy1BQ0NFU1MtS0VZ
  AZURE_STORAGE_ACCOUNT_KEY: UkVQTEFDRS1XSVRILUFXUy1TRUNSRVQtS0VZ
```

!!! note

    The following command can be used to get a base64-encoded string from
    a plain text one:

    === "in Linux"

        ```bash
        $ echo -n 'plain-text-string' | base64 --wrap=0
        ```

    === "in macOS"

        ```bash
        $ echo -n 'plain-text-string' | base64
        ```

The `name` value is the [Kubernetes
secret](https://kubernetes.io/docs/concepts/configuration/secret/)
name which will be used further, and `AZURE_STORAGE_ACCOUNT_NAME` and
`AZURE_STORAGE_ACCOUNT_KEY` credentials will be used to access the storage
(and obviously they should contain proper values to make this access
possible). To have effect secrets file should be applied with the appropriate
command to create the secret object, e.g.
`kubectl apply -f deploy/backup-azure.yaml` (for Kubernetes).

All the data needed to access the Azure Blob storage to store backups should be
put into the `backup.storages` subsection. Here is an example
of [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
which uses Azure Blob storage for backups:

```yaml
...
backup:
  enabled: true
  ...
  storages:
    azure-blob:
      type: azure
      azure:
        container: <your-container-name>
        credentialsSecret: cluster1-azure-credentials
```

The options within this subsection are further explained in the
[Operator Custom Resource options](operator.md#operator-backup-section).

One option which should be mentioned separately is
`credentialsSecret` which is a [Kubernetes
secret](https://kubernetes.io/docs/concepts/configuration/secret/)
for backups. Value of this key should be the same as the name used to
create the secret object (`cluster1-azure-credentials` in the last
example).

## Making on-demand backup

To make an on-demand backup, the user should first make changes in the
`deploy/cr.yaml` configuration file: set the `backup.enabled` key to
`true` and configure backup storage in the `backup.storages` subsection.

When the `deploy/cr.yaml` file
contains correctly configured keys and is applied with `kubectl` command, use
*a special backup configuration YAML file* with the following contents:

* **backup name** in the `metadata.name` key,

* **Percona Distribution for MySQL Cluster name** in the `clusterName` key,

* **storage name** from `deploy/cr.yaml` in the `spec.storageName` key.

* <a name="finalizers"></a>**S3 backup finalizer** set by the `metadata.finalizers.delete-backup` key (it triggers the actual deletion of backup files from the S3 bucket when there is a manual or scheduled removal of the corresponding backup object).

The example of such file is [deploy/backup/backup.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/backup.yaml).

When the backup destination is configured and applied with kubectl apply -f deploy/cr.yaml command, make backup as follows:

```{.bash data-prompt="$"}
$ kubectl apply -f deploy/backup.yaml
```

!!! note

    Storing backup settings in a separate file can be replaced by
    passing its content to the `kubectl apply` command as follows:

    ```{.bash data-prompt="$"}
    $ cat <<EOF | kubectl apply -f-
    apiVersion: ps.percona.com/v1alpha1
    kind: PerconaServerMySQLBackup
    metadata:
      name: backup1
      finalizers:
        - delete-backup
    spec:
      clusterName: cluster1
      storageName: s3-us-west
    EOF
    ```

## Restore the cluster from a previously saved backup

Following things are needed to restore a previously saved backup:

* Make sure that the cluster is running.

* Find out correct names for the **backup** and the **cluster**. Available
backups can be listed with the following command:

    ```{.bash data-prompt="$"}
    $ kubectl get ps-backup
    ```

    And the following command will list existing Percona Distribution for MySQL
    Cluster names in the current Kubernetes-based environment:

    ```{.bash data-prompt="$"}
    $ kubectl get ps
    ```

When the correct names for the backup and the cluster are known, backup
restoration can be done in the following way.

1. Set appropriate keys in the `deploy/restore.yaml` file.

    * set `spec.clusterName` key to the name of the target cluster to restore
        the backup on,

    * set `spec.backupName` key to the name of your backup.

2. After that, the actual restoration process can be started as follows:

    ```{.bash data-prompt="$"}
    $ kubectl apply -f deploy/restore.yaml
    ```

!!! note

    Storing backup settings in a separate file can be replaced by passing
    its content to the `kubectl apply` command as follows:

    ```{.bash data-prompt="$"}
    $ cat <<EOF | kubectl apply -f-
    apiVersion: "ps.percona.com/v1alpha1"
    kind: "PerconaServerMySQLRestore"
    metadata:
      name: "restore1"
    spec:
      clusterName: "cluster1"
      backupName: "backup1"
    EOF
    ```

## Delete the unneeded backup

Manual deleting of a previously saved backup requires not more than the backup
name. This name can be taken from the list of available backups returned
by the following command:

```{.bash data-prompt="$"}
$ kubectl get ps-backup
```

When the name is known, backup can be deleted as follows:

```{.bash data-prompt="$"}
$ kubectl delete ps-backup/<backup-name>
```
