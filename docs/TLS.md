# Transport Layer Security (TLS)

The Percona Operator for MySQL uses Transport Layer
Security (TLS) cryptographic protocol for the following types of communication:

* External - communication between the client application and the cluster.
* Internal - communication between Percona Server for MySQL instances. The internal certificate is also used as an authorization method.

TLS security can be configured in several ways.

* By default, the Operator **generates long-term certificates** automatically during the cluster creation if there are no certificate secrets available. The Operator's self-signed issuer is local to the Operator Namespace. This self-signed issuer is created because Percona Distribution for MySQL
        requires all certificates issued by the same source.

* The Operator can use a *cert-manager*, which will
    automatically **generate and renew short-term TLS certificates**. You must explicitly install cert-manager for this scenario.
    
    The *cert-manager* acts as a self-signed issuer and generates certificates allowing you to deploy and use the
        Percona Operator without a separate certificate issuer.

* You can generate TLS certificates manually or obtain them from some other issuer and provide to the Operator.

## Install and use the *cert-manager*

### About the *cert-manager*

A [cert-manager :octicons-link-external-16:](https://cert-manager.io/docs/) is a Kubernetes certificate
management controller which is widely used to automate the management and
issuance of TLS certificates. It is community-driven, and open source.

When you have already installed *cert-manager*, nothing else is needed: just
deploy the Operator, and the Operator will request a certificate from the
*cert-manager*.

### Installation of the *cert-manager*

The cert-manager requires its own namespace

The steps to install the *cert-manager* are the following:

1. Create a namespace:

    ```{.bash data-prompt="$"}
    $ kubectl create namespace cert-manager
    ```

2. Disable resource validations on the cert-manager namespace:

    ```{.bash data-prompt="$"}
    $ kubectl label namespace cert-manager certmanager.k8s.io/disable-validation=true
    ```

3. Install the cert-manager:

    ```{.bash data-prompt="$"}
    $ kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v{{ certmanagerrecommended }}/cert-manager.yaml
    ```

4. Verify the *cert-manager* by running the following command:

    ```{.bash data-prompt="$"}
    $ kubectl get pods -n cert-manager
    ```

    The result should display the *cert-manager* and webhook active and running:

    ??? example "Expected output"

        ```{.text .no-copy}
        NAME                                       READY   STATUS    RESTARTS   AGE
        cert-manager-69f748766f-6chvt              1/1     Running   0          65s
        cert-manager-cainjector-7cf6557c49-l2cwt   1/1     Running   0          66s
        cert-manager-webhook-58f4cff74d-th4pp      1/1     Running   0          65s
        ```

Once you create the database with the Operator, it will automatically trigger the cert-manager to create certificates. Whenever you [check certificates for expiration](#), you will find that they are valid and short-term.

## Generate certificates manually

To generate certificates manually, follow these steps:

1. Provision a Certificate Authority (CA) to generate TLS certificates

2. Generate a CA key and certificate file with the server details

3. Create the server TLS certificates using the CA keys, certs, and server
    details

The set of commands generate certificates with the following attributes:

* `Server-pem` - Certificate

* `Server-key.pem` - the private key

* `ca.pem` - Certificate Authority

A secret must be added to `cr.yaml/spec/sslSecretName`.

```bash
cat <<EOF | cfssl gencert -initca - | cfssljson -bare ca
{
  "CN": "Root CA",
  "key": {
    "algo": "rsa",
    "size": 2048
  }
}
EOF

cat <<EOF | cfssl gencert -ca=ca.pem  -ca-key=ca-key.pem - | cfssljson -bare server
{
  "hosts": [
    "*.${CLUSTER_NAME}-mysql",
    "*.${CLUSTER_NAME}-mysql.${NAMESPACE}",
    "*.${CLUSTER_NAME}-mysql.${NAMESPACE}.svc",
    "*.${CLUSTER_NAME}-orchestrator",
    "*.${CLUSTER_NAME}-orchestrator.${NAMESPACE}",
    "*.${CLUSTER_NAME}-orchestrator.${NAMESPACE}.svc",
    "*.${CLUSTER_NAME}-router",
    "*.${CLUSTER_NAME}-router.${NAMESPACE}",
    "*.${CLUSTER_NAME}-router.${NAMESPACE}.svc"
  ],
  "CN": "${CLUSTER_NAME}-mysql",
  "key": {
    "algo": "rsa",
    "size": 2048
  }
}
EOF

kubectl create secret generic my-cluster-ssl --from-file=tls.crt=server.pem --
from-file=tls.key=server-key.pem --from-file=ca.crt=ca.pem --
type=kubernetes.io/tls
```

### Configure your cluster

After creating the Secret, reference it in your cluster configuration in the deploy/cr.yaml.

```yaml
spec:
  sslSecretName: my-cluster-ssl
```

Apply the configuration to update the cluster:

```bash
kubectl apply -f deploy/cr.yaml -n $NAMESPACE
```

This triggers your Pods to restart.

