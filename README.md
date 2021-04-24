# Deploying MLflow to Kubernetes using Bodywork

Although Bodywork is focused on the deployment needs of machine learning projects, it is flexible enough to be capable of deploying nearly any type of Python application. We are going to demonstrate this by using Bodywork to deploy MLflow to Kubernetes, ready for production, in only a few minutes.

MLflow is a popular open-source tool for managing various aspects of the the machine learning lifecycle, such as tracking model metrics or versioning models. It can be used alongside Bodywork's machine learning deployment capabilities, to make for a powerful MLOps stack.

All of the files mentioned below can be found in the [bodywork-mlflow](https://github.com/bodywork-ml/bodywork-mlflow) repository on GitHub. You can use this repo, together with this guide to deploy MLflow to your Kubernetes cluster. Alternatively, you can use this repo as a template for deploying your own Python application.

Once we get MLflow deployed, we'll demonstrate it in action by training a model, tracking metrics and storing artefacts in the registry. We will also discuss how to build Bodywork machine learning pipeline that can interact with MLflow.

## Before we get Started

Bodywork is distributed as a Python package, that exposes a Command Line Interface (CLI) for configuring Kubernetes to deploy Python projects, directly from remote Git repositories (e.g. GitHub). Start by creating a new Python virtual environment and installing Bodywork,

```shell
$ python3.8 -m venv .venv
$ source .venv/bin/activate
$ pip install bodywork==2.0.2
```

### Getting Started with Kubernetes

If you have never worked with Kubernetes before, then please don't stop here. We have written a guide to [Getting Started with Kubernetes for MLOps](https://bodywork.readthedocs.io/en/latest/kubernetes/#getting-started-with-kubernetes), that will have you up-and-running with a single-node cluster on your laptop, in under 10 minutes. Should you want to deploy to a cloud-based cluster in the future, you need only to follow the same steps while pointing to your new cluster. This is one of the key advantages of Kubernetes - you can test locally with confidence that your production deployments will behave in the same way.

## Bodywork as a Generic Deployment Tool

Bodywork enables you to map executable Python modules to Kubernetes primitives: jobs and deployments. All you need to do is add to your project a single configuration file, `bodywork.yaml`, to describe how you want Bodywork to deploy your application - i.e., which executable Python scripts should be run as jobs (with a well defined start and end), and which should be run as service deployments (with no scheduled end).

Based on the contents of `bodywork.yaml`, Bodywork creates a deployment plan and configures Kubernetes to execute it, using pre-built [Bodywork containers](https://hub.docker.com/repository/docker/bodyworkml/bodywork-core) for executing Python modules. Bodywork containers use Git to pull your project's codebase from your remote Git repository, thereby removing the need to build container images and push them to a remote image registry.

Each unit of deployment is referred to as a stage and runs within it's own Bodywork container. You are free to specify as many stages as your project requires. Stages can be executed in sequentially and/or in parallel - you have the flexibility to specify a deployment [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph) (or workflow). It is precisely this combination of jobs, service deployments and workflows, using Git to distribute your codebase into pre-built container images, that makes Bodywork a powerful tool for deploying machine learning projects. But it will also light work of deploying something simpler, like MLflow.

The `bodywork.yaml` for our MLflow deployment is reproduced below. We will give a brief overview of what it contains - for a complete discussion of how to configure a Bodywork deployment, refer to the [User Guide](https://bodywork.readthedocs.io/en/latest/user_guide/).

```yaml
version: "1.0"
project:
  name: bodywork-mlflow
  docker_image: bodyworkml/bodywork-core:latest
  DAG: server
stages:
  server:
    executable_module_path: mlflow_server.py
    requirements:
      - mlflow[extras]==1.14.1
      - psycopg2-binary==2.8.6
    secrets:
      MLFLOW_BACKEND_STORE_URI: mlflow-config
      MLFLOW_DEFAULT_ARTIFACT_ROOT: mlflow-config
      AWS_ACCESS_KEY_ID: aws-credentials
      AWS_SECRET_ACCESS_KEY: aws-credentials
      AWS_DEFAULT_REGION: aws-credentials
    cpu_request: 1
    memory_request_mb: 250
    service:
      max_startup_time_seconds: 30
      replicas: 1
      port: 5000
      ingress: false
logging:
  log_level: INFO
```

We can see from `bodywork.yaml` above, that...

## Testing Locally

TODO

```shell
$ pip install mlflow==1.14.1
```

```shell
$ git clone https://github.com/bodywork-ml/bodywork-mlflow.git
```

### TODO

TODO

```shell
$ export MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow.db
$ export MLFLOW_DEFAULT_ARTIFACT_ROUTE=mlflow_artefacts
$ python mlflow_server.py
```

### Preparing for Production with PostgreSQL and Cloud Object Storage

TODO

```shell
$ pip install \
    psycopg2-binary==2.8.6 \
    boto3==1.17.56
```

```shell
$ export MLFLOW_BACKEND_STORE_URI=postgresql://USER_NAME:PASSWORD@HOST_ADDRESS:5432/mlflow
$ export MLFLOW_DEFAULT_ARTIFACT_ROUTE=s3://bodywork-mlflow-artefacts
$ python mlflow_server.py
```

## Deploying to Kubernetes

TODO

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
    --data MLFLOW_BACKEND_STORE_URI=postgresql://USER_NAME:PASSWORD@HOST_ADDRESS:5432/mlflow MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://bodywork-mlflow-artefacts
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

### Accessing MLflow from within a Bodywork Stage

TODO

## Where to go from Here

- Sentry for monitoring.
- Deploy your own app.
- Logs
