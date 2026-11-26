> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Install Percona Server for MySQL cluster using kubectl

A Kubernetes Operator is a special type of controller introduced to simplify complex deployments. The Operator extends the Kubernetes API with custom resources.

The Percona Operator for MySQL is based on best practices for configuration and setup of a [Percona Server for MySQL](https://www.percona.com/mysql/software/percona-server) in a Kubernetes-based environment on-premises or in the cloud.

We recommend installing the Operator with the [kubectl](https://kubernetes.io/docs/tasks/tools/) command line utility. It is the universal way to interact with Kubernetes. Alternatively, you can install it using the [Helm](https://github.com/helm/helm) package manager.

[Install with kubectl](#prerequisites) [Install with Helm](https://docs.percona.com/percona-operator-for-mysql/1.3.0/helm.md)

## Prerequisites

To install Percona Server for MySQL cluster, you need the following:

1. The **kubectl** tool to manage and deploy applications on Kubernetes, included in most Kubernetes distributions. If not already installed, [follow its official installation instructions](https://kubernetes.io/docs/tasks/tools/install-kubectl/) .

1. A Kubernetes environment. You can deploy it on [Minikube](https://github.com/kubernetes/minikube) for testing purposes or using any cloud provider of your choice. Check the list of our [officially supported platforms](https://docs.percona.com/percona-operator-for-mysql/1.3.0/System-Requirements.md#supported-platforms).

   See also

   - [Set up Minikube](https://docs.percona.com/percona-operator-for-mysql/1.3.0/minikube.md)
   - [Create and configure the GKE cluster](https://docs.percona.com/percona-operator-for-mysql/1.3.0/gke.md)
   - [Set up Amazon Elastic Kubernetes Service](https://docs.percona.com/percona-operator-for-mysql/1.3.0/eks.md)
   - [Install on DigitalOcean Kubernetes](https://docs.percona.com/percona-operator-for-mysql/1.3.0/doks.md)

## Procedure

Here’s a sequence of steps to follow:

1. Create the Kubernetes namespace for your cluster. It is a good practice to isolate workloads in Kubernetes by installing the Operator in a custom namespace. Replace the `<namespace>` placeholder with your value.

   ```bash
   $ kubectl create namespace <namespace>
   ```

   Expected output

   ```text
   namespace/<namespace> was created
   ```

1. Deploy the Operator with the following command:

   ```bash
   $ kubectl apply -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v1.3.0/deploy/bundle.yaml  -n <namespace>
   ```

   Expected output

   ```text
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

   As the result you will have the Operator Pod up and running.

1. Deploy Percona Server for MySQL cluster:

   ```bash
   $ kubectl apply -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v1.3.0/deploy/cr.yaml -n <namespace>
   ```

   Expected output

   ```text
   perconaservermysql.ps.percona.com/ps-cluster1 created
   ```

1. Check the Operator and the database Pods status.

   ```bash
   $ kubectl get ps -n <namespace>
   ```

   Expected output

   ```text
   NAME       REPLICATION         ENDPOINT                   STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
   ps-cluster1   group-replication   ps-cluster1-haproxy.<namespace>   ready   3                                3        20m
   ```

   The creation process may take some time. When the process is over your cluster obtains the `ready` status.

You have successfully installed and deployed the Operator with default parameters.

The default configuration includes three HAProxy and three Percona Server for MySQL instances.

You can check the rest of the Operator’s parameters in the [Custom Resource options reference](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.md).

## Next steps

[Connect to Percona Server for MySQL](https://docs.percona.com/percona-operator-for-mysql/1.3.0/connect.md)
