# Install Percona Server for MySQL on DigitalOcean Kubernetes (DOKS)

This guide shows you how to deploy Percona Operator for MySQL on DigitalOcean Kubernetes (DOKS). The document assumes some experience with the platform. For more information on DOKS, see the [DigitalOcean Kubernetes documentation :octicons-link-external-16:](https://docs.digitalocean.com/products/kubernetes/).

## Prerequisites

Prepare the following before you create a cluster:

1. Install [doctl :octicons-link-external-16:](https://docs.digitalocean.com/reference/doctl/how-to/install/), the DigitalOcean command-line interface (CLI), to create and manage DOKS clusters.
2. Create a [DigitalOcean personal access token :octicons-link-external-16:](https://docs.digitalocean.com/reference/api/create-personal-access-token/) so `doctl` can access your account. After you create the token, authenticate `doctl`:

    ```bash
    doctl auth init
    ```

3. Install [kubectl :octicons-link-external-16:](https://kubernetes.io/docs/tasks/tools/install-kubectl/) to manage Kubernetes resources.

## Before you start

Check the [System requirements](System-Requirements.md) to confirm your environment meets the prerequisites. Use a cluster with at least three nodes.

## Create a DigitalOcean Kubernetes cluster

1. Decide on the following details:

    * Cluster name
    * Region where you deploy the cluster
    * Kubernetes version
    * Node size and count for the [node pool :octicons-link-external-16:](https://docs.digitalocean.com/products/kubernetes/how-to/add-node-pools/)

2. Create the cluster in the DigitalOcean control panel, or with `doctl`:

    ```bash
    doctl kubernetes cluster create <cluster-name> --region <region> --version <version> --size <node-size> --count 3
    ```

    Replace the `<cluster-name>`, `<region>`, `<version>` and `<node-size>` placeholders with your values. Cluster creation takes several minutes.

    For the full list of options, see [How to create Kubernetes clusters :octicons-link-external-16:](https://docs.digitalocean.com/products/kubernetes/how-to/create-clusters/).

3. Save the cluster credentials to your `kubeconfig` file so `kubectl` can connect:

    ```bash
    doctl kubernetes cluster kubeconfig save <cluster-name>
    ```

    For more connection options, see [How to connect to a DigitalOcean Kubernetes cluster :octicons-link-external-16:](https://docs.digitalocean.com/products/kubernetes/how-to/connect-to-cluster/).

## Install the Operator and deploy your MySQL cluster

1. Create a namespace and set it as the current context. Replace `<namespace>` with a descriptive name:

    ```bash
    kubectl create namespace <namespace>
    kubectl config set-context $(kubectl config current-context) --namespace=<namespace>
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        namespace/<namespace> created
        Context "<context>" modified.
        ```

2. Deploy the Operator:

    ```bash
    kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/bundle.yaml
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        customresourcedefinition.apiextensions.k8s.io/perconaservermysqlbackups.ps.percona.com created
        customresourcedefinition.apiextensions.k8s.io/perconaservermysqlrestores.ps.percona.com created
        customresourcedefinition.apiextensions.k8s.io/perconaservermysqls.ps.percona.com created
        serviceaccount/percona-server-mysql-operator created
        role.rbac.authorization.k8s.io/percona-server-mysql-operator-leaderelection created
        role.rbac.authorization.k8s.io/percona-server-mysql-operator created
        rolebinding.rbac.authorization.k8s.io/percona-server-mysql-operator-leaderelection created
        rolebinding.rbac.authorization.k8s.io/percona-server-mysql-operator created
        configmap/percona-server-mysql-operator-config created
        deployment.apps/percona-server-mysql-operator created
        ```

    The Operator Pod is now running.

3. Deploy the Percona Server for MySQL cluster.

    DOKS installs the DigitalOcean Container Storage Interface (CSI) driver and sets `do-block-storage` as the default StorageClass. The default cluster manifest uses that StorageClass. Set `storageClassName` only if you want a different volume type.

    ```bash
    kubectl apply -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/cr.yaml
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        perconaservermysql.ps.percona.com/ps-cluster1 created
        ```

4. Check the cluster status. Creation takes several minutes:

    ```bash
    kubectl get ps
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        NAME          REPLICATION         ENDPOINT                          STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
        ps-cluster1   group-replication   ps-cluster1-haproxy.<namespace>   ready   3                                3        20m
        ```

    When the `STATE` column shows `ready`, the cluster is running.

## Verify the cluster operation

When `kubectl get ps` shows the cluster status as `ready`, connect to the cluster.

{% include 'assets/fragments/connectivity.txt' %}

## Delete the DigitalOcean Kubernetes cluster

To delete the cluster, run the following command:

```bash
doctl kubernetes cluster delete <cluster-name>
```

Cluster deletion takes several minutes.

!!! warning

    Deleting the cluster deletes all data stored in it.
