# Deploying MLflow to Kubernetes using Bodywork

```shell
export MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow.db
export MLFLOW_DEFAULT_ARTIFACT_ROUTE=mlflow_artefacts
python mlflow_server.py
```

```shell
export MLFLOW_BACKEND_STORE_URI=postgresql://XXX:XXX@XXX.XXX.XXX.rds.amazonaws.com:5432/mlflow
export MLFLOW_DEFAULT_ARTIFACT_ROUTE=s3://bodywork-mlflow-artefacts
python mlflow_server.py
```

```shell
bodywork setup-namespace mlflow
```

```shell
 bodywork secret create \
    --namespace=mlflow \
    --name=aws-credentials \
    --data AWS_ACCESS_KEY_ID=XXX AWS_SECRET_ACCESS_KEY=XXX AWS_DEFAULT_REGION=XXX
```

```shell
 --namespace=mlflow \
    --name=mlflow-config \
    --data MLFLOW_BACKEND_STORE_URI=postgresql://XXX:XXX@XXX.XXX.XXX.rds.amazonaws.com:5432/mlflow MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://bodywork-mlflow-artefacts
```

```http
http://CLUSTER_IP/mlflow/bodywork-mlflow--server/
```
