# Users

MySQL user accounts within the Cluster can be divided into two different groups:

* *application-level users*: the unprivileged user accounts,
* *system-level users*: the accounts needed to automate the cluster deployment
    and management tasks, such as Percona Server for MySQL Health checks.

As these two groups of user accounts serve different purposes, they are
considered separately in the following sections.

## Unprivileged users

There are no unprivileged (general purpose) user accounts created by
default. If you need general purpose users, run the following commands:

Start a temporary Percona MySQL client Pod and connect to MySQL in your cluster

```bash
kubectl run -it --rm percona-client --image=percona:8.0 --restart=Never -- mysql -hps-cluster1-mysql -uroot -proot_password
```

The following SQL command creates a new user `user1` with the password `password1`, and grants this user all privileges on all tables in the `database1` database. The `@'%'` means that the user can connect from any host.

```sql
CREATE USER 'user1'@'%' IDENTIFIED BY 'password1';
GRANT ALL PRIVILEGES ON database1.* TO 'user1'@'%';
FLUSH PRIVILEGES;
```

!!! note

    MySQL password here should not exceed 32 characters due to the [replication-specific limit introduced in MySQL 5.7.5 :octicons-link-external-16:](https://dev.mysql.com/doc/relnotes/mysql/5.7/en/news-5-7-5.html).

Verify that the user was created successfully. If successful, the
following command will let you successfully login to MySQL shell via
ProxySQL:

```bash
kubectl run -it --rm percona-client --image=percona:8.0 --restart=Never -- bash -il
percona-client:/$ mysql -h ps-cluster1-mysql-primary -uuser1 -ppassword1
mysql> SELECT * FROM database1.table1 LIMIT 1;
```

You may also try executing any simple SQL statement to ensure the
permissions have been successfully granted.

## System Users

To automate the deployment and management of the cluster components,
the Operator requires system-level Percona Server for MySQL users.

Credentials for these users are stored as a [Kubernetes Secrets :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/) object.
The Operator requires to be deployed before the Percona Server for MySQL is
started. 

!!! note

    The Operator will either use existing Secrets, or create a new
    Secrets object with randomly generated passwords if it didn’t
    exist. Also, starting from the Operator version 0.5, it will
    generate random passwords for system users not found in the
    existing Secrets object.

The name of the required Secrets (`ps-cluster1-secrets` by default)
should be set in the `spec.secretsName` option of the `deploy/cr.yaml`
configuration file.

The following table shows system users’ names and purposes.

!!! warning

    These users should not be used to run an application.

| User Purpose   | Username     | Password Secret Key | Description                                                            |
| -------------- | ------------ | ------------------- | ---------------------------------------------------------------------- |
| Admin          | root         | root                | Database administrative user, can be used by the application if needed |
| Orchestrator   | orchestrator | orchestrator        | Orchestrator administrative user                                       |
| Backup         | xtrabackup   | xtrabackup          | [User to run backups :octicons-link-external-16:](https://www.percona.com/doc/percona-xtrabackup/2.4/using_xtrabackup/privileges.html)     |
| Cluster Check  | clustercheck | clustercheck        | [User for liveness checks and readiness checks :octicons-link-external-16:](http://galeracluster.com/library/documentation/monitoring-cluster.html) |
| Monitoring     | monitor      | monitor             | User for internal monitoring purposes and [PMM agent :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/2/setting-up/server/index.html) |
| Operator Admin | operator     | operator            | Database administrative user, should be used only by the Operator      |
| Replication    | replication  | replication         | Administrative user needed for replication                             |
| PMM Server token | | pmmservertoken | [The service token used to access PMM Server :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/3/api/authentication.html) |

### YAML Object Format

The default name of the Secrets object for these users is
`ps-cluster1-secrets` and can be set in the CR for your cluster in
`spec.secretName` to something different. When you create the object yourself,
it should match the following simple format:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ps-cluster1-secrets
type: Opaque
stringData:
  root: root_password
  xtrabackup: backup_password
  monitor: monitor_password
  pmmserverkey: my_pmm_server_key
  operator: operator_password
  replication: replication_password
  orchestrator: orchestrator_password
  heartbeat: heartbeat_password
```

As you can see, because we use the `stringData` type when creating the Secrets
object, all values for each key/value pair are stated in plain text format
convenient from the user’s point of view. But the resulting Secrets
object contains passwords stored as `data` - i.e., base64-encoded strings.
If you want to update any field, you’ll need to encode the value into base64
format. To do this, you can run `echo -n "password" | base64 --wrap=0` (or just
`echo -n "password" | base64` in case of Apple macOS) in your local shell to get
valid values. For example, setting the Admin user’s password to `new_password`
in the `ps-cluster1-secrets` object can be done with the following command:

=== "in Linux"

    ```bash
    kubectl patch secret/ps-cluster1-secrets -p '{"data":{"root": "'$(echo -n new_password | base64 --wrap=0)'"}}'
    ```

=== "in macOS"

    ```bash
    kubectl patch secret/ps-cluster1-secrets -p '{"data":{"root": "'$(echo -n new_password | base64)'"}}'
    ```

### Password rotation policies and timing

When there is a change in user secrets, the Operator
creates the necessary transaction to change passwords. This rotation happens
almost instantly (the delay can be up to a few seconds), and it’s not needed to
take any action beyond changing the password.

!!! warning

    Please don’t change `secretName` option in CR, make changes inside
    the secrets object itself.

### Passwords with special characters

The Operator automatically generates passwords for user secrets with special characters to increase security. It uses the following set of characters:

* Uppercase letters (A–Z)
* Lowercase letters (a–z)
* Digits (0–9)
* Special symbols: `! $ % & ( ) * + , - . < = > ? @ [ ] ^ _ { } ~ #`

This character set has been carefully selected to ensure correct functioning of SQL, shell scripts, YAML files and connection strings.

To avoid issues in these contexts, the following characters are excluded: single quotes ('), double quotes ("), backslashes (\),
forward slashes (/), colons (:), pipes (|), semicolons (;) and backticks (`).

You can define passwords for user secrets yourself. When doing so, be sure to stick to the approved character set to ensure your services run smoothly.

### Marking System Users In MySQL

Starting with MySQL 8.0.16, a new feature called Account Categories has been
implemented, which allows us to mark our system users as such.
See [the official documentation on this feature :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/account-categories.html)
for more details.
