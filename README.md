# Run Development KMIP Server

This repository aims to execute a dev KMIP server which can be used to configure/test KMIP clients.

To start a KMIP Server, following steps should be taken in the order as specified:

## Generate certificates for running KMIP Server


```
 python3 scripts/create_certificates.py setup --root_cn root_ca --server_cn server_cn -cl jane_doe jane_smith
```

`-cl` is a list of client certificates which should be generated, in the command above, 2 will be created. They will
be present in the directory `certificates/`.

## Start KMIP Dev Server

```
make start
```

## Stop KMIP Dev Server

```
make stop
```
