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

## Rotate certificates

The TLS Secret stores two kinds of material. The Operator treats them differently:

* **Certificate Authority (CA)** (`ca.crt`) — the trust store every component uses to verify peers
* **Server certificate and key** (the leaf: `tls.crt` and `tls.key`) — the certificate `mysqld` presents to clients and other nodes

Rotating the leaf while the CA stays the same is the usual case. Rotating the CA is a separate procedure.

### Identify which Pods restart

Starting with version 1.3.0, the Operator reloads a new leaf into running `mysqld` processes. It still restarts MySQL Pods when the CA changes.

| What changed in the TLS Secret | MySQL Pods | HAProxy, MySQL Router, and Orchestrator Pods |
| --- | --- | --- |
| New `tls.crt` and `tls.key`, same `ca.crt` | Stay running. The Operator reloads TLS in `mysqld`. | Rolling restart |
| `ca.crt` changes, including a combined old+new CA | Rolling restart | Rolling restart |
| Secret has no `ca.crt` | Rolling restart for any certificate change | Rolling restart |

Keep the following in mind:

* The new leaf applies only to new connections. Existing connections keep the previous certificate until they reconnect.
* kubelet refreshes a mounted Secret on its own schedule. The Operator waits until the new files are on disk in every MySQL Pod, then reloads TLS.
* Deleting all TLS Secrets so the Operator can recreate them issues a new CA and restarts MySQL Pods.
* Versions older than 1.3.0 restart MySQL Pods for any TLS Secret change.

??? note "What happens under the hood for a leaf rotation"

    When the Operator sees a new leaf signed by the same CA, it does the following:

    * Leaves the MySQL StatefulSet unchanged. The hash on the MySQL Pod template covers only `ca.crt`.
    * Waits until kubelet has written the new `tls.crt` and `tls.key` into every MySQL Pod.
    * Runs `ALTER INSTANCE RELOAD TLS` on each `mysqld`.
    * Records the `percona.com/last-reloaded-tls` annotation on the MySQL StatefulSet.

    HAProxy, MySQL Router, and Orchestrator read certificates once at startup, so their Pod-template hash still covers the whole Secret. They restart.

See [Update certificates](tls-update.md) for how to rotate the leaf and how to rotate the CA.
