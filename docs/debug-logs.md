# Check the Logs

Logs provide valuable information. It makes sense to check the logs of the
database Pods and the Operator Pod. Following flags are helpful for checking the
logs with the `kubectl logs` command:

| Flag                          | Description                                                               |
| ----------------------------- | ------------------------------------------------------------------------- |
| `--container=<container-name>`| Print log of a specific container in case of multiple containers in a Pod |
| `--follow`                    | Follows the logs for a live output                                        |
| `--since=<time>`              | Print logs newer than the specified time, for example: `--since="10s"`    |
| `--timestamps`                | Print timestamp in the logs (timezone is taken from the container)        |
| `--previous`                  | Print previous instantiation of a container. This is extremely useful in case of container restart, where there is a need to check the logs on why the container restarted. Logs of previous instantiation might not be available in all the cases. |

In the following examples we will access containers of the `cluster1-mysql-0` Pod.

* Check logs of the `mysql` container:

    ``` {.bash data-prompt="$" }
    $ kubectl logs cluster1-mysql-0 -c mysql
    ```

* Check logs of the `xtrabackup` container:

    ``` {.bash data-prompt="$" }
    $ kubectl logs cluster1-mysql-0 -c xtrabackup
    ```

* Filter logs of the `mysql` container which are not older than 600 seconds:

    ``` {.bash data-prompt="$" }
    $ kubectl logs cluster1-mysql-0 -c mysql --since=600s
    ```

* Check logs of a previous instantiation of the `mysql` container, if any:

    ``` {.bash data-prompt="$" }
    $ kubectl logs cluster1-mysql-0 -c mysql --previous
    ```

* Check logs of the `mysql` container, parsing the output with [jq JSON processor](https://stedolan.github.io/jq/):

    ``` {.bash data-prompt="$" }
    $ kubectl logs cluster1-mysql-0 -c mysql -f | jq -R 'fromjson?'
    ```

