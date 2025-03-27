# Exec into the containers

If you want to examine the contents of a container "in place" using remote access to it, you can use the `kubectl exec` command. It allows you to run any command or just open an interactive shell session in the container. Of course, you can have shell access to the container only if container supports it and has a “Running” state.

In the following examples we will access the container `pxc` of the `cluster1-pxc-0` Pod.

* Run `date` command:

    ``` {.bash data-prompt="$" }
    $ kubectl exec -ti cluster1-mysql-0 -c mysql -- date
    ```

    ??? example "Expected output"

        ``` {.text .no-copy}
        Thu Nov 24 10:01:17 UTC 2023
        ```

    You will see an error if the command is not present in a container. For
    example, trying to run the `time` command, which is not present in the
    container, by executing `kubectl exec -ti cluster1-mysql-0 -c mysql -- time`
    would show the following result:
    
    ``` {.text .no-copy}
    OCI runtime exec failed: exec failed: unable to start container process: exec: "time": executable file not found in $PATH: unknown command terminated with exit code 126
    ```

* Print `/var/log/mysqld.log` file to a terminal:

    ``` {.bash data-prompt="$" }
    $ kubectl exec -ti cluster1-mysql-0 -c mysql -- cat /var/log/mysqld.log
    ```

* Similarly, opening an Interactive terminal, executing a pair of commands in
    the container, and exiting it may look as follows:

    ```{.bash data-prompt="$" data-prompt-second="[mysql@cluster1-mysql-0 /]$"}
    $ kubectl exec -ti cluster1-mysql-0 -c mysql -- bash
    [mysql@cluster1-mysql-0 /]$ hostname
    cluster1-mysql-0
    [mysql@cluster1-mysql-0 /]$ ls /var/log/mysqld.log
    /var/log/mysqld.log
    [mysql@cluster1-mysql-0 /]$ exit
    exit
    $
    ```

## Avoid the restart-on-fail loop for Percona Server for MySQL containers

The restart-on-fail loop takes place when the container entry point fails
(e.g. `mysqld` crashes). In such a situation, Pod is continuously restarting.
Continuous restarts prevent to get console access to the container, and so a
special approach is needed to make fixes.

You can prevent such infinite boot loop by putting the Percona Server for MySQL
containers into the infinity loop *without* starting mysqld. This behavior
of the container entry point is triggered by the presence of the
`/var/lib/mysql/sleep-forever` file.

For example, you can do it for the `mysql` container of an appropriate Percona
Server for MySQL instance as follows:

``` {.bash data-prompt="$" }
$ kubectl exec -it cluster1-mysql-0 -c mysql -- sh -c 'touch /var/lib/mysql/sleep-forever'
```

The instance will restart automatically and run in its usual way as soon as you
remove this file (you can do it with a command similar to the one you have used
to create the file, just substitute `touch` to `rm` in it).

