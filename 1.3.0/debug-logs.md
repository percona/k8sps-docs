> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Check the Logs

Logs provide valuable information. It makes sense to check the logs of the database Pods and the Operator Pod. Following flags are helpful for checking the logs with the `kubectl logs` command:

| Flag                           | Description                                                                                                                                                                                                                                         |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--container=<container-name>` | Print log of a specific container in case of multiple containers in a Pod                                                                                                                                                                           |
| `--follow`                     | Follows the logs for a live output                                                                                                                                                                                                                  |
| `--since=<time>`               | Print logs newer than the specified time, for example: `--since="10s"`                                                                                                                                                                              |
| `--timestamps`                 | Print timestamp in the logs (timezone is taken from the container)                                                                                                                                                                                  |
| `--previous`                   | Print previous instantiation of a container. This is extremely useful in case of container restart, where there is a need to check the logs on why the container restarted. Logs of previous instantiation might not be available in all the cases. |

When [persistent logging](https://docs.percona.com/percona-operator-for-mysql/1.3.0/persistent-logging.html) is enabled, the MySQL error log is written to a file on the data volume and streamed to the `logs` container. It does not appear in the `mysql` container output. Read it with:

```
kubectl logs ps-cluster1-mysql-0 -c logs
```

In the following examples we will access containers of the `ps-cluster1-mysql-0` Pod.

- Check logs of the `mysql` container:

  ```
  kubectl logs ps-cluster1-mysql-0 -c mysql
  ```

- Check logs of the `xtrabackup` container:

  ```
  kubectl logs ps-cluster1-mysql-0 -c xtrabackup
  ```

  See more about troubleshooting backups in the [Troubleshoot backups and restores](https://docs.percona.com/percona-operator-for-mysql/1.3.0/debug-backup-restore.html) chapter.

- Filter logs of the `mysql` container which are not older than 600 seconds:

  ```
  kubectl logs ps-cluster1-mysql-0 -c mysql --since=600s
  ```

- Check logs of a previous instantiation of the `mysql` container, if any:

  ```
  kubectl logs ps-cluster1-mysql-0 -c mysql --previous
  ```

- Check logs of the `mysql` container for `ERROR` messages:

  ```
  kubectl logs ps-cluster1-mysql-0 -c mysql | grep 'ERROR'
  ```

- Check logs of the Operator:

  ```
  kubectl logs -l "app.kubernetes.io/name=percona-server-mysql-operator" --tail=-1
  ```

- Check logs of the operator, parsing the output with [jq JSON processor](https://stedolan.github.io/jq/) (requires `LOG_STRUCTURED` to be `true`):

  ```
  kubectl logs -l "app.kubernetes.io/name=percona-server-mysql-operator" --tail=-1 -f | jq -R 'fromjson?'
  ```

- Check logs of the HAProxy pod for configuration issues:

  ```
  kubectl logs ps-cluster1-haproxy-0 | grep 'The custom config /etc/haproxy-custom/haproxy.cfg is not valid and will be ignored.'
  ```
