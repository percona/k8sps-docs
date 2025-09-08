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

## Backups and encryption

Percona Operator for MySQL uses Percona XtraBackup for backups and fully supports backing up encrypted data. The backups remain encrypted, ensuring your data is secure both on your live cluster and in your backup storage.

!!! warning "Keep your encryption keys safe"

    To restore from an encrypted backup, you **must have the original master encryption key**. If the encryption key is lost, your backups will be irrecoverable. Always ensure you have a secure and reliable process for managing and backing up your master encryption keys separately from your database backups.


## Next steps

[Configure data-at-rest encryption](encryption-setup.md){.md-button}

