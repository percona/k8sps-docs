# Install Percona Server for MySQL on Kubernetes


1. First of all, clone the percona-server-mysql-operator repository:

    ```{.bash data-prompt="$"}
    $ git clone -b v{{ release }} https://github.com/percona/percona-server-mysql-operator
    cd percona-server-mysql-operator
    ```

    !!! note

        It is crucial to specify the right branch with `-b`
        option while cloning the code on this step. Please be careful.


2. Now Custom Resource Definition for Percona Server for MySQL should be created
    from the `deploy/crd.yaml` file. Custom Resource Definition extends the
    standard set of resources which Kubernetes “knows” about with the new
    items (in our case ones which are the core of the operator). [Apply it :octicons-link-external-16:](https://kubernetes.io/docs/reference/using-api/server-side-apply/) as follows:

    ```{.bash data-prompt="$"}
    $ kubectl apply --server-side -f deploy/crd.yaml
    ```

    This step should be done only once; it does not need to be repeated
    with the next Operator deployments, etc.

3. The next thing to do is to add the `mysql` namespace to Kubernetes,
    not forgetting to set the correspondent context for further steps:

    ```{.bash data-prompt="$"}
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
    documentation :octicons-link-external-16:](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings)).

    ```{.bash data-prompt="$"}
    $ kubectl apply -f deploy/rbac.yaml
    ```

    !!! note

         Setting RBAC requires your user to have cluster-admin role
         privileges. For example, those using Google Kubernetes Engine can
         grant user needed privileges with the following command:
         `$ kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=$(gcloud config get-value core/account)`

    Finally it’s time to start the operator within Kubernetes:

    ```{.bash data-prompt="$"}
    $ kubectl apply -f deploy/operator.yaml
    ```

5. Now that’s time to add the Percona Server for MySQL Users secrets to
    Kubernetes. They should be placed in the data section of the
    `deploy/secrets.yaml` file as logins and plaintext passwords for the user
    accounts (see [Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/secret/)
    for details).

    After editing is finished, users secrets should be created using the
    following command:

    ```{.bash data-prompt="$"}
    $ kubectl create -f deploy/secrets.yaml
    ```

    More details about secrets can be found in [Users](users.md).


6. Now certificates should be generated. By default, the Operator generates
    certificates automatically, and no actions are required at this step. Still,
    you can generate and apply your own certificates as secrets according
    to the [TLS instructions](TLS.md).

7. After the operator is started and user secrets are added, Percona Server for
    MySQL can be created at any time with the following command:

    ```{.bash data-prompt="$"}
    $ kubectl apply -f deploy/cr.yaml
    ```

    Creation process will take some time. The process is over when both
    operator and replica set pod have reached their Running status.
    `kubectl get pods` output should look like this:

    ```{.text .no-copy}
    NAME                                                 READY   STATUS    RESTARTS        AGE
    ps-cluster1-mysql-0                                     1/1     Running   0               7m6s
    ps-cluster1-mysql-1                                     1/1     Running   1 (5m39s ago)   6m4s
    ps-cluster1-mysql-2                                     1/1     Running   1 (4m40s ago)   5m7s
    ps-cluster1-orc-0                                       2/2     Running   0               7m6s
    percona-server-for-mysql-operator-54c5c87988-xfmlf   1/1     Running   0               7m42s
    ```

## Verify the cluster operation

{% include 'assets/fragments/connectivity.txt' %}
