"""
TODO
"""
import logging
import os
import sys

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
    """TODO

    :param backend_store_uri: TODO
    :param default_artifact_root: TODO
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
        log.error(f'Running the mlflow server failed. Please see the logs above for details - {e}')
        sys.exit(1)


if __name__ == '__main__':
    log = configure_logger()

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
