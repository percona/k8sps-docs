# Data-at-rest encryption

Data-at-rest encryption ensures that stored data remains protected even if the underlying storage is compromised. Percona Operator for MySQL uses the `keyring_vault` plugin, shipped with Percona Server for MySQL, to encrypt tablespaces, bin logs and backups. 

[HashiCorp Vault :octicons-link-external-16:](https://www.vaultproject.io/) is used to securely store and manage encryption keys, enabling automatic key rotation, audit logging, and compliance with enterprise security standards. This setup enhances the overall security posture of your MySQL cluster.

This guide walks you through deploying and configuring HashiCorp Vault to work with Percona Operator for MySQL to enable data-at-rest encryption. 
## Create the namespace

It is a good practice to isolate workloads in Kubernetes using namespaces. Create a namespace with the following command:

```{.bash .data-prompt="$"}
$ kubectl create namespace vault
```

Export the namespace as an environment variable to simplify further configuration and management

```bash 
NAMESPACE="vault"
```

## Install Vault

For this setup, we install Vault in Kubernetes using the [Helm 3 package manager :octicons-link-external-16:](https://helm.sh/). However, Helm is not required — any supported Vault deployment (on-premises, in the cloud, or a managed Vault service) works as long as the Operator can reach it.

1. Add and update the Vault Helm repository.

    ``` {.bash data-prompt="$" }
    $ helm repo add hashicorp https://helm.releases.hashicorp.com
    $ helm repo update
    ```

2. Install Vault 

    ``` {.bash data-prompt="$" }
    $ helm upgrade --install vault hashicorp/vault \ 
      --namespace $NAMESPACE \
    ```

    ??? example "Sample output"

        ```{.text .no-copy}
        NAME: vault2
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

    ```{.bash data-prompt="$" }
    $(kubectl -n $NAMESPACE get pod -l app.kubernetes.io/name=vault -o jsonpath='{.items[0].metadata.name}')
    ```

    ??? example "Sample output"

        ```{.text .no-copy}
        vault-0
        ```

4. After Vault is installed, you need to initialize it. Run the following command:

    ```{.bash .data-prompt="$"}
    $ kubectl exec -it pod/vault-0 -- vault operator init -key-shares=1 -key-threshold=1 -format=json > /tmp/vault-init
    ```
    
    The command does the following:

    * Connects to the Vault Pod
    * Initializes Vault server
    * Creates 1 unseal key share which is required to unseal the server
    * Outputs the init response in JSON format to a local file `/tmp/vault-init`. It includes unseal keys and root token.

5.  Vault is started in a sealed state. In this state Vault can access the storage but it cannot decrypt data. In order to use Vault, you need to unseal it.

    Retrieve the unseal key from the file:

    ```{.bash .data-prompt="$"}
    $ unsealKey=$(jq -r ".unseal_keys_b64[]" < /tmp/vault-init
    ```

    Now, unseal Vault. Run the following command on every Pod where Vault is running:

    ```{.bash .data-prompt="$"}
    $ kubectl exec -it pod/vault2-0 -n $NAMESPACE -- vault operator unseal "$unsealKey"
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

    ```{.bash .data-prompt="$"}
    $ cat /tmp/vault-init | jq -r ".root_token"
    ```

    ??? example "Sample output"

        ```{.text .no-copy}
        hvs.CvmS4c0DPTvHv5eJgXWMJg9r
        ```

2. Authenticate in Vault with this token:

    ``` {.bash data-prompt="$" }
    $ kubectl exec -it vault-0 -n $NAMESPACE -- /bin/sh
    $ vault login hvs.CvmS4c0DPTvHv5eJgXWMJg9r
    ```

3. Enable the secrets engine at the mount path. The following command enables KV secrets engine v2 and the `ps-secret` mount-path:
    
     ``` {.bash data-prompt="$" }
     $ vault secrets enable --version=2 -path=ps-secret kv
     ```

    ??? example "Sample output"

        ```{.text .no-copy}
        Success! Enabled the kv secrets engine at: ps-secret/
        ```

## Create a Secret for Vault

To enable Vault for the Operator, create a Secrets object for it. To do so, create a YAML configuration file and specify the following information:

* A token to access Vault
* A Vault server URL
* The secrets mount path
* Path to TLS certificates if you [deployed Vault with TLS :octicons-link-external-16:](https://developer.hashicorp.com/vault/docs/auth/cert)
* Contents of the ca.cert certificate file

You can modify the example `deploy/vault-secret.yaml` configuration file:

=== "HTTP access without TLS"

    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: cluster1-vault
    type: Opaque
    stringData:
      keyring_vault.conf: |-
        token = hvs.CvmS4c0DPTvHv5eJgXWMJg9r
        vault_url = http://vault2.vault.svc.cluster.local:8200
        secret_mount_point = ps-secret
    ```

=== "HTTPS access with TLS"

    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: cluster1-vault
    type: Opaque
    stringData:
      keyring_vault.conf: |-
        token = hvs.CvmS4c0DPTvHv5eJgXWMJg9r
        vault_url = http://vault2.vault.svc.cluster.local:8200
        secret_mount_point = ps-secret
        vault_ca = /etc/mysql/vault-keyring-secret/ca.cert
    ca.cert: |-
      -----BEGIN CERTIFICATE-----
      MIIEczCCA1ugAwIBAgIBADANBgkqhkiG9w0BAQQFAD..AkGA1UEBhMCR0Ix
      EzARBgNVBAgTClNvbWUtU3RhdGUxFDASBgNVBAoTC0..0EgTHRkMTcwNQYD
      7vQMfXdGsRrXNGRGnX+vWDZ3/zWI0joDtCkNnqEpVn..HoX
      -----END CERTIFICATE-----
    ```

    Note that you must either specify the certificate value or don't declare it at all. Having a commented `#ca.cert` field in the Secret configuration file is not allowed.

Now create a Secrets object:

``` {.bash data-prompt="$" }
$ kubectl apply -f deploy/vault-secret.yaml -n $NAMESPACE
```

## Reference the Secret in your Custom Resource manifest 

Now, reference the Vault Secret in the Operator Custom Resource manifest. Note that the Secret name is the one you specified in the `metadata.name` field when you created a Secret.

Since this is a running cluster, we will apply a patch:

``` {.bash data-prompt="$" }
$ kubectl patch ps cluster1 \
  --namespace $NAMESPACE \
  --type=merge \
  --patch '{"spec":{"mysql":{"vaultSecretName":"cluster1-vault"}}}'
```

## Use data at rest encryption

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
