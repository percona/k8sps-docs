# Configure storage for backups

You can configure storage for backups in the `backup.storages` subsection of the
Custom Resource, using the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
configuration file.

You should also create the [Kubernetes Secret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/)
object with credentials needed to access the storage.

=== "Amazon S3 or S3-compatible storage"

    Since backups are stored separately on the Amazon S3, a secret with
    `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` should be present on
    the Kubernetes cluster. The secrets file with these base64-encoded keys should
    be created: for example [deploy/backup/backup-s3.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/backup/backup-secret-s3.yaml) file with the following
    contents.

    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: ps-cluster1-s3-credentials
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
            echo -n 'plain-text-string' | base64 --wrap=0
            ```    

        === "in macOS"

            ```bash
            echo -n 'plain-text-string' | base64
            ```    

    The `name` value is the [Kubernetes
    secret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/)
    name which will be used further, and `AWS_ACCESS_KEY_ID` and
    `AWS_SECRET_ACCESS_KEY` are the keys to access S3 storage (and
    obviously they should contain proper values to make this access
    possible). To have effect secrets file should be applied with the
    appropriate command to create the secret object,
    e.g. `kubectl apply -f deploy/backup/backup-s3.yaml` (for Kubernetes).

    All the data needed to access the S3-compatible cloud to store backups should be
    put into the `backup.storages` subsection. Here is an example
    of [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
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
            credentialsSecret: ps-cluster1-s3-credentials
    ```

    If you use some S3-compatible storage instead of the original
    Amazon S3, the [endpointURL :octicons-link-external-16:](https://docs.min.io/docs/aws-cli-with-minio.html) is needed in the `s3` subsection which points to the actual cloud used for backups and
    is specific to the cloud provider. For example, using the endpoint URL for MinIO will be:

    ```yaml
    endpointUrl: https://minio-service:9000
    ```

    Also you can use [prefix](operator.md#backupstoragesstorage-names3prefix) option to
    specify the path (sub-folder) to the backups inside the S3 bucket. If prefix is
    not set, backups are stored in the root directory.

    The options within this subsection are further explained in the
    [Operator Custom Resource options](operator.md#operator-backup-section).

    One option which should be mentioned separately is
    `credentialsSecret` which is a [Kubernetes
    secret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/)
    for backups. Value of this key should be the same as the name used to
    create the secret object (`ps-cluster1-s3-credentials` in the last
    example).

=== "Microsoft Azure Blob storage"

    Since backups are stored separately on [Azure Blob Storage :octicons-link-external-16:](https://azure.microsoft.com/en-us/services/storage/blobs/),
    a secret with `AZURE_STORAGE_ACCOUNT_NAME` and `AZURE_STORAGE_ACCOUNT_KEY` should be present on
    the Kubernetes cluster. The secrets file with these base64-encoded keys should
    be created: for example `deploy/backup/backup-azure.yaml` file with the following
    contents.

    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: ps-cluster1-azure-credentials
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
            echo -n 'plain-text-string' | base64 --wrap=0
            ```    

        === "in macOS"

            ```bash
            echo -n 'plain-text-string' | base64
            ```    

    The `name` value is the [Kubernetes
    secret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/)
    name which will be used further, and `AZURE_STORAGE_ACCOUNT_NAME` and
    `AZURE_STORAGE_ACCOUNT_KEY` credentials will be used to access the storage
    (and obviously they should contain proper values to make this access
    possible). To have effect secrets file should be applied with the appropriate
    command to create the secret object, e.g.
    `kubectl apply -f deploy/backup/backup-azure.yaml` (for Kubernetes).

    All the data needed to access the Azure Blob storage to store backups should be
    put into the `backup.storages` subsection. Here is an example
    of [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
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
            credentialsSecret: ps-cluster1-azure-credentials
    ```

    The options within this subsection are further explained in the
    [Operator Custom Resource options](operator.md#operator-backup-section).

    One option which should be mentioned separately is
    `credentialsSecret` which is a [Kubernetes
    secret :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/)
    for backups. Value of this key should be the same as the name used to
    create the secret object (`ps-cluster1-azure-credentials` in the last
    example).

=== "Google Cloud Storage"

    To use Google Cloud Storage for storing backups, create a Secret object with the access credentials to this storage. Use the `deploy/backup/backup-secret-gcp.yaml` file as the example. You must specify the following information:

    *  `name` is the name of the Kubernetes secret which you will reference in the Custom Resource
    * `ACCESS_KEY_ID` and `SECRET_ACCESS_KEY` are base64 encoded keys to access GCS storage. 

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

    ```title="deploy/backup/backup-secret-gcp.yaml"
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

    2. Configure the storage in the Custom Resource. Modify the `deploy/cr.yaml` file and define the following information:

        *  `bucket` where the data will be stored
        *  `region` - location of the bucket
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
                region: us-east-1
                credentialsSecret: ps-cluster1-gcp-credentials
        ```

    3. Apply the configuration:

       ```bash
       kubectl apply -f deploy/cr.yaml -n <namespace>
       ```