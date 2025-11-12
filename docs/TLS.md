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


