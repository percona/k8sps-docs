# Percona Operator for MySQL based on Percona Server for MySQL

Percona Operator for MySQL automates managing your MySQL databases on Kubernetes, making this process simple, reliable, and worry-free. Built on [Percona Server for MySQL :octicons-link-external-16:](https://www.percona.com/doc/percona-server/LATEST/index.html), the Operator brings enterprise-grade reliability,
performance, and observability right out of the box.

With Percona Operator for MySQL, you can quickly set up, scale, and protect your databases using easy-to-understand configuration files. The Operator takes care of everyday tasks such as deployment, backups, updates, and failover, so you can focus on your applications and your business, not on manual database management.

!!! note ""
    Percona Operator for MySQL is generally available with [**group replication**](architecture.md#group-replication). Asynchronous replication is still in tech preview and is not recommended for production yet.

[Get started :material-arrow-down:](#get-started-today){ .md-button }
[See what's new in version {{release}}](ReleaseNotes/Kubernetes-Operator-for-PS-RN{{release}}.md){.md-button}

## Why choose Percona Operator for MySQL?

### Deploy and manage with ease

No need for complicated scripts or manual setups. Define your database
requirements in a YAML file, and have the Operator to automatically create, configure,
and manage your entire MySQL cluster. 

### Built for reliability

From day one, your database comes with robust features you need for production: high availability, automated backups, built-in monitoring, and strong security. Everything is ready to use right out of the box.

### Cloud-native by design

Whether you use AWS, Google Cloud, Azure, or any other Kubernetes platform, the Operator fits right in. Enjoy a consistent, cloud-native MySQL experience everywhere.

## Get started today

Set up Percona Operator for MySQL in just a few minutes. Start with our simple guides and begin managing your databases with confidence.

[Quickstart guide :material-arrow-right:](quickstart.md){ .md-button }

<div data-grid markdown><div data-banner markdown>

## :fontawesome-solid-magnifying-glass: Discover the Operator { .title }

Learn about all the features Percona Operator for MySQL offers, how it works, and how it can help you.

[Features :material-arrow-right:](features.md){ .md-button }

</div><div data-banner markdown>

## :material-security: Security you can trust { .title }

Your data safety is our priority. See how our Operator protects your information with advanced security and encryption options.

[Security features :material-arrow-right:](TLS.md){ .md-button }

</div><div data-banner markdown>

### :material-backup-restore: Backup management { .title }

Learn how to keep your MySQL databases backed up and ready for a quick restore whenever you need it.

[Backup options :material-arrow-right:](backups.md){ .md-button }

</div><div data-banner markdown>

### :material-frequently-asked-questions: Troubleshooting { .title }

Need assistance? Our troubleshooting guides cover common questions and step-by-step solutions.

[Diagnostics :material-arrow-right:](debug.md){.md-button}
