# Configure data-at-rest encryption with HashiCorp Vault

This guide walks you through deploying and configuring HashiCorp Vault to work with Percona Operator for MySQL to enable [data-at-rest encryption](encryption.md). 

## Create the namespace

It is a good practice to isolate workloads in Kubernetes using namespaces. Create a namespace with the following command:

```{.bash data-prompt="$"}
kubectl create namespace vault
```

Export the namespace as an environment variable to simplify further configuration and management

```bash 
NAMESPACE="vault"
```

## Install Vault

For this setup, we install Vault in Kubernetes using the [Helm 3 package manager :octicons-link-external-16:](https://helm.sh/). However, Helm is not required — any supported Vault deployment (on-premises, in the cloud, or a managed Vault service) works as long as the Operator can reach it.

1. Add and update the Vault Helm repository.

    ``` bash
    helm repo add hashicorp https://helm.releases.hashicorp.com
    helm repo update
    ```

2. Install Vault 

    ``` bash
    helm upgrade --install vault hashicorp/vault --namespace $NAMESPACE 
    ```

    ??? example "Sample output"

        ```{.text .no-copy}
        NAME: vault
        LAST DEPLOYED: Wed Aug 20 12:55:38 2025
        NAMESPACE: vault
        STATUS: deployed
        REVISION: 1
        NOTES:
        Thank you for installing HashiCorp Vault!

        Now that you have deployed Vault, you should look over the docs on using
        Vault with Kubernetes available here:

        https://developer.hashicorp.com/vault/docs
        ```

3. Retrieve the Pod name where Vault is running:

    ```bash
    $(kubectl -n $NAMESPACE get pod -l app.kubernetes.io/name=vault -o jsonpath='{.items[0].metadata.name}')
    ```

    ??? example "Sample output"

        ```{.text .no-copy}
        vault-0
        ```

4. After Vault is installed, you need to initialize it. Run the following command:

    ```{.bash data-prompt="$"}
    kubectl exec -it pod/vault-0 -n $NAMESPACE -- vault operator init -key-shares=1 -key-threshold=1 -format=json > /tmp/vault-init
    ```
    
    The command does the following:

    * Connects to the Vault Pod
    * Initializes Vault server
    * Creates 1 unseal key share which is required to unseal the server
    * Outputs the init response in JSON format to a local file `/tmp/vault-init`. It includes unseal keys and root token.

5.  Vault is started in a sealed state. In this state Vault can access the storage but it cannot decrypt data. In order to use Vault, you need to unseal it.

    Retrieve the unseal key from the file:

    ```{.bash data-prompt="$"}
    unsealKey=$(jq -r ".unseal_keys_b64[]" < /tmp/vault-init)
    ```

    Now, unseal Vault. Run the following command on every Pod where Vault is running:

    ```{.bash data-prompt="$"}
    kubectl exec -it pod/vault-0 -n $NAMESPACE -- vault operator unseal "$unsealKey"
    ```
    
    ??? example "Sample output"

        ```{.text .no-copy}
        Key             Value
        ---             -----
        Seal Type       shamir
        Initialized     true
        Sealed          false
        Total Shares    1
        Threshold       1
        Version         1.20.1
        Build Date      2025-07-24T13:33:51Z
        Storage Type    file
        Cluster Name    vault-cluster-55062a37
        Cluster ID      37d0c2e4-8f47-14f7-ca49-905b66a1804d
        HA Enabled      false
        ```

## Configure Vault

At this step you need to configure Vault and enable secrets within it. To do so you must first authenticate in Vault. 

When you started Vault, it generates and starts with a [root token :octicons-link-external-16:](https://developer.hashicorp.com/vault/docs/concepts/tokens) that provides full access to Vault. Use this token to authenticate.

!!! note

    For the purposes of this tutorial we use the root token in further sections. For security considerations, the use of root token is not recommended. Refer to the [Create token :octicons-link-external-16:](https://developer.hashicorp.com/vault/docs/commands/token/create) in Vault documentation how to create user tokens.

1. Extract the Vault root token from the file where you saved the init response output:

    ```{.bash data-prompt="$"}
    cat /tmp/vault-init | jq -r ".root_token"
    ```

    ??? example "Sample output"

        ```{.text .no-copy}
        hvs.*************Jg9r
        ```

2. Connect to Vault Pod:

    ``` bash
    kubectl exec -it vault-0 -n $NAMESPACE -- /bin/sh
    ```

3. Authenticate in Vault with this token:
    
    ```bash
    vault login hvs.*************Jg9r
    ```

4. Enable the secrets engine at the mount path. The following command enables KV secrets engine v2 at the `ps-secret` mount-path:
    
     ``` bash
     vault secrets enable --version=2 -path=ps-secret kv
     ```

    ??? example "Sample output"

        ```{.text .no-copy}
        Success! Enabled the kv secrets engine at: ps-secret/
        ```

## Create a Secret for Vault

To enable Vault for the Operator, create a Secret object for it. To do so, create a YAML configuration file and specify the following information:

* A token to access Vault
* A Vault server URL
* The secrets mount path
* Path to TLS certificates if you [deployed Vault with TLS :octicons-link-external-16:](https://developer.hashicorp.com/vault/docs/auth/cert)
* Contents of the ca.cert certificate file

Depending on Percona Server for MySQL version, you must specify the Vault configuration as follows:

* For Percona Server for MySQL 8.0 - as key=value pairs 
* For Percona Server for MySQL 8.4 - as a JSON object

You can modify the example `deploy/vault-secret.yaml` configuration file:

=== "Percona Server for MySQL 8.0"

    === "HTTP access without TLS"

        ```yaml
        apiVersion: v1
        kind: Secret
        metadata:
          name: ps-cluster1-vault
        type: Opaque
        stringData:
          keyring_vault.cnf: |-
            token = hvs.CvmS4c0DPTvHv5eJgXWMJg9r
            vault_url = http://vault.vault.svc.cluster.local:8200
            secret_mount_point = ps-secret
        ```

    === "HTTPS access with TLS"

        ```yaml
        apiVersion: v1
        kind: Secret
        metadata:
          name: ps-cluster1-vault
        type: Opaque
        stringData:
          keyring_vault.cnf: |-
            token = hvs.CvmS4c0DPTvHv5eJgXWMJg9r
            vault_url = https://vault.vault.svc.cluster.local:8200
            secret_mount_point = ps-secret
            vault_ca = /etc/mysql/vault-keyring-secret/ca.cert
        ca.cert: |-
          -----BEGIN CERTIFICATE-----
          MIIEczCCA1ugAwIBAgIBADANBgkqhkiG9w0BAQQFAD..AkGA1UEBhMCR0Ix
          EzARBgNVBAgTClNvbWUtU3RhdGUxFDASBgNVBAoTC0..0EgTHRkMTcwNQYD
          7vQMfXdGsRrXNGRGnX+vWDZ3/zWI0joDtCkNnqEpVn..HoX
          -----END CERTIFICATE-----
        ```

=== "Percona Server for MySQL 8.4"

    === "HTTP access without TLS"

        ```yaml
        apiVersion: v1
        kind: Secret
        metadata:
          name: ps-cluster1-vault-84
        type: Opaque
        stringData:
          keyring_vault.cnf: |-
            {
              "token": "hvs.CvmS4c0DPTvHv5eJgXWMJg9r",
              "vault_url": "http://vault.vault.svc.cluster.local:8200",
              "secret_mount_point": "ps-secret"
            }
        ```

    === "HTTPS access with TLS"

        ```yaml
        apiVersion: v1
        kind: Secret
        metadata:
          name: ps-cluster1-vault-84
        type: Opaque
        stringData:
          keyring_vault.cnf: |-
            {
              "token": "hvs.CvmS4c0DPTvHv5eJgXWMJg9r",
              "vault_url": "https://vault.vault.svc.cluster.local:8200",
              "secret_mount_point": "ps-secret",
              "vault_ca": "/etc/mysql/vault-keyring-secret/ca.cert"
            }
        ca.cert: |-
          -----BEGIN CERTIFICATE-----
          MIIEczCCA1ugAwIBAgIBADANBgkqhkiG9w0BAQQFAD..AkGA1UEBhMCR0Ix
          EzARBgNVBAgTClNvbWUtU3RhdGUxFDASBgNVBAoTC0..0EgTHRkMTcwNQYD
          7vQMfXdGsRrXNGRGnX+vWDZ3/zWI0joDtCkNnqEpVn..HoX
          -----END CERTIFICATE-----
        ```

  Note that you must either specify the certificate value or don't declare it at all. Having a commented `#ca.cert` field in the Secret configuration file is not allowed.

Now create a Secret object. Replace the `<namespace>` placeholder with the namespace where your database cluster is deployed:

```bash
kubectl apply -f deploy/vault-secret.yaml -n <namespace>
```
!!! warning "If your deployment uses Group Replication as the cluster type, you must pause the cluster before patching to enable encryption."

    After you add the required secret, unpause the cluster to resume normal operation.

## Reference the Secret in your Custom Resource manifest 

Now, reference the Vault Secret in the Operator Custom Resource manifest. Note that the Secret name is the one you specified in the `metadata.name` field when you created a Secret.

1. Export the namespace where the cluster is deployed as an environment variable:

    ```bash
    export ps-cluster-namespace = <cluster-namespace>
    ```

2. Update the cluster configuration. Since this is a running cluster, we will apply a patch.

    === "Group replication"

        1. Pause the cluster:

            ``` bash
            kubectl patch ps ps-cluster1 \
              --namespace $<ps-cluster-namespace> \
              --type=merge \
              --patch '{"spec": {"pause": true}}'
            ```
        
        2. Apply the patch referencing your Secret. Note for MySQL 8.0 the default Secret name is `ps-cluster1-vault` and for MySQL 8.4 - `ps-cluster1-vault-84`. Use the following command as an example and specify the Secret name for the MySQL version you're using:

            ``` bash
            kubectl patch ps ps-cluster1 \
              --namespace $<ps-cluster-namespace> \
              --type=merge \
              --patch '{"spec":{"mysql":{"vaultSecretName":"ps-cluster1-vault"}}}'
            ```

        3. Unpause the cluster:
            
            ``` bash
            kubectl patch ps ps-cluster1 \
              --namespace $<ps-cluster-namespace> \
              --type=merge \
              --patch '{"spec": {"pause": false}}'
            ```

    === "Asynchronous replication"

        Apply the patch referencing your Secret. Note for MySQL 8.0 the default Secret name is `ps-cluster1-vault` and for MySQL 8.4 - `ps-cluster1-vault-84`. Use the following command as an example and specify the Secret name for the MySQL version you're using:
        
        ```bash
        kubectl patch ps ps-cluster1 \
          --namespace $<ps-cluster-namespace> \
          --type=merge \
          --patch '{"spec":{"mysql":{"vaultSecretName":"ps-cluster1-vault"}}}'
        ```


## Use data-at-rest encryption

To use encryption, you can:

* turn it on for every table you create with the `ENCRYPTION='Y'
clause in your SQL statement. For example, 

   ```sql
   CREATE TABLE t1 (c1 INT, PRIMARY KEY pk(c1)) ENCRYPTION='Y';
   CREATE TABLESPACE foo ADD DATAFILE 'foo.ibd' ENCRYPTION='Y';
   ```

* turn on default encryption of a schema or a general tablespace. Then all tables you create will have encryption enabled. To turn on default encryption, use the following SQL statement:

   ```sql
   SET default_table_encryption=ON;
   ```

## Verify encryption

Refer to the [Percona Server for MySQL documentation :octicons-link-external-16:](https://docs.percona.com/percona-server/8.0/verifying-encryption.html) for guidelines how to verify encryption in your database.
