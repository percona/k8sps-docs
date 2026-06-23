# Data-at-rest encryption

Data-at-rest encryption ensures that data stored on disk remains protected even if the underlying storage is compromised. This process is transparent to your applications, meaning you don't need to change your application code. If an unauthorized user gains access to the storage, they can't read the data files.

Percona Operator for MySQL uses the `keyring_vault` plugin, shipped with Percona Server for MySQL, to encrypt tablespaces, backups and binlogs. It also uses [HashiCorp Vault :octicons-link-external-16:](https://www.vaultproject.io/) to securely store and manage master encryption keys, enabling automatic key rotation, audit logging, and compliance with enterprise security standards. This setup enhances the overall security posture of your MySQL cluster.

## Encryption flow

The encryption mechanism uses a two-tiered key architecture to secure your data:

* Each database instance has a master encryption key to encrypt tablespaces and binlogs. Master encryption key is stored separately from tablespace keys, in an external key management service like HashiCorp Vault.
* Each tablespace has a unique tablespace key to encrypt the data files (tables and indexes).

The data is encrypted before being written to disk. When you need to read the data, it's decrypted in memory for use and then re-encrypted before being written back to disk.

## Key rotation

Key rotation is replacing the old master encryption key with the new one. When a new master encryption key is created, it is stored in Vault and tablespace keys are re-encrypted with it. The entire dataset is not re-encrypted and this makes the key rotation a fast and lightweight operation.

Read more about key rotation in the [Rotate the master key :octicons-link-external-16:](https://docs.percona.com/percona-server/8.0/rotating-master-key.html).

## Backups and encryption

Percona Operator for MySQL uses Percona XtraBackup for backups and fully supports backing up [encrypted](encryption-setup.md) tablespaces. When your database uses the `keyring_vault` plugin, backup files retain that encryption layer as part of the physical backup data.

Starting with Operator 1.2.0, you can also [encrypt backup files in the object storage](backups-encrypted.md) independently of database encryption. This protects backup data even when live database encryption is not enabled.

!!! warning "Keep your encryption keys safe"

    To restore the encrypted data you must have the original key that was used to encrypt it. For data-at-rest encryption, this is the **the original Vault master encryption key**. For encrypted backups, this is the **backup encryption key** from the Kubernetes Secret.

    If either key is lost or rotated, your backups will be irrecoverable. Always ensure you have a secure and reliable process for managing and backing up encryption keys separately from your database backups.


## Next steps

[Configure data-at-rest encryption](encryption-setup.md){.md-button}