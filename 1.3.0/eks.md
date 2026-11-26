> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Install Percona Distribution for MySQL on Amazon Elastic Kubernetes Service (EKS)

This guide shows you how to deploy Percona Operator for MySQL on Amazon Elastic Kubernetes Service (EKS). The document assumes some experience with Amazon EKS. For more information on the EKS, see the [Amazon EKS official documentation](https://aws.amazon.com/eks/) .

## Prerequisites

The following tools are used in this guide and therefore should be preinstalled:

1. **AWS Command Line Interface (AWS CLI)** for interacting with the different parts of AWS. You can install it following the [official installation instructions for your system](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) .
1. **eksctl** to simplify cluster creation on EKS. It can be installed along its [installation notes on GitHub](https://github.com/weaveworks/eksctl#installation) .
1. **kubectl** to manage and deploy applications on Kubernetes. Install it [following the official installation instructions](https://kubernetes.io/docs/tasks/tools/install-kubectl/) .

Also, you need to configure AWS CLI with your credentials according to the [official guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) .

## Before you start

Check the [System Requirements](https://docs.percona.com/percona-operator-for-mysql/1.3.0/System-Requirements.md) to ensure your environment meets the necessary prerequisites.

## Create the EKS cluster

1. To create your cluster, you will need the following data:

   - name of your EKS cluster,
   - AWS region in which you wish to deploy your cluster,
   - the amount of nodes you would like to have,
   - the desired ratio between [on-demand](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-on-demand-instances.html) and [spot](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html) instances in the total number of nodes.

   Note

   [spot](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html) instances are not recommended for production environment, but may be useful e.g. for testing purposes.

   After you have settled all the needed details, create your EKS cluster [following the official cluster creation instructions](https://docs.aws.amazon.com/eks/latest/userguide/create-cluster.html) .

1. After you have created the EKS cluster, you also need to [install the Amazon EBS CSI driver](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html) on your cluster. See the [official documentation](https://docs.aws.amazon.com/eks/latest/userguide/managing-ebs-csi.html) on adding it as an Amazon EKS add-on.

## Install the Operator and deploy your MySQL cluster

1. Create a namespace and set the context for the namespace. The resource names must be unique within the namespace and provide a way to divide cluster resources between users spread across multiple projects.

   So, create the namespace and save it in the namespace context for subsequent commands as follows (replace the `<namespace name>` placeholder with some descriptive name):

   ```bash
   kubectl create namespace <namespace name>
   kubectl config set-context $(kubectl config current-context) --namespace=<namespace name>
   ```

   At success, you will see the message that namespace/ was created, and the context was modified.

1. Use the following `git clone` command to download the correct branch of the percona-server-mysql-operator repository:

   ```bash
   git clone -b v1.3.0 https://github.com/percona/percona-server-mysql-operator
   ```

   After the repository is downloaded, change the directory to run the rest of the commands in this document:

   ```bash
   cd percona-server-mysql-operator
   ```

1. Deploy the Operator [using](https://kubernetes.io/docs/reference/using-api/server-side-apply/) the following command:

   ```bash
   kubectl apply --server-side -f deploy/bundle.yaml
   ```

   The following confirmation is returned:

   ```text
   customresourcedefinition.apiextensions.k8s.io/perconaserverformysqlbackups.ps.percona.com created
   customresourcedefinition.apiextensions.k8s.io/perconaserverformysqlrestores.ps.percona.com created
   customresourcedefinition.apiextensions.k8s.io/perconaserverformysqls.ps.percona.com created
   serviceaccount/percona-server-for-mysql-operator created
   role.rbac.authorization.k8s.io/percona-server-for-mysql-operator-leader-election-role created
   role.rbac.authorization.k8s.io/percona-server-for-mysql-operator-role created
   rolebinding.rbac.authorization.k8s.io/percona-server-for-mysql-operator-leader-election-rolebinding created
   rolebinding.rbac.authorization.k8s.io/percona-server-for-mysql-operator-rolebinding created
   configmap/percona-server-for-mysql-operator-config created
   deployment.apps/percona-server-for-mysql-operator created
   ```

1. The operator has been started, and you can create the Percona Distribution for MySQL cluster:

   Warning

   Starting with 1.30, Amazon EKS no longer automatically applies the default annotation for the `gp2` StorageClass to newly created clusters.

   You need to specify the storageClassName explicitly in `deploy/cr.yaml`:

   ```text
   mysql:
     ...
     volumeSpec:
       persistentVolumeClaim:
         storageClassName: gp2
         resources:
           requests:
             storage: 20Gi
   ```

   ```bash
   kubectl apply -f deploy/cr.yaml
   ```

   The process could take some time. The return statement confirms the creation:

   ```text
   perconaserverformysql.ps.percona.com/ps-cluster1 created
   ```

## Verify the cluster operation

To connect to Percona Server for MySQL, use the connection Secret that the Operator creates for the `root` user. It is named `<cluster_name>-psuser-root` (by default, `ps-cluster1-psuser-root`) and contains hostnames, ports, credentials, and ready-to-use connection URIs. Read [Connection secrets](https://docs.percona.com/percona-operator-for-mysql/1.3.0/connection-secrets.md) for the full reference.

Here’s how to connect:

1. Export the namespace, cluster name and the Secret name as environment variables:

   ```bash
   export NAMESPACE=my-namespace
   export CLUSTER_NAME=ps-cluster1
   export SECRET_NAME=${CLUSTER_NAME}-psuser-root
   ```

   Replace `ps-cluster1` with the [name of your cluster](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.md#metadata-name) if you changed it during installation.

1. List the Secrets objects.

   ```bash
   $ kubectl get secrets -n $NAMESPACE
   ```

   Look for the Secret named `<cluster_name>-psuser-root`. By default, it is `ps-cluster1-psuser-root`.

1. Retrieve the user credentials from the Secret:

   ```bash
   kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" \
   -o jsonpath='{.data.user}' | base64 --decode && echo
   kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" \
   -o jsonpath='{.data.password}' | base64 --decode && echo
   ```

1. Run a container with the `mysql` tool and connect its console output to your terminal:

   ```bash
   kubectl run -i --rm --tty percona-client --image=percona/percona-server:8.4 --restart=Never -- bash -il
   ```

   It may require some time to execute the command and deploy the corresponding Pod.

1. Now run `mysql` tool in the `percona-client` command shell using the password obtained from the Secret instead of the `<root password>` placeholder. The command will look different depending on whether the cluster uses load balancing with [HAProxy](https://docs.percona.com/percona-operator-for-mysql/1.3.0/haproxy-conf.md) (the default behavior) or uses [MySQL Router](https://docs.percona.com/percona-operator-for-mysql/1.3.0/router-conf.md) (can be used with Group Replication clusters):

   **If using HAProxy (default)**

   ```bash
   mysql -h ps-cluster1-haproxy -uroot -p<root password>
   ```

   **If using MySQL Router**

   ```bash
   mysql -h ps-cluster1-router -uroot -p<root password>
   ```

   Expected output

   ```text
   mysql: [Warning] Using a password on the command line interface can be insecure.
   Welcome to the MySQL monitor.  Commands end with ; or \g.
   Your MySQL connection id is 1665
   Server version: 8.4.11-11.1 Percona Server (GPL), Release 6, Revision dbba4396

   Copyright (c) 2009-2026 Percona LLC and/or its affiliates
   Copyright (c) 2000, 2026, Oracle and/or its affiliates.

   Oracle is a registered trademark of Oracle Corporation and/or its
   affiliates. Other names may be trademarks of their respective
   owners.

   Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

   mysql>
   ```

   The following example uses the MySQL prompt to check the `max_connections` variable:

   ```sql
   SHOW VARIABLES LIKE "max_connections";
   ```

   Expected output

   ```text
   +-----------------+-------+
   | Variable_name   | Value |
   +-----------------+-------+
   | max_connections | 158   |
   +-----------------+-------+
   1 row in set (0.02 sec)

   mysql>
   ```

1. You can also check whether you can connect to MySQL from the outside with the help of the `kubectl port-forward` command as follows:

   ```bash
   kubectl port-forward svc/ps-cluster1-mysql-primary 3306:3306 &
   mysql -h 127.0.0.1 -P 3306 -uroot -p<root password>
   ```
