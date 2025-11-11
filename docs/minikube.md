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
    kubectl apply -f deploy/bundle.yaml
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

Since Minikube runs on a single node, you need to adjust the default configuration. The Operator normally spreads pods across multiple nodes, but Minikube only has one node available.

Edit the `deploy/cr.yaml` file and set **all occurrences** of the `antiAffinityTopologyKey` key to `"none"`. This allows the Operator to run all pods on a single node.

Here's the example of the modified `deploy/cr.yaml` file:

```yaml
apiVersion: ps.percona.com/v1
kind: PerconaServerMySQL
metadata:
  name: minimal-cluster
  finalizers:
    - percona.com/delete-mysql-pods-in-order
spec:
  unsafeFlags:
    mysqlSize: true
    orchestrator: false
    orchestratorSize: false
    proxy: false
    proxySize: true
  crVersion: {{release}}
  secretsName: minimal-cluster-secrets
  sslSecretName: minimal-cluster-ssl
  updateStrategy: SmartUpdate
  upgradeOptions:
    versionServiceEndpoint: https://check.percona.com
    apply: disabled
  mysql:
    clusterType: group-replication
    autoRecovery: true
    image: percona/percona-server:{{ps84recommended}}
    imagePullPolicy: Always
    size: 1

    podDisruptionBudget:
      maxUnavailable: 1

    resources:
      requests:
        memory: 1Gi
      limits:
        memory: 2Gi

    affinity:
      antiAffinityTopologyKey: "none"

    exposePrimary:
      enabled: true

    volumeSpec:
      persistentVolumeClaim:
        resources:
          requests:
            storage: 2Gi

    gracePeriod: 600

  proxy:
    haproxy:
      enabled: true
      size: 1
      image: percona/haproxy:{{haproxyrecommended}}
      imagePullPolicy: Always

      podDisruptionBudget:
        maxUnavailable: 1

      resources:
        requests:
          memory: 1Gi
          cpu: 600m

      gracePeriod: 30

      affinity:
        antiAffinityTopologyKey: "none"
    router:
      enabled: false
      size: 1
      image: percona/percona-mysql-router:{{router84recommended}}
  backup:
    enabled: false
    image: percona/percona-xtrabackup:{{pxb84recommended}}
```

After making this change, deploy your MySQL cluster:

```bash
kubectl apply -f deploy/cr.yaml
```

??? example "Expected output"

    ```{.text .no-copy}
    perconaservermysql.ps.percona.com/ps-cluster1 created
    ```

This creates a cluster with three Percona Server for MySQL instances and one Orchestrator instance. For more configuration options, see the `deploy/cr.yaml` file and the [Custom Resource Options](operator.md) reference.

### Check the cluster status

The cluster creation process takes a few minutes. Monitor the status with:

```bash
kubectl get ps
```

Wait until the `STATE` column shows `ready`. This indicates your cluster is fully operational.

??? example "Expected output"

    ```{.text .no-copy}
    NAME       REPLICATION   ENDPOINT                   STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
    ps-cluster1   async         ps-cluster1-haproxy.default   ready   3       3              3                  5m50s
    ```

## Verify the cluster operation

It typically takes about ten minutes for the cluster to start. Once `kubectl get ps` shows the cluster status as `ready`, you can connect to it and start using your MySQL database.

{% include 'assets/fragments/connectivity.txt' %}
