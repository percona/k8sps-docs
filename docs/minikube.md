# Install Percona Server for MySQL on Minikube

[Minikube :octicons-link-external-16:](https://github.com/kubernetes/minikube) lets you run a Kubernetes cluster locally without a cloud provider. It works on Linux, Windows, and macOS using a hypervisor like VirtualBox, KVM/QEMU, VMware Fusion, Hyper-V, or Docker. This makes it perfect for testing the Operator before deploying it in a cloud or in production

## Prerequisites

Before you begin, you need to [install Minikube :octicons-link-external-16:](https://kubernetes.io/docs/tasks/tools/install-minikube/) on your system. The installation includes three components:

1. **kubectl** - the Kubernetes command-line tool
2. **A hypervisor** - if you don't already have one installed
3. **Minikube** - the Minikube package itself

After installing Minikube, start it with increased resources to ensure the Operator runs smoothly:

```bash
minikube start --memory=4096 --cpus=3
```

This command downloads the necessary virtualized images, then initializes and starts your local Kubernetes cluster. The `--memory=4096` and `--cpus=3` parameters allocate more resources to the virtual machine, which helps the Operator run reliably.

!!! tip "Optional: Kubernetes Dashboard"

    You can optionally start the Kubernetes dashboard to visualize your cluster. Run:

    ```bash
    minikube dashboard
    ```

    This opens the dashboard in your default web browser, giving you a visual view of your cluster's state.

## Install the Operator 

1. Clone the repository and navigate into it:

    ```bash
    git clone -b v{{ release }} https://github.com/percona/percona-server-mysql-operator
    cd percona-server-mysql-operator
    ```

2. Deploy the Operator to your Minikube cluster

    ```bash
    kubectl apply--server-side -f deploy/bundle.yaml
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

## Configure and deploy your MySQL cluster

Since Minikube runs on a single node, the default configuration doesn't fit. Use the minimal configuration adjusted for Minikube environment.

```bash
kubectl apply -f deploy/cr-minimal.yaml
```

??? example "Expected output"

    ```{.text .no-copy}
    perconaservermysql.ps.percona.com/ps-cluster1 created
    ```

This creates a group-replication cluster with one Percona Server for MySQL instances and one HAProxy instance. For more configuration options, see the `deploy/cr.yaml` file and the [Custom Resource Options](operator.md) reference.

### Check the cluster status

The cluster creation process takes a few minutes. Monitor the status with:

```bash
kubectl get ps
```

Wait until the `STATE` column shows `ready`. This indicates your cluster is fully operational.

??? example "Expected output"

    ```{.text .no-copy}
    NAME           REPLICATION         ENDPOINT                   STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
    ps-cluster1   group-replication    ps-cluster1-haproxy.default   ready   1                     1                  5m50s
    ```

## Verify the cluster operation

It typically takes about ten minutes for the cluster to start. Once `kubectl get ps` shows the cluster status as `ready`, you can connect to it and start using your MySQL database.

{% include 'assets/fragments/connectivity.txt' %}
