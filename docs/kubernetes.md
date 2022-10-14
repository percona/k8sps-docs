# Install Percona Server for MySQL on Kubernetes


1. First of all, clone the percona-server-mysql-operator repository:

    ```bash
    $ git clone -b v{{ release }} https://github.com/percona/percona-server-mysql-operator
    cd percona-server-mysql-operator
    ```

    !!! note

        It is crucial to specify the right branch with `-b`
        option while cloning the code on this step. Please be careful.


2. Now Custom Resource Definition for Percona Server for MySQL should be created
    from the `deploy/crd.yaml` file. Custom Resource Definition extends the
    standard set of resources which Kubernetes “knows” about with the new
    items (in our case ones which are the core of the operator). [Apply it](https://kubernetes.io/docs/reference/using-api/server-side-apply/) as follows:

    ```bash
    $ kubectl apply --server-side -f deploy/crd.yaml
    ```

    This step should be done only once; it does not need to be repeated
    with the next Operator deployments, etc.

3. The next thing to do is to add the `mysql` namespace to Kubernetes,
    not forgetting to set the correspondent context for further steps:

    ```bash
    $ kubectl create namespace mysql
    $ kubectl config set-context $(kubectl config current-context) --namespace=mysql
    ```

    !!! note

        You can use different namespace name or even stay with the *Default* one.

4. Now RBAC (role-based access control) for Percona Server for MySQL should be set
    up from the `deploy/rbac.yaml` file. Briefly speaking, role-based access is
    based on specifically defined roles and actions corresponding to
    them, allowed to be done on specific Kubernetes resources (details
    about users and roles can be found in [Kubernetes
    documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings)).

    ```bash
    $ kubectl apply -f deploy/rbac.yaml
    ```

    !!! note

         Setting RBAC requires your user to have cluster-admin role
         privileges. For example, those using Google Kubernetes Engine can
         grant user needed privileges with the following command:
         `$ kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=$(gcloud config get-value core/account)`

    Finally it’s time to start the operator within Kubernetes:

    ```bash
    $ kubectl apply -f deploy/operator.yaml
    ```

5. Now that’s time to add the Percona Server for MySQL Users secrets to
    Kubernetes. They should be placed in the data section of the
    `deploy/secrets.yaml` file as logins and plaintext passwords for the user
    accounts (see [Kubernetes documentation](https://kubernetes.io/docs/concepts/configuration/secret/)
    for details).

    After editing is finished, users secrets should be created using the
    following command:

    ```bash
    $ kubectl create -f deploy/secrets.yaml
    ```

    More details about secrets can be found in [Users](users.md#users).


6. Now certificates should be generated. By default, the Operator generates
    certificates automatically, and no actions are required at this step. Still,
    you can generate and apply your own certificates as secrets according
    to the [TLS instructions](TLS.md#tls).

7. After the operator is started and user secrets are added, Percona Server for
    MySQL can be created at any time with the following command:

    ```bash
    $ kubectl apply -f deploy/cr.yaml
    ```

    Creation process will take some time. The process is over when both
    operator and replica set pod have reached their Running status.
    `kubectl get pods` output should look like this:

    ```text
    NAME                                                 READY   STATUS    RESTARTS        AGE
    cluster1-mysql-0                                     1/1     Running   0               7m6s
    cluster1-mysql-1                                     1/1     Running   1 (5m39s ago)   6m4s
    cluster1-mysql-2                                     1/1     Running   1 (4m40s ago)   5m7s
    cluster1-orc-0                                       2/2     Running   0               7m6s
    percona-server-for-mysql-operator-54c5c87988-xfmlf   1/1     Running   0               7m42s
    ```

8. Check connectivity to your newly created cluster. Run a MySQL client container
    and connect its console output to your terminal. The following command
    will do this, naming the new Pod `percona-client`:

    ```bash
    $ kubectl run -i --rm --tty percona-client --image=percona:8.0 --restart=Never -- bash -il
    percona-client:/$ mysql -h cluster1-mysql-primary -uroot -proot_password
    ```

    This command will connect you to the MySQL monitor.

    ```text
    mysql: [Warning] Using a password on the command line interface can be insecure.
    Welcome to the MySQL monitor.  Commands end with ; or \g.
    Your MySQL connection id is 2268
    Server version: 8.0.25-15 Percona Server (GPL), Release 15, Revision a558ec2

    Copyright (c) 2009-2021 Percona LLC and/or its affiliates
    Copyright (c) 2000, 2021, Oracle and/or its affiliates.

    Oracle is a registered trademark of Oracle Corporation and/or its
    affiliates. Other names may be trademarks of their respective
    owners.

    Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
    ```
