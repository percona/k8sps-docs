# Transport Layer Security (TLS)

The Percona Operator for MySQL uses Transport Layer
Security (TLS) cryptographic protocol for the following types of communication:

* Internal - communication between Percona Server for MySQL instances,
* External - communication between the client application and the cluster.

The internal certificate is also used as an authorization method.

TLS security can be configured in several ways.

* By default, the Operator *generates long-term certificates* automatically if
    there are no certificate secrets available.
   
    ??? note "The Operator's self-signed issuer is local to the Operator Namespace"
        This self-signed issuer is created because Percona Distribution for MySQL
        requires all certificates issued by the same source.

* The Operator can use a specifically installed *cert-manager*, which will
    automatically *generate and renew short-term TLS certificate*
    
    ??? note "The *cert-manager* acts as a self-signed issuer and generates certificates" 
        It is still a self-signed issuer which allows you to deploy and use the
        Percona Operator without a separate certificate issuer.

* Certificates can be generated manually: obtained from some other issuer and
    provided to the Operator.

## Install and use the *cert-manager*

### About the *cert-manager*

A [cert-manager](https://cert-manager.io/docs/) is a Kubernetes certificate
management controller which is widely used to automate the management and
issuance of TLS certificates. It is community-driven, and open source.

When you have already installed *cert-manager*, nothing else is needed: just
deploy the Operator, and the Operator will request a certificate from the
*cert-manager*.

### Installation of the *cert-manager*

The steps to install the *cert-manager* are the following:

* Create a namespace,

* Disable resource validations on the cert-manager namespace,

* Install the cert-manager.

The following commands perform all the needed actions:

```bash
$ kubectl create namespace cert-manager
$ kubectl label namespace cert-manager certmanager.k8s.io/disable-validation=true
$ kubectl_bin apply -f https://github.com/jetstack/cert-manager/releases/download/v{{ certmanagerrecommended }}/cert-manager.yaml
```

After the installation, you can verify the *cert-manager* by running the following command:

```bash
$ kubectl get pods -n cert-manager
```

The result should display the *cert-manager* and webhook active and running.

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

You should generate certificates twice: one set is for external communications,
and another set is for internal ones. A secret created for the external use must
be added to `cr.yaml/spec/secretsName`. A certificate generated for internal
communications must be added to the `cr.yaml/spec/sslInternalSecretName`.

```bash
$ cat <<EOF | cfssl gencert -initca - | cfssljson -bare ca
{
  "CN": "Root CA",
  "key": {
    "algo": "rsa",
    "size": 2048
  }
}
EOF

$ cat <<EOF | cfssl gencert -ca=ca.pem  -ca-key=ca-key.pem - | cfssljson -bare server
{
  "hosts": [
    "${CLUSTER_NAME}-proxysql",
    "*.${CLUSTER_NAME}-proxysql-unready",
    "*.${CLUSTER_NAME}-pxc"
  ],
  "CN": "${CLUSTER_NAME}-pxc",
  "key": {
    "algo": "rsa",
    "size": 2048
  }
}
EOF

$ kubectl create secret generic my-cluster-ssl --from-file=tls.crt=server.pem --
from-file=tls.key=server-key.pem --from-file=ca.crt=ca.pem --
type=kubernetes.io/tls
```
