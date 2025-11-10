# Install Percona Distribution for MySQL on Amazon Elastic Kubernetes Service (EKS)

This guide shows you how to deploy Percona Operator for MySQL on Amazon Elastic Kubernetes Service (EKS). The document assumes some experience with Amazon EKS. For more information on the EKS, see the [Amazon EKS official documentation :octicons-link-external-16:](https://aws.amazon.com/eks/).

## Prerequisites

The following tools are used in this guide and therefore should be preinstalled:

1. **AWS Command Line Interface (AWS CLI)** for interacting with the different
    parts of AWS. You can install it following the [official installation instructions for your system :octicons-link-external-16:](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).

2. **eksctl** to simplify cluster creation on EKS. It can be installed
    along its [installation notes on GitHub :octicons-link-external-16:](https://github.com/weaveworks/eksctl#installation).

3. **kubectl**  to manage and deploy applications on Kubernetes. Install
    it [following the official installation instructions :octicons-link-external-16:](https://kubernetes.io/docs/tasks/tools/install-kubectl/).

Also, you need to configure AWS CLI with your credentials according to the [official guide :octicons-link-external-16:](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

## Create the EKS cluster

1. To create your cluster, you will need the following data:

    * name of your EKS cluster,
    * AWS region in which you wish to deploy your cluster,
    * the amount of nodes you would like to have,
    * the desired ratio between [on-demand :octicons-link-external-16:](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-on-demand-instances.html)
        and [spot :octicons-link-external-16:](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html)
        instances in the total number of nodes.

    !!! note

        [spot :octicons-link-external-16:](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html)
        instances are not recommended for production environment, but may be useful
        e.g. for testing purposes.

    After you have settled all the needed details, create your EKS cluster [following the official cluster creation instructions :octicons-link-external-16:](https://docs.aws.amazon.com/eks/latest/userguide/create-cluster.html).

2. After you have created the EKS cluster, you also need to [install the Amazon EBS CSI driver :octicons-link-external-16:](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html) on your cluster. See the [official documentation :octicons-link-external-16:](https://docs.aws.amazon.com/eks/latest/userguide/managing-ebs-csi.html) on adding it as an Amazon EKS add-on.

## Install the Operator and deploy your MySQL cluster

1. Create a namespace and set the context for the namespace. The resource names must be unique within the namespace and provide a way to divide cluster resources between users spread across multiple projects.

    So, create the namespace and save it in the namespace context for subsequent commands as follows (replace the `<namespace name>` placeholder with some descriptive name):

    ```bash
    kubectl create namespace <namespace name>
    kubectl config set-context $(kubectl config current-context) --namespace=<namespace name>
    ```

    At success, you will see the message that namespace/<namespace name> was created, and the context was modified.

2. Use the following `git clone` command to download the correct branch of the percona-server-mysql-operator repository:

    ```bash
    git clone -b v{{ release }} https://github.com/percona/percona-server-mysql-operator
    ```

    After the repository is downloaded, change the directory to run the rest of the commands in this document:

    ```bash
    cd percona-server-mysql-operator
    ```

3. Deploy the Operator [using :octicons-link-external-16:](https://kubernetes.io/docs/reference/using-api/server-side-apply/) the following command:

    ```bash
    kubectl apply --server-side -f deploy/bundle.yaml
    ```

    The following confirmation is returned:

    ```{.text .no-copy}
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

4. The operator has been started, and you can create the Percona Distribution for MySQL cluster:

    !!! warning

        Starting with 1.30, Amazon EKS no longer automatically applies the default annotation for the `gp2` StorageClass to newly created clusters.

        You need to specify the storageClassName explicitly in `deploy/cr.yaml`:

        ```
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

    The process could take some time.
    The return statement confirms the creation:

    ```{.text .no-copy}
    perconaserverformysql.ps.percona.com/ps-cluster1 created
    ```

## Verify the cluster operation

{% include 'assets/fragments/connectivity.txt' %}


6. You can also check whether you can connect to MySQL from the outside
    with the help of the `kubectl port-forward` command as follows:

    ```bash
    kubectl port-forward svc/ps-cluster1-mysql-primary 3306:3306 &
    mysql -h 127.0.0.1 -P 3306 -uroot -p<root password>
    ```
