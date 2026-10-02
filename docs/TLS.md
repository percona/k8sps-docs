# Transport Layer Security (TLS)

The Percona Operator for MySQL uses Transport Layer
Security (TLS) cryptographic protocol for the communication between the client application and the cluster.

You can configure TLS in these ways:

| Approach | Best for | Renewal |
| -------- | -------- | ------- |
| Operator-generated certificates (default) | Quick start, development | Manual |
| cert-manager with Operator-managed issuers | Automated TLS without external PKI | Automatic (cert-manager) |
| cert-manager with your existing `Issuer` or `ClusterIssuer` | Production clusters that use the organization's PKI | Automatic (cert-manager) |
| Manual Secrets | Full control, air-gapped or custom PKI workflows | Manual |

* By default, the Operator **generates long-term certificates** automatically during cluster creation if there are no certificate secrets available and cert-manager is not installed. Percona Server for MySQL requires all certificates issued by the same CA.

* The Operator can use an installed *cert-manager* to automatically **generate and renew short-term TLS certificates**. By default it creates namespace-scoped issuers in the database namespace. You can also point it at an existing `Issuer` or cluster-wide `ClusterIssuer` so certificates are signed by your organization's CA.

* You can generate TLS certificates manually or obtain them from some other issuer and provide them to the Operator as a Kubernetes Secret.

## TLS configuration

The following sections provide guidelines on how to:

* [Configure TLS using cert-manager](tls-cert-manager.md)
* [Generate certificates manually](tls-manual.md)
* [Update certificates](tls-update.md)
