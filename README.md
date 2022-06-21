<div align="center">
<img src="https://bodywork-media.s3.eu-west-2.amazonaws.com/bodywork-mlflow-logo.png" width="450"/>
</div>


# Deploying MLflow to Kubernetes using Bodywork

Although Bodywork is focused on deploying machine learning projects, it is flexible enough to deploy almost any type of Python project. We're going to demonstrate this by using Bodywork to deploy a production-ready instance of MLflow (a [Flask](https://flask.palletsprojects.com/en/1.1.x/) app), to Kubernetes, in only a few minutes.

MLflow is a popular open-source tool for managing various aspects of the the machine learning lifecycle, such as tracking training metrics or versioning models. It can be used alongside Bodywork's machine learning deployment capabilities, to make for a powerful open-source MLOps stack.

All of the files mentioned below can be found in the [bodywork-mlflow](https://github.com/bodywork-ml/bodywork-mlflow) repository on GitHub. You can use this repo, together with this guide to deploy MLflow to your Kubernetes cluster. Alternatively, you can use this repo as a template for deploying your own Python project.

Once we get MLflow deployed, we'll demonstrate it in action by training a model, tracking metrics and storing artefacts in the model registry. We'll also discuss patterns for integrating MLflow with Bodywork machine learning pipelines and how you can add monitoring and alerting to the deployment, by integrating with [Sentry](https://sentry.io).

## TL;DR

If you already have access to a Kubernetes cluster, then install the Bodywork Python package using Pip and head straight down to 'Deploying to Kubernetes'. If you're new to Kubernetes, then don't worry - we've got you covered - read on.

## Bodywork as a Generic Deployment Tool

Bodywork enables you to map executable Python modules to Kubernetes primitives - jobs and deployments. All you need to do is add to your project a single configuration file, `bodywork.yaml`, to describe how you want Bodywork to deploy your application - i.e., which executable Python scripts should be deployed as jobs (with a well defined start and end), and which should be deployed as service-deployments (with no scheduled end).

Based on the contents of `bodywork.yaml`, Bodywork creates a deployment plan and configures Kubernetes to execute it, using pre-built [Bodywork containers](https://hub.docker.com/repository/docker/bodyworkml/bodywork-core) for running Python modules. Bodywork containers use Git to pull your project's codebase from your remote Git repository, removing the need to build and manage bespoke container images.

Each unit of deployment is referred to as a stage and runs using it's own Bodywork container. You are free to specify as many stages as your project requires. Stages can be executed sequentially and/or in parallel - you have the flexibility to specify a deployment workflow (or [DAG](https://bodywork.readthedocs.io/en/latest/key_concepts/)).

It is precisely this combination of jobs, service-deployments, workflows and using Git repos as a means of distributing your codebase into pre-built container images, that makes Bodywork a powerful tool for quickly deploying machine learning projects. But it will also easily deploying something simpler, like MLflow.

The `bodywork.yaml` for our MLflow deployment is reproduced below. In what follows we will give a brief overview of the deployment it describes.

```yaml
version: "1.1"
pipeline:
  name: bodywork-mlflow
  docker_image: bodyworkml/bodywork-core:3.0
  DAG: server
  secrets_group: prod
stages:
  server:
    executable_module_path: mlflow_server.py
    requirements:
      - mlflow==1.16.0
      - scikit-learn
      - pyarrow
      - boto3
      - protobuf==3.6.0
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
      max_startup_time_seconds: 240
      replicas: 1
      port: 5000
      ingress: false
logging:
  log_level: INFO
```

- `pipeline.name` - the name of the pipeline, used to name Kubernetes resources created by the deployment.
- `pipeline.docker_image` - the container image to use for running your Python executables - must be hosted from a public Docker Hub repository.
- `pipeline.DAG` - the deployment workflow. For this project, we have just one 'stage' to deploy, which we have named 'server'.
- `pipeline.secrets_group` - the group in which to look for the secrets - e.g., 'dev', 'prod', etc.
- `stages.server` - a deployment stage object, that we have named 'server'. The key-value pairs that follow, describe how 'server' will be deployed by Bodywork.
- `stages.server.executable_module_path` - path to the executable Python module within the project's Git repo, that you want Bodywork to run for this stage.
- `stages.server.requirements` - a list of Python package dependencies, required by the executable Python module. These will be installed using Pip from inside the Bodywork container, when it is created.
- `stages.server.secrets` - encrypted credentials and other secrets can be mounted into Bodywork containers as environment variables. This set of key-value pairs defines the name of the encrypted value and the Kubernetes secret in which to find for it.
- `stages.server.cpu_request` - CPU resource to request from Kubernetes.
- `stages.server.memory_request_mb` - memory resource to request from Kubernetes.
- `stages.server.service` - Bodywork stages can be one of two types: batch or service. The 'server' stage is a service, so we need to supply it with service-specific configuration: the port to open on the container, the number of container replicas to create, whether to open a public HTTP ingress route to the service and how long to wait for the service to successfully start-up.

For a complete discussion of how to configure a Bodywork deployment, refer to the [User Guide](https://bodywork.readthedocs.io/en/latest/user_guide/).

## Installing Bodywork

Bodywork is distributed as a Python package, that exposes a Command Line Interface (CLI) for configuring Kubernetes to deploy Python projects, directly from remote Git repositories (e.g. GitHub). Start by creating a new Python virtual environment and installing Bodywork,

```text
$ python3.9 -m venv .venv
$ source .venv/bin/activate
$ pip install bodywork
```

### Getting Started with Kubernetes

If you have never worked with Kubernetes before, then please don't stop here. We have written a [Quickstart Guide to Kubernetes for MLOps](https://bodywork.readthedocs.io/en/latest/kubernetes/#quickstart), that will explain the basic concepts and have you up-and-running with a single-node cluster on your machine, in under 10 minutes.

Should you want to deploy to a cloud-based cluster in the future, you need only to follow the same steps while pointing to your new cluster. This is one of the key advantages of Kubernetes - you can test locally with confidence that your production deployments will behave in the same way.

## Configuring the MLflow Tracking Server

Before we deploy to our Kubernetes cluster, we'll configure and run the server locally. Start by installing MLFlow as defined in `reqirements.txt`,

```text
$ pip install -r requirements.txt
```

And then cloning the [GitHub repo](https://github.com/bodywork-ml/bodywork-mlflow) containing the MLflow deployment project,

```text
$ git clone https://github.com/bodywork-ml/bodywork-mlflow.git
$ cd bodywork-mlflow
```

We have written a custom script for starting the MLflow server - `mlflow_server.py`. This is the executable Python module that we have configured the Bodywork container to run in the 'server' deployment stage described in `bodywork.yaml`.

### Trivial Configuration

The quickest way to get started is to use Python's in-built [SQLite database](https://docs.python.org/3.8/library/sqlite3.html#module-sqlite3) as a back-end for MLflow to store things like model metrics, and to use the local file-system for storing artefacts, such as trained models. Our MLflow startup-script will look for this configuration in environment variables, so we will need to export these locally,

```text
$ export MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow.db
$ export MLFLOW_DEFAULT_ARTIFACT_ROUTE=mlflow_artefacts
```

This will cause MLflow to create a `mlflow.db` database file, together with a folder called `mlflow_artefacts`.

Now start the server,

```text
$ python mlflow_server.py
```

And open a browser at `http://localhost:5000` to access the MLflow UI.

### Preparing for Production with PostgreSQL and Cloud Object Storage

To provide concurrent connections to multiple users from multiple service replicas, MLflow will need to use a database service that can support this scenario, as a backend store. Similarly, to make model artefacts available to anyone, it will need to use a common storage service. We are AWS users here at Bodywork HQ, so we have opted to use S3 for storing artefacts and an AWS managed Postgres database instance. Managed cloud services allow you to easily scale-out when required and also offer the convenience of automated backups, upgrades, etc. (albeit, at a price).

To test this setup locally, we need to install some more Python packages,

```text
$ pip install \
    psycopg2-binary==2.8.6 \
    boto3==1.17.56
```

Where:

- `psycopg2` allows MLflow to interact Postgres.
- `boto3` allows MLflow to interact with AWS.

See the [MLflow](https://mlflow.org/docs/latest/tracking.html#mlflow-tracking-servers) documentation for how to configure MLflow to use your chosen database and artefact store. To their credit, they provide a **lot** of options.

Now, set the MLflow environment variables for our chosen production setup.

```text
$ export MLFLOW_BACKEND_STORE_URI=postgresql://USER_NAME:PASSWORD@HOST_ADDRESS:5432/mlflow
$ export MLFLOW_DEFAULT_ARTIFACT_ROUTE=s3://bodywork-mlflow-artefacts
```

We also need to make sure that our local machine is configured to use the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html), **or** that the following environment variables have been set:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION

Now re-start the server to test the connection.

```text
$ python mlflow_server.py
```

As before, open a browser at `http://localhost:5000` to access the MLflow UI.

## Deploying to Kubernetes

Start by configuring your cluster for use with Bodywork,

```text
$ bodywork configure-cluster
```

Then check the `bodywork.yaml` for errors,

```text
$ bodywork validate --check-files

--> bodywork.yaml is a valid Bodywork config file.
```

Create a Kubernetes secret that contains values for `MLFLOW_BACKEND_STORE_URI` and `MLFLOW_DEFAULT_ARTIFACT_ROOT`, to be mounted as environment variables into the containers running MLflow. If you don't have a database and/or cloud object storage available and just want to play with a toy deployment, then use the defaults shown below.

```text
bodywork create secret mlflow-config \
    --group prod \
    --data MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow.db \
    --data MLFLOW_DEFAULT_ARTIFACT_ROOT=mlflow_artefacts
```

If you want to use cloud object storage, then create a secret to contain your cloud access credentials - e.g., for AWS we would use,

```text
bodywork create secret aws-credentials \
    --group prod \
    --data AWS_ACCESS_KEY_ID=XX \
    --data AWS_SECRET_ACCESS_KEY=XX \
    --data AWS_DEFAULT_REGION=XX
```

Now deploy MLflow, using the Bodywork deployment described in the [bodywork-mlflow](https://github.com/bodywork-ml/bodywork-mlflow) GitHub repo,

```text
$ bodywork create deployment https://github.com/bodywork-ml/bodywork-mlflow.git
```

This will run the workflow-controller (locally) to orchestrate the deployment and will stream logs to stdout.

### Testing

Wait until the deployment has finished and then create a local proxy into the cluster,

```text
$ kubectl proxy
```

Now open a browser to the location of the MLflow service on your cluster,

```http
$ http://localhost:8001/api/v1/namespaces/bodywork-mlflow/services/server/proxy/
```

We will use Kubectl proxy as a secure means of authenticating with the cluster, as MLflow provides no mechanism for this out-of-the-box.

## MLflow Demo

The [mlflow_demo.ipynb](https://github.com/bodywork-ml/bodywork-mlflow/blob/master/mlflow_demo.ipynb) notebook within the [bodywork-mlflow](https://github.com/bodywork-ml/bodywork-mlflow) repo, contains an end-to-end demo of how to connect to the MLflow tracking server deployed above. It demonstrates how to,

- train a model, using MLflow to track performance metrics during hyper-paramter tuning;
- find the most optimal set of parameters;
- persist the optimal model in the model registry and push it to 'production';
- persist additional model-related artefacts (feature names and class labels, stored in text files); and finally,
- how to retrieve the latest 'production' model version, from the model registry.

If you want to run this notebook locally, the you'll need to install the following Python packages,

```text
$ pip install \
    jupyterlab==2.2.9 \
    sklearn==0.0 \
    pandas==1.1.5 \
    tqdm==4.54.1 \
    numpy==1.19.4
```

And then fire-up Jupyter Lab,

```text
$ jupyter lab
```

### Patterns for Integrating MLflow with Bodywork Pipelines

Kubernetes greatly simplifies networking between services in the cluster. From **within** the cluster, you will be able to access the tracking server using the following URL,

```text
http://server.bodywork-mlflow.svc.cluster.local:5000
```

Any Bodywork stage can make use of the tracking server at this location, by setting the tracking URI (as we did in the demo notebook),

```python
import mlflow

mlflow.set_tracking_uri('http://server.bodywork-mlflow.svc.cluster.local:5000')
```

This enables us to revisit the [Bodywork Quickstart Tutorial](https://bodywork.readthedocs.io/en/latest/quickstart_serve_model/) for serving a model. This project also provides predictions for the iris classification task, as used in the MLflow demo notebook. In this example deployment, we used the joblib package to load a model that was persisted as an artefact in the project's repo (not a best-practice, albeit pragmatic). We can now modify [service.py](https://github.com/bodywork-ml/bodywork-serve-model-project/blob/master/scoring_service/service.py) to collect the latest 'production' model from MLflow. If we assume that this is the same 'production' version as the one trained in the MLflow demo notebook, then all we need to do is swap these units of code,

```python
import numpy as np
from flask import Flask, jsonify, make_response, request, Response
from joblib import load
from sklearn.base import BaseEstimator

MODEL_PATH = 'classification_model.joblib'

# web API definition code
# ...

if __name__ == '__main__':
    model = load(MODEL_PATH)
    print(f'loaded model={model}')
    print(f'starting API server')
    app.run(host='0.0.0.0', port=5000)
```

For these ones,

```python
import mlflow
import numpy as np
from flask import Flask, jsonify, make_response, request, Response
from sklearn.base import BaseEstimator

MODEL_NAME = 'iris_classification'

# web API definition code
# ...

if __name__ == '__main__':
    mlflow.set_tracking_uri('http://server.bodywork-mlflow.svc.cluster.local:5000')
    model = mlflow.sklearn.load_model(model_uri=f'models:/{MODEL_NAME}/Production')
    print(f'loaded model={model}')
    print(f'starting API server')
    app.run(host='0.0.0.0', port=5000)
```

We can also take this one step further and create a Bodywork cronjob, that will re-deploy (and hence re-run the server start-up code), on a schedule. For example, issuing the following command,

```text
$ bodywork create cronjob https://github.com/bodywork-ml/bodywork-serve-model-project \
    --name=scoring-service-deployment-pipeline \
    --schedule="0 * * * *" \
    --retries=2
```

Will cause Bodywork to trigger a rolling re-deployment of the prediction web API, every hour. Each time, it will load the most recent version of the model that has been pushed to 'production' - either manually, or as part of an [automated re-training pipeline](https://bodywork.readthedocs.io/en/latest/quickstart_ml_pipeline/). Thereby demonstrating how Bodywork can be used to implement continuous delivery for machine learning.

## Optional Extras - Application Monitoring with Sentry

Here at Bodywork HQ, we are becoming fans of using [Sentry](https://sentry.io) for monitoring Python services and generating alerts. Sentry is free for individual users, but charges for business use (i.e. Teams). We have setup `mlflow_server.py` to configure Sentry, if it has been installed and configured for your deployment.

To ensure that Sentry gets installed in the Bodywork containers running the MLflow service replicas, modify `bodywork.yaml` to include the Sentry Python client in the list of requirements.

```yaml
...
stages:
  server:    
    ...
    requirements:
      - ...
      - sentry-sdk==0.20.3
```

Then, modify `bodywork.yaml` again to retrieve the Sentry client key from a Kubernetes secret called `sentry-integration`,

```yaml
...
stages:
  server:    
    ...
    secrets:
      ...
      SENTRY_DSN: sentry-integration
```

Create the Kubernetes secret containing your secret client key.

```text
bodywork create secret sentry-integration \
    --group prod \
    --data SENTRY_DSN=YOUR_SENTRY_CLIENT_KEY
```

Finally, re-deploy the server,

```text
$ bodywork update deployment https://github.com/bodywork-ml/bodywork-mlflow.git
```

Which we trigger remotely this time, as there is no need observe the logs as they are generated.

Congratulations - you now have a production-worthy deployment of MLflow!
