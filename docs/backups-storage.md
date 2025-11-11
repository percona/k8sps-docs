# Configure storage for backups

You configure backup storage in the `backup.storages` subsection of your Custom Resource using the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml) file.

Before configuring storage, you need to create a [Kubernetes Secret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/) object that contains the credentials needed to access your storage.

=== "Amazon S3 or S3-compatible storage"

    To use Amazon S3 or S3-compatible storage for backups, create a Secret object with your access credentials. Use the [deploy/backup/backup-secret-s3.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/backup-secret-s3.yaml) file as an example. You must specify the following information:

    * `name` is the name of the Kubernetes secret which you will reference in the Custom Resource
    * `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are base64-encoded keys to access S3 storage

        Use the following command to encode the keys:

        === "in Linux"

            ```bash
            echo -n 'plain-text-string' | base64 --wrap=0
            ```

        === "in macOS"

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

        !!! tip "Organizing backups"

            You can use the [prefix](operator.md#backupstoragesstorage-names3prefix) option to specify a path (sub-folder) inside the S3 bucket where backups will be stored. If you don't set a prefix, backups are stored in the root directory.

    3. Apply the configuration:

        ```bash
        kubectl apply -f deploy/cr.yaml -n <namespace>
        ```

    For more configuration options, see the [Operator Custom Resource options](operator.md#operator-backup-section).

=== "Microsoft Azure Blob storage"

    To use [Azure Blob Storage :octicons-link-external-16:](https://azure.microsoft.com/en-us/services/storage/blobs/) for storing backups, create a Secret object with your access credentials. Use the [deploy/backup/backup-secret-azure.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/backup-secret-azure.yaml) file as an example. You must specify the following information:

    * `name` is the name of the Kubernetes secret which you will reference in the Custom Resource
    * `AZURE_STORAGE_ACCOUNT_NAME` and `AZURE_STORAGE_ACCOUNT_KEY` are base64-encoded credentials to access Azure Blob storage

        Use the following command to encode the credentials:

        === "in Linux"

            ```bash
            echo -n 'plain-text-string' | base64 --wrap=0
            ```

        === "in macOS"

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

=== "Google Cloud Storage"

    To use Google Cloud Storage for storing backups, create a Secret object with your access credentials. Use the [deploy/backup/backup-secret-gcp.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/backup/backup-secret-gcp.yaml) file as an example. You must specify the following information:

    * `name` is the name of the Kubernetes secret which you will reference in the Custom Resource
    * `ACCESS_KEY_ID` and `SECRET_ACCESS_KEY` are base64-encoded keys to access GCS storage

        Use the following command to encode the keys:

        === "in Linux"

            ```bash
            echo -n 'plain-text-string' | base64 --wrap=0
            ```

        === "in macOS"

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
