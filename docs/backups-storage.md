# Configure storage for backups

You configure backup storage in the `backup.storages` subsection of your Custom Resource using the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml) file.

Before configuring storage, you need to create a [Kubernetes Secret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/) object that contains the credentials needed to access your storage.

To [encrypt backups](backups-encrypted.md) in object storage, create a separate Secret with your encryption key and reference it in `spec.backup.encryptionKeySecret` or under the storage entry.

=== ":fontawesome-brands-amazon: Amazon S3 or S3-compatible storage"

    To use Amazon S3 or S3-compatible storage for backups, create a Secret object with your access credentials. Use the [deploy/backup/backup-secret-s3.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/backup-secret-s3.yaml) file as an example. You must specify the following information:

    * `name` is the name of the Kubernetes secret which you will reference in the Custom Resource
    * `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are base64-encoded keys to access S3 storage

        Use the following command to encode the keys:

        === ":simple-linux: in Linux"

            ```bash
            echo -n 'plain-text-string' | base64 --wrap=0
            ```

        === ":simple-apple: in macOS"

            ```bash
            echo -n 'plain-text-string' | base64
            ```

    Here's the example configuration of the Secret file:

    ```yaml title="deploy/backup/backup-secret-s3.yaml"
    apiVersion: v1
    kind: Secret
    metadata:
      name: ps-cluster1-s3-credentials
    type: Opaque
    data:
      AWS_ACCESS_KEY_ID: UkVQTEFDRS1XSVRILUFXUy1BQ0NFU1MtS0VZ
      AWS_SECRET_ACCESS_KEY: UkVQTEFDRS1XSVRILUFXUy1TRUNSRVQtS0VZ
    ```

    1. Create the Secret object with this file:

        ```bash
        kubectl apply -f deploy/backup/backup-secret-s3.yaml -n <namespace>
        ```

    2. Configure the storage in the Custom Resource. Modify the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml) file and define the following information:

        * `bucket` where the data will be stored
        * `region` - location of the bucket
        * `credentialsSecret` - the name of the Secret you created previously

        Here's the example:

        ```yaml
        backup:
          enabled: true
          ...
          storages:
            s3-us-west:
              type: s3
              s3:
                bucket: S3-BACKUP-BUCKET-NAME-HERE
                region: us-west-2
                credentialsSecret: ps-cluster1-s3-credentials
        ```

        !!! note "S3-compatible storage"

            If you use S3-compatible storage instead of Amazon S3, add the `endpointUrl` option in the `s3` subsection. This points to your storage service and is specific to your cloud provider. For example, for MinIO:

            ```yaml
            endpointUrl: https://minio-service:9000
            ```

            You can use a certificate from your organization's PKI and verify TLS communication using those certificates. See the [Configure TLS verification with custom certificates](#configure-tls-verification-with-custom-certificates-for-s3-storage) section for configuration steps.

        !!! tip "Organizing backups"

            You can use the [prefix](operator.md#backupstoragesstorage-names3prefix) option to specify a path (sub-folder) inside the S3 bucket where backups will be stored. If you don't set a prefix, backups are stored in the root directory.

    3. Apply the configuration:

        ```bash
        kubectl apply -f deploy/cr.yaml -n <namespace>
        ```

    For more configuration options, see the [Operator Custom Resource options](operator.md#operator-backup-section).

=== ":material-microsoft-azure: Microsoft Azure Blob storage"

    To use [Azure Blob Storage :octicons-link-external-16:](https://azure.microsoft.com/en-us/services/storage/blobs/) for storing backups, create a Secret object with your access credentials. Use the [deploy/backup/backup-secret-azure.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/backup-secret-azure.yaml) file as an example. You must specify the following information:

    * `name` is the name of the Kubernetes secret which you will reference in the Custom Resource
    * `AZURE_STORAGE_ACCOUNT_NAME` and `AZURE_STORAGE_ACCOUNT_KEY` are base64-encoded credentials to access Azure Blob storage

        Use the following command to encode the credentials:

        === ":simple-linux: in Linux"

            ```bash
            echo -n 'plain-text-string' | base64 --wrap=0
            ```

        === ":simple-apple: in macOS"

            ```bash
            echo -n 'plain-text-string' | base64
            ```

    Here's the example configuration of the Secret file:

    ```yaml title="deploy/backup/backup-secret-azure.yaml"
    apiVersion: v1
    kind: Secret
    metadata:
      name: ps-cluster1-azure-credentials
    type: Opaque
    data:
      AZURE_STORAGE_ACCOUNT_NAME: UkVQTEFDRS1XSVRILUFXUy1BQ0NFU1MtS0VZ
      AZURE_STORAGE_ACCOUNT_KEY: UkVQTEFDRS1XSVRILUFXUy1TRUNSRVQtS0VZ
    ```

    1. Create the Secret object with this file:

        ```bash
        kubectl apply -f deploy/backup/backup-secret-azure.yaml -n <namespace>
        ```

    2. Configure the storage in the Custom Resource. Modify the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml) file and define the following information:

        * `container` where the data will be stored
        * `credentialsSecret` - the name of the Secret you created previously

        Here's the example:

        ```yaml
        backup:
          enabled: true
          ...
          storages:
            azure-blob:
              type: azure
              azure:
                container: <your-container-name>
                credentialsSecret: ps-cluster1-azure-credentials
        ```

    3. Apply the configuration:

        ```bash
        kubectl apply -f deploy/cr.yaml -n <namespace>
        ```

    For more configuration options, see the [Operator Custom Resource options](operator.md#operator-backup-section).

=== ":material-google-cloud: Google Cloud Storage"

    To use Google Cloud Storage for storing backups, create a Secret object with your access credentials. Use the [deploy/backup/backup-secret-gcp.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/backup-secret-gcp.yaml) file as an example. You must specify the following information:

    * `name` is the name of the Kubernetes secret which you will reference in the Custom Resource
    * `ACCESS_KEY_ID` and `SECRET_ACCESS_KEY` are base64-encoded keys to access GCS storage

        Use the following command to encode the keys:

        === ":simple-linux: in Linux"

            ```bash
            echo -n 'plain-text-string' | base64 --wrap=0
            ```

        === ":simple-apple: in macOS"

            ```bash
            echo -n 'plain-text-string' | base64
            ```

    Here's the example configuration of the Secret file:

    ```yaml title="deploy/backup/backup-secret-gcp.yaml"
    apiVersion: v1
    kind: Secret
    metadata:
      name: ps-cluster1-gcp-credentials
    type: Opaque
    data:
      ACCESS_KEY_ID: Z2NwLWFjY2Vzcy1rZXkK
      SECRET_ACCESS_KEY: Z2NwLXNlY3JldC1rZXkK
    ```

    1. Create the Secret object with this file:

        ```bash
        kubectl apply -f deploy/backup/backup-secret-gcp.yaml -n <namespace>
        ```

    2. Configure the storage in the Custom Resource. Modify the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml) file and define the following information:

        * `bucket` where the data will be stored
        * `credentialsSecret` - the name of the Secret you created previously

        Here's the example:

        ```yaml
        backup:
          enabled: true
          ...
          storages:
            gcp-cs:
              type: gcs
              gcs:
                bucket: GCS-BACKUP-BUCKET-NAME-HERE
                credentialsSecret: ps-cluster1-gcp-credentials
        ```

    3. Apply the configuration:

        ```bash
        kubectl apply -f deploy/cr.yaml -n <namespace>
        ```

    For more configuration options, see the [Operator Custom Resource options](operator.md#operator-backup-section).

## Configure TLS verification with custom certificates for S3 storage

!!! note "Version added: [1.3.0](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.3.0.md)"

You can use your organization's CA to verify TLS to S3-compatible storage. This way you ensure secure communication and comply with the security policies in your organization.

You must run the Operator 1.3.0 and have a Custom Resource version (`spec.crVersion`) set to `1.3.0` or later.

To configure TLS verification with custom certificates, do the following:

--8<-- [start:casecret]

1. Create a Secret that contains the CA certificate needed to verify the S3 endpoint. This Secret is separate from the storage credentials Secret.

    You can create it from a file:

    ```bash
    kubectl create secret generic minio-ca-bundle --from-file=ca.crt=/path/to/ca.crt -n <namespace>
    ```

    Or define it in YAML. The `ca.crt` value must be base64-encoded:

    ```yaml title="custom-ca-bundle.yaml"
    apiVersion: v1
    kind: Secret
    metadata:
      name: minio-ca-bundle
    type: Opaque
    data:
      ca.crt: <base64-encoded-ca>
    ```

    Apply the Secret:

    ```bash
    kubectl apply -f custom-ca-bundle.yaml -n <namespace>
    ```

--8<-- [end:casecret]

2. Modify the S3 storage configuration in the Custom Resource and specify the following:

    * `storages.<NAME>.s3.caBundle.name` is the name of the Secret you created
    * `storages.<NAME>.s3.caBundle.key` is the key in the Secret that holds the CA certificate. If you omit `key`, the Operator uses `ca.crt`.
    * Keep `storages.<NAME>.verifyTLS` set to `true`

    Here's the example configuration:

    ```yaml
    backup:
      enabled: true
      storages:
        minio:
          type: s3
          verifyTLS: true
          s3:
            bucket: S3-BACKUP-BUCKET-NAME-HERE
            region: us-west-2
            credentialsSecret: ps-cluster1-s3-credentials
            endpointUrl: https://minio-service:9000
            caBundle:
              name: minio-ca-bundle
              key: ca.crt
    ```

3. Apply the configuration:

    ```bash
    kubectl apply -f deploy/cr.yaml -n <namespace>
    ```

The Operator uses this CA to verify TLS when it runs backups, restores, and backup deletion Jobs for that storage.

If the CA lives in a cert-manager Secret that also contains `tls.crt` and `tls.key`, still set `caBundle.key` to `ca.crt` (or the key that holds the CA). The Operator mounts only that key.

If you configure several S3 storages, each can reference its own CA. The Operator mounts all of those CAs on MySQL Pods. A backup or restore Job uses the CA of the storage you selected.

`caBundle` on `backup.storages` does not apply to Binlog Server. To verify TLS communication for [point-in-time recovery](backups-pitr.md), supply your custom certificate within the Binlog Server configuration as well by setting `caBundle` on [`backup.pitr.binlogServer.storage.s3`](backups-pitr.md#verify-tls-with-a-custom-ca). See [Verify TLS with a custom CA](backups-pitr.md#verify-tls-with-a-custom-ca).

When you restore with `backupSource`, such as on a new cluster, create the CA Secret on the target and set `caBundle` on `backupSource.storage.s3`. See [Restore from S3 storage that uses a custom CA](backups-restore-to-new-cluster.md#restore-from-s3-storage-that-uses-a-custom-ca). 

For point-in-time recovery, also set `caBundle` on the binlog storage as shown in [Use a custom CA](backups-restore-pitr.md#use-a-custom-ca).

