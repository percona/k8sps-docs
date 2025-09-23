# Delete Percona Operator for MySQL based on Percona Server for MySQL

You may have different reasons to clean up your Kubernetes environment: moving from trial deployment to a production one, testing experimental configurations and the like. In either case, you need to remove some (or all) of these objects:

* Percona Server for MySQL managed by the Operator
* Percona Operator for MySQL itself
* Custom Resource Definition deployed with the Operator
* Resources like PVCs and Secrets

## Delete the database cluster

To delete the database cluster means to delete the Custom Resource associated with it.

!!! note

    There are 2 [finalizers :octicons-link-external-16:](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#finalizers) defined in the Custom Resource, which define whether to delete or preserve  TLS-related objects and data volumes when the cluster is deleted.

    * `finalizers.percona.com/delete-mysql-pvc`: if present, [Persistent Volume Claims :octicons-link-external-16:](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) for the database cluster Pods and all user Secrets are deleted along with the cluster deletion. 
    * `finalizers.percona.com/delete-ssl`: if present, objects, created for SSL (Secret, certificate, and issuer) are deleted along with the cluster deletion.

    These finalizers are off by default in the `deploy/cr.yaml` configuration file, and it allows you to recreate the cluster without losing data, credentials for the system users, etc. You can always [delete TLS-related objects and PVCs manually](#clean-up-resources), if needed. 

The steps are the following:
{.power-number}

1. List the Custom Resources. Replace the `<namespace>` placeholder with your value

    ```{.bash data-prompt="$"}
    $ kubectl get ps -n <namespace>
    ```

2. Delete the Custom Resource with the name of your cluster

    ```{.bash data-prompt="$"}
    $ kubectl delete ps <cluster_name> -n <namespace>
    ```

    ??? example "Sample output"

        ```{.text .no-copy}
        perconaservermysql.ps.percona.com "cluster1" deleted
        ```

    It may take a while to stop and delete the cluster. 


3. Check that the cluster is deleted by listing the Custom Resources again:

    ```{.bash data-prompt="$"}
    $ kubectl get ps -n <namespace>
    ```

    ??? example "Sample output"

        ```{.text .no-copy}
        No resources found in <namespace> namespace.
        ```

## Delete the Operator

Choose the instructions relevant to the way you installed the Operator. 

=== "kubectl"

    To uninstall the Operator, delete the [Deployments :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) related to it.
    {.power-number}

    1. List the deployments. Replace the `<namespace>` placeholder with your namespace.

        ```{.bash data-prompt="$"}
        $ kubectl get deploy -n <namespace>
        ```

        ??? example "Sample output"

            ```{.text .no-copy}
            NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
            percona-server-mysql-operator   1/1     1            1           42m
            ```

    2. Delete the `percona-*` deployment

        ```{.bash data-prompt="$"}
        $ kubectl delete deploy percona-server-mysql-operator -n <namespace>
        ```

        ??? example "Sample output"

            ```{.text .no-copy}
            deployment.apps "percona-server-mysql-operator" deleted
            ```

    3. Check that the Operator is deleted by listing the Pods. As a result you should have no Pods related to it.

        ```{.bash data-prompt="$"}
        $ kubectl get pods -n <namespace>
        ```
        
        ??? example "Sample output"

            ```{.text .no-copy}
            No resources found in <namespace> namespace.
            ```

    4. If you are not just deleting the Operator and Percona Server for MySQL from a specific namespace, but want to clean up your entire Kubernetes environment, you can also delete the [CustomRecourceDefinitions (CRDs) :octicons-link-external-16:](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions).

        <i warning>:material-alert: Warning:</i> CRDs in Kubernetes are non-namespaced but are available to the whole environment. This means that you shouldn’t delete CRDs if you still have the Operator and database cluster in some namespace.

        Get the list of CRDs. 

        ```{.bash data-prompt="$"}
        $ kubectl get crd
        ```

        ??? example "Sample output"

            ```{.text .no-copy}
            NAME                                        CREATED AT
            perconaservermysqlbackups.ps.percona.com    2025-02-07T20:10:42Z
            perconaservermysqlrestores.ps.percona.com   2025-02-07T20:10:42Z
            perconaservermysqls.ps.percona.com          2025-02-07T20:10:42Z
            ```

    5. Delete the `percona*.ps.percona.com` CRDs

        ```{.bash data-prompt="$"}
        $ kubectl delete crd perconaservermysqlbackups.ps.percona.com perconaservermysqlrestores.ps.percona.com perconaservermysqls.ps.percona.com
        ``` 

        ??? example "Sample output"

            ```{.text .no-copy}
            customresourcedefinition.apiextensions.k8s.io "perconaservermysqlbackups.ps.percona.com" deleted
            customresourcedefinition.apiextensions.k8s.io "perconaservermysqlrestores.ps.percona.com" deleted
            customresourcedefinition.apiextensions.k8s.io "perconaservermysqls.ps.percona.com" deleted
            ```

=== "Helm"

    To delete the Operator, do the following:
    {.power-number}

    1. List the Helm charts:

        ```{.bash data-prompt="$"}
        $ helm list -n <namespace>
        ```

        ??? example "Sample output"

            ```{.text .no-copy}
            cluster1    <namespace>         1           2023-10-31 10:18:10.763049 +0100 CET    deployed    ps-db-{{release}}        {{release}}
            my-op       <namespace>         1           2023-10-31 10:15:18.41444 +0100 CET     deployed    ps-operator-{{release}}   {{release}}
            ```

    2. Delete the [release object :octicons-link-external-16:](https://helm.sh/docs/intro/using_helm/#three-big-concepts) for Percona XtraDB Cluster 

        ```{.bash data-prompt="$"}
        $ helm uninstall cluster1 --namespace <namespace>
        ```

    3. Delete the [release object :octicons-link-external-16:](https://helm.sh/docs/intro/using_helm/#three-big-concepts) for the Operator 

        ```{.bash data-prompt="$"}
        $ helm uninstall my-op --namespace <namespace>
        ```

## Clean up resources
 
By default, TLS-related objects, user Secrets and data volumes remain in Kubernetes environment after you delete the cluster to allow you to recreate it without losing the data.

You can automate resource cleanup by turning on `percona.com/delete-mysql-pvc` and/or `percona.com/delete-ssl` [finalizers](operator.md#metadata-name)). You can also delete TLS-related objects and PVCs manually. 

To manually clean up resources, do the following:
{.power-number}

1. Delete Persistent Volume Claims.

    1. List PVCs. Replace the `<namespace>` placeholder with your namespace:

        ```{.bash data-prompt="$"}
        $ kubectl get pvc -n <namespace>
        ```    

        ??? example "Sample output"    

            ```{.text .no-copy}
            NAME                     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
            datadir-cluster1-mysql-0   Bound    pvc-8683d0ab-7ed4-48cb-93a9-bc6ceb6ec285   2G         RWO            standard       <unset>                 47m
            datadir-cluster1-mysql-1   Bound    pvc-fbc5a8a4-94ff-4259-9d15-f798c97e0788   2G         RWO            standard       <unset>                 45m
            datadir-cluster1-mysql-2   Bound    pvc-4c164ff3-a4f5-431c-9aa8-e5c7eb71a31b   2G         RWO            standard       <unset>                 44m
            ```

    2. Delete PVCs related to your cluster. The following command deletes PVCs for the `cluster1` cluster:

        ```{.bash data-prompt="$"}
        $ kubectl delete pvc datadir-cluster1-mysql-0 datadir-cluster1-mysql-1 datadir-cluster1-mysql-2 -n <namespace>
        ```    

        ??? example "Sample output"       

            ```{.text .no-copy}
            persistentvolumeclaim "datadir-cluster1-mysql-0" deleted
            persistentvolumeclaim "datadir-cluster1-mysql-1" deleted
            persistentvolumeclaim "datadir-cluster1-mysql-2" deleted
            ```    

2. Delete the Secrets

    1. List Secrets:

        ```{.bash data-prompt="$"}
        $ kubectl get secrets -n <namespace>
        ```    

    2. Delete the Secret:
        
        ```{.bash data-prompt="$"}
        $ kubectl delete secret <secret_name> -n <namespace>
        ```

