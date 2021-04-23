# Deploying MLflow to Kubernetes using Bodywork

## Before you get Started

TODO

```shell
$ pip install \
    bodywork==2.0.2 \
    mlflow==1.14.1 \
    psycopg2-binary==2.8.6 \
    boto3==1.17.56
```

## Proof of Concept

```shell
$ export MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow.db
$ export MLFLOW_DEFAULT_ARTIFACT_ROUTE=mlflow_artefacts
$ python mlflow_server.py
```

## Preparing for Production with PostgreSQL and Cloud Object Storage

```shell
$ export MLFLOW_BACKEND_STORE_URI=postgresql://XXX:XXX@XXX.XXX.XXX.rds.amazonaws.com:5432/mlflow
$ export MLFLOW_DEFAULT_ARTIFACT_ROUTE=s3://bodywork-mlflow-artefacts
$ python mlflow_server.py
```

## Deploying to Kubernetes

```shell
$ bodywork setup-namespace mlflow
```

```shell
 $ bodywork secret create \
    --namespace=mlflow \
    --name=aws-credentials \
    --data AWS_ACCESS_KEY_ID=XXX AWS_SECRET_ACCESS_KEY=XXX AWS_DEFAULT_REGION=XXX
```

```shell
$ bodywork secret create \
    --namespace=mlflow \
    --name=mlflow-config \
    --data MLFLOW_BACKEND_STORE_URI=postgresql://XXX:XXX@XXX.XXX.XXX.rds.amazonaws.com:5432/mlflow MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://bodywork-mlflow-artefacts
```

```shell
$ bodywork workflow --ns mlflow https://github.com/bodywork-ml/bodywork-mlflow.git master
```

## Testing

```shell
$ kubectl proxy
```

```http
$ http://localhost:8001/api/v1/namespaces/mlflow/services/bodywork-mlflow--server/proxy/
```

## MLflow Demo

TODO - use `mlflow_demo.ipynb`

```shell
$ pip install \
    jupyterlab==2.2.9 \
    sklearn==0.0 \
    pandas==1.1.5 \
    tqdm==4.54.1 \
    numpy==1.19.4
```
