"""
Custom start-up script for MLflow. This is based on mlflow.cli.server,
from the MLflow Python package.
"""
import logging
import os
import sys

import sentry_sdk
from mlflow.server import _run_server
from mlflow.server.handlers import initialize_backend_stores
from mlflow.utils.process import ShellCommandException


DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5000


def configure_logger() -> logging.Logger:
    """Configure a logger that will write to stdout."""
    log_handler = logging.StreamHandler(sys.stdout)
    log_format = logging.Formatter(
        '%(asctime)s - '
        '%(levelname)s - '
        '%(module)s.%(funcName)s - '
        '%(message)s'
    )
    log_handler.setFormatter(log_format)
    log = logging.getLogger(__name__)
    log.addHandler(log_handler)
    log.setLevel(logging.INFO)
    return log

def start_mlflow_server(
    backend_store_uri: str,
    default_artifact_root: str
) -> None:
    """Start the server.

    :param backend_store_uri: URI to a database back-end.
    :param default_artifact_root: Location to use for storing artefacts.
    """
    try:
        initialize_backend_stores(backend_store_uri, default_artifact_root)
    except Exception as e:
        log.error(f'Error initializing backend store - {e}')
        sys.exit(1)

    try:
        _run_server(
            backend_store_uri,
            default_artifact_root,
            DEFAULT_HOST,
            DEFAULT_PORT,
            workers=1
        )
    except ShellCommandException as e:
        log.error(f'Running the mlflow server failed - {e}')
        sys.exit(1)


if __name__ == '__main__':
    log = configure_logger()

    try:
        sentry_dsn = os.environ.get('SENTRY_DSN')
        sentry_sdk.init(sentry_sdk, traces_sample_rate=1.0)
    except KeyError:
        log.warning('environment variable SENTRY_DSN cannot be found - '
                    'Sentry not setup to monitor service')

    try:
        backend_store_uri = os.environ['MLFLOW_BACKEND_STORE_URI']
    except KeyError:
        log.error('environment variable MLFLOW_BACKEND_STORE_URI cannot be found')
        sys.exit(1)

    try:
        default_artifact_root = os.environ['MLFLOW_DEFAULT_ARTIFACT_ROOT']
    except KeyError:
        log.error('environment variable MLFLOW_DEFAULT_ARTIFACT_ROUTE cannot be found')
        sys.exit(1)

    start_mlflow_server(
        backend_store_uri=backend_store_uri,
        default_artifact_root=default_artifact_root
    )
