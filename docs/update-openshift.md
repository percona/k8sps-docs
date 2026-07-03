# Upgrade the Operator and CRD via Operator Lifecycle Manager (OLM)

## Considerations for using OpenShift 4.22

Starting with OpenShift 4.22, the way images with not fully qualified names are pulled has changed for repositories that share the same repository name on DockerHub and Red Hat Marketplace. By default the tags are pulled from Red Hat Marketplace. Specifying not fully qualified image names may result in the `ImagePullBackOff` error.

* **OLM installation:** Images are provided with the fully qualified names and are pulled from the Red Hat Marketplace/DockerHub registry.
* **Manual install/update with default manifests:** Images must use the `docker.io` registry prefix to guarantee successful download from the DockerHub `percona-xtradb-cluster` repository. See the [Update via the command-line interface](#update-via-the-command-line-interface) section for the exact steps.


The upgrade on OpenShift consists of two steps:

* Upgrade the Operator Deployment
* [Upgrade the database cluster](update-db.md)

## Upgrade the Operator via Operator Lifecycle Manager (OLM)

You can upgrade the Operator Deployment for MySQL that was [installed on the OpenShift platform using OLM](openshift.md#install-percona-server-for-mysql-on-openshift) directly through the Operator Lifecycle Manager.

If you know the OLM upgrade workflow, jump to the [update Deployment steps](#upgrade-the-operator).

### Understand how OLM applies Operator upgrades

OLM manages the Operator using a resource called a `ClusterServiceVersion` (CSV).
Each CSV represents a specific version of the Operator and contains:

* the Operator Deployment specification
* required RBAC permissions
* CRD definitions
* metadata and examples

When a new Operator version is available and the upgrade is approved, OLM installs the new CSV and reconciles the Operator Deployment to match it.
The following items are replaced with the values defined in the new CSV:

* container image
* command and arguments
* labels and annotations
* probes
* most Deployment fields

If you previously customized the Operator Deployment manually, these changes are overwritten during the upgrade.

The CRD may be updated too, if the new Operator version introduces schema changes.
However, OLM doesn't modify the `PerconaServerMySQL` Custom Resource. It remains unchanged and continues running with its current configuration. For how to update it, refer to [Update Percona Server for MySQL](update-db.md).

#### Persisting custom Operator configuration

If you need to customize the Operator Deployment (for example, to adjust resource limits or set environment variables), you can do it through the Subscription.

A Subscription is the OLM resource that defines which operator you want to install and how you want it to be upgraded. A Subscription connects your cluster to an Operator package in a CatalogSource and ensures that OLM continuously manages that Operator according to your chosen update strategy.

Here's how you can customize the Operator Deployment. This example command sets an environment variable for the Operator:

```bash
kubectl patch subscription percona-server-mysql-operator -n <namespace> \
  --type merge \
  -p '{"spec":{"config":{"env":[{"name":"LOG_LEVEL","value":"DEBUG"}]}}}'
```

OLM supports overriding only the following fields through the Subscription:

* env
* envFrom
* volumes
* volumeMounts
* resources
* nodeSelector
* tolerations
* affinity

These overrides are applied on top of the CSV and persist across upgrades. All other fields are overridden by the values from the new CSV during the Operator Deployment upgrade.

### Upgrade the Operator

1. Log in to the OpenShift web console and check the list of installed Operators in your namespace to see if upgrades are available.

    ![image](assets/images/olm4.svg)

2. Click the "Upgrade available" link to review details, click "Preview InstallPlan," and then click "Approve" to upgrade the Operator.

### Update via the command-line interface

The following steps apply if you plan to use OpenShift 4.22. See the [Considerations for using OpenShift 4.22](#considerations-for-using-openshift-422).

1. Check all clusters managed by the Operator to see if `initContainer.image` is set.

    * If defined: skip the next step.
    * If undefined: proceed to step 2.

2. Apply a patch to the clusters with undefined `initContainer.image` to define this image with the `docker.io` registry in the image path:

    ```bash
    kubectl patch ps ps-cluster1 --type=merge --patch '{
      "spec": {
        "initcontainer": {
              "image": "docker.io/perconpercona-server-mysql-operator:{{release}}"
        }
      }
    }'
    ```

    **Important!** This command triggers the restart of your clusters. Wait till they restart and report the `Ready` status.

3. Update the Operator deployment and specify the `docker.io` registry name in the image path:

    ```bash
    kubectl patch deployment percona-server-mysql-operator \
    -p'{"spec":{"template":{"spec":{"containers":[{"name":"percona-server-mysql-operator","image":"docker.io/percona/percona-server-mysql-operator:{{release}}"}]}}}}'
    ```

4. Update the Custom Resource version and the database cluster. Specify the `initContainer` image with the `docker.io` registry name in the path.
   
    The following example shows how to update Percona Server for MySQL cluster 8.4 with Group Replication and HAProxy:

    ```bash
    kubectl patch ps ps-cluster1 --type=merge --patch '{
      "spec": {
        "crVersion": "{{release}}",
        "initContainer": "docker.io/percona/percona-server-mysql-operator:{{release}}",
        "mysql":{ "image": "docker.io/percona/percona/percona-server:{{ ps84recommended }}" },
        "proxy":{
            "haproxy":{ "image": "percona/haproxy:{{haproxyrecommended}}" }
        },
        "backup":{ "image": "docker.io/percona/percona-xtrabackup:{{ pxb84recommended }}" },
        "toolkit":{ "image": "percona/percona-toolkit:{{ptrecommended}}" },
        "pmm":{ "image": "docker.io/percona/pmm-client:{{ pmm3recommended }}" }
      }
    }'
    ```
   
