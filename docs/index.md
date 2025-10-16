# Percona Operator for MySQL based on Percona Server for MySQL

If you run MySQL and want easier operations, better reliability, and to use modern cloud workflows - Percona Operator for MySQL is here for you. 

Percona Operator for MySQL is based on [Percona Server for MySQL :octicons-link-external-16:](https://www.percona.com/doc/percona-server/LATEST/index.html), delivering enhanced performance, better observability and robust backup capabilities right out of the box.

Think of Percona Operator for MySQL as a MySQL automation engine inside your Kubernetes cluster. You define your desired setup in a YAML configuration file—and the Operator makes it real. It automates all database management operations for you, from deployment to scaling, backups and upgrades - everything you need to have a reliable, production ready database from day one.

The Operator constantly watches your cluster, understands its unique needs and automatically manages its lifecycle ensuring it operates as you intended.

!!! note ""

    Percona Operator for MySQL is General Availability with [**group replication**](architecture.md#replication-types-and-proxy-solutions). Asynchronous replication remains in Beta state, and we don't recommend it for production use yet.

[What's new in version {{release}}](ReleaseNotes/Kubernetes-Operator-for-PS-RN{{release}}.md){.md-button}

## Why to use the Operator

*  DBAs & SREs choose it because it reduces manual toil—no more babysitting clusters or writing custom failover logic.
*  DevOps teams use it to deploy MySQL consistently across environments, with infrastructure as code.
*  Architects choose it for its portability, reliability, and open source flexibility and benefit from no vendor lock-in.


## Ready to get started? 

Starting with the Operator is easy. Follow our documentation and you'll be set up in a minute.

[Quickstart guides :material-arrow-right:](quickstart.md){ .md-button }


<div data-grid markdown><div data-banner markdown>

## :fontawesome-solid-magnifying-glass: Discover the Operator { .title }

Learn the Operator's features, how it works and what it consists of.

[Features :material-arrow-right:](features.md){ .md-button }

</div><div data-banner markdown>

## :material-security: Security and encryption { .title }

Rest assured! Learn more about our security features designed to protect your valuable data.

[Security measures :material-arrow-right:](TLS.md){ .md-button }

</div><div data-banner markdown>

### :material-backup-restore: Backup management { .title }

Learn what you can do to maintain regular backups of your Percona Server for MySQL cluster.

[Backup management :material-arrow-right:](backups.md){ .md-button }

</div><div data-banner markdown>

### :material-frequently-asked-questions: Troubleshooting { .title }

Our comprehensive resources will help you overcome challenges, from everyday issues to specific doubts.

[Diagnostics :material-arrow-right:](debug.md){.md-button}
