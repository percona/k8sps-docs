# Upgrade the Operator from version 0.8.0 to 0.9.0

The upgrade flow for this Operator version differs due to a number of internal changes.

## Upgrade the CRD and the Operator

1. Find the name of the MySQL primary Pod. For example, you can do it by quering MySQL. Get access to MySQL Shell with the following command (substitute your real cluster name instead of `ps-cluster1`, if needed, and use your namespace instead of the `<namespace_name>` placeholder):

    ```bash
    kubectl exec -n <namespace_name> -it ps-cluster1-mysql-0 -- bash -c 'mysqlsh -u operator -p$(/etc/mysql/mysql-users-secret/operator)'
    ```

    ??? example "Expected output"

        ```text
        Defaulted container "mysql" out of: mysql, xtrabackup, mysql-init (init)
        MySQL Shell 8.0.36

        Copyright (c) 2016, 2024, Oracle and/or its affiliates.
        Oracle is a registered trademark of Oracle Corporation and/or its affiliates.
        Other names may be trademarks of their respective owners.

        Type '\help' or '\?' for help; '\quit' to exit.
        WARNING: Using a password on the command line interface can be insecure.
        Creating a session to 'operator@localhost'
        Fetching schema names for auto-completion... Press ^C to stop.
        Your MySQL connection id is 1092 (X protocol)
        Server version: 8.0.36-28 Percona Server (GPL), Release 28, Revision 47601f19
        No default schema selected; type \use <schema> to set one.
        ```

    Now, execute the following request in MySQL Shell:

    ```sh
    dba.getCluster().status().defaultReplicaSet.primary
    ```

    ???+ example "Expected output"

        ```text
        ps-cluster1-mysql-0.ps-cluster1-mysql.default:3306
        ```

2. Exec into the `mysql` on this primary Pod (`ps-cluster1-mysql-0` in the above example):

    ```bash
    kubectl exec -n <namespace_name> -it ps-cluster1-mysql-0 -- bash -c 'mysql -u operator -p$(/etc/mysql/mysql-users-secret/operator)'
    ```

3. Create the `replication` user with some password (we use `<change-this>` password placeholder in this example):

    ```mysql
    CREATE USER 'replication'@'%' IDENTIFIED by '<change-this>';
    ```

4. Encode the replication user's password with base64:

    === "in Linux"

        ```bash
        echo -n '<change-this>' | base64 --wrap=0
        ```

        ??? example "Expected output"

            ```text
            PGNoYW5nZS10aGlzPg==
            ```

    === "in macOS"

        ```bash
        echo -n '<change-this>' | base64
        ```    

        ??? example "Expected output"

            ```text
            PGNoYW5nZS10aGlzPg==
            ```        

6. Patch the secrets to add this replication password:

    ```bash
    kubectl patch -n <namespace_name> secrets ps-cluster1-secrets -p '{"data": { "replication": "PGNoYW5nZS10aGlzPg==" } }'
    ```

    ??? example "Expected output"

        ```text
        secret/ps-cluster1-secrets patched
        ```

    ``` bash
    kubectl patch -n <namespace_name> secrets internal-ps-cluster1 -p '{"data": { "replication": "PGNoYW5nZS10aGlzPg==" } }'
    ```

    ??? example "Expected output"

        ```text
        secret/internal-ps-cluster1 patched
        ```

## Upgrade the database

You should [delete your cluster](delete.md), not [cleaning up](delete.md#clean-up-resources) Persistent Volume Claims, and recreate it back (by applying the `deploy/cr.yaml` file from the new release with all needed edits related to your cluster configuration).
