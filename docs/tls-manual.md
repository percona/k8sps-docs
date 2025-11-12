# Generate certificates manually

You can generate TLS certificates manually instead of using the Operator's automatic certificate generation. This approach gives you full control over certificate properties and is useful for production environments with specific security requirements.

## What you'll create

When you follow the steps from this guide, you'll generate these certificate files:

* `server.pem` - Server certificate for MySQL nodes
* `server-key.pem` - Private key for the server certificate  
* `ca.pem` - Certificate Authority certificate
* `ca-key.pem` - Certificate Authority private key

Next, create the server TLS certificates using the CA keys, certs, and server details and then reference this Secret in the Custom Resource.

## Prerequisites

Before you start, make sure you have:

* `cfssl` and `cfssljson` tools installed on your system
* Your cluster name and namespace ready
* Access to your Kubernetes cluster

## Generate certificates

1. Replace `ps-cluster1` and `my-namespace` with your actual cluster name and namespace in the commands below:

    ```bash
    CLUSTER_NAME=ps-cluster1
    NAMESPACE=my-namespace
    ```

2. Generate a Certificate Authority (CA). You will use it to sign your server certificates.

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
    ```

    The output is two files: `ca.pem` (the CA certificate) and `ca-key.pem` (the CA private key).

3. Generate the Server Certificate using the CA. This command generates a server certificate and key, signed by your newly-created CA. The certificate will be valid for all hosts required by your cluster components.

    ```bash
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
    ```

    The outputs are `server.pem` (the server certificate) and `server-key.pem` (the server private key).

## Create the Kubernetes Secret from the generated certificates

This command packages the generated certificate and key files into a Kubernetes secret named `my-cluster-ssl` in your chosen namespace.

```bash
kubectl create secret generic my-cluster-ssl -n $NAMESPACE \
  --from-file=tls.crt=server.pem \
  --from-file=tls.key=server-key.pem \
  --from-file=ca.crt=ca.pem \
  --type=kubernetes.io/tls
```

## Configure your cluster

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
