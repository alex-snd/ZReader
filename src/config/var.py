import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv

# -------------------------------------------------General Variables----------------------------------------------------

ALPHABET = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'v',
            'u', 'w', 'x', 'y', 'z'}

ALPHABET2NUM = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10,
                'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'v': 20,
                'u': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25}

NUM2ALPHABET = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i', 9: 'j', 10: 'k',
                11: 'l', 12: 'm', 13: 'n', 14: 'o', 15: 'p', 16: 'q', 17: 'r', 18: 's', 19: 't', 20: 'v',
                21: 'u', 22: 'w', 23: 'x', 24: 'y', 25: 'z'}

COLORS = ('green', 'yellow', 'blue', 'magenta', 'cyan', 'bright_green', 'bright_yellow', 'bright_blue',
          'bright_magenta', 'bright_cyan', 'red')

BASE_DIR = Path(__file__).parent.parent.parent.absolute()

CONFIG_DIR = BASE_DIR / 'src' / 'config'
INFERENCE_DIR = BASE_DIR / 'inference'
LOGS_DIR = BASE_DIR / 'logs'
EXPERIMENTS_DIR = BASE_DIR / 'experiments'
MLFLOW_REGISTRY_DIR = EXPERIMENTS_DIR / 'mlflow_registry'
WANDB_REGISTRY_DIR = EXPERIMENTS_DIR / 'wandb_registry'

LOGS_DIR.mkdir(parents=True, exist_ok=True)
EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
MLFLOW_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
WANDB_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / '.env')

# --------------------------------------------------Wandb Variables----------------------------------------------------


# --------------------------------------------------Mlflow Variables----------------------------------------------------

MLFLOW_HOST = os.getenv('MLFLOW_HOST', default='localhost')
MLFLOW_PORT = int(os.getenv('MLFLOW_PORT', default=8002))
MLFLOW_BACKEND = os.getenv('MLFLOW_BACKEND',
                           default=f'sqlite:{(MLFLOW_REGISTRY_DIR.absolute() / "mlflow.db").as_uri()[5:]}')
MLFLOW_WORKERS = int(os.getenv('MLFLOW_WORKERS', default=1))
MLFLOW_PID = CONFIG_DIR / 'mlflow.pid'

# -------------------------------------------------Dashboard Variables--------------------------------------------------

STREAMLIT_HOST = os.getenv('STREAMLIT_HOST', default='localhost')
STREAMLIT_PORT = int(os.getenv('STREAMLIT_PORT', default=8000))
DASHBOARD_PID = CONFIG_DIR / 'dashboard.pid'

# ---------------------------------------------------API Variables------------------------------------------------------

FASTAPI_HOST = os.getenv('FASTAPI_HOST', default='localhost')
FASTAPI_PORT = int(os.getenv('FASTAPI_PORT', default=8001))
FASTAPI_WORKERS = int(os.getenv('FASTAPI_WORKERS', default=1))
FASTAPI_URL = f'http://{FASTAPI_HOST}:{FASTAPI_PORT}'
API_PID = CONFIG_DIR / 'api.pid'

# --------------------------------------------------Broker Variables----------------------------------------------------

BROKER_PORT = int(os.getenv('BROKER_PORT', default=5672))
BROKER_UI_PORT = int(os.getenv('BROKER_UI_PORT', default=15672))
BROKER_IMAGE = os.getenv('BROKER_IMAGE', default='rabbitmq:3.9.8-management')
BROKER_VOLUME_ID = 'zreader_broker_data'
BROKER_ID = 'zreader_broker'

# -------------------------------------------------Backend Variables----------------------------------------------------

BACKEND_PORT = int(os.getenv('BACKEND_PORT', default=6379))
BACKEND_IMAGE = os.getenv('BACKEND_IMAGE', default='redis:6.2')
BACKEND_VOLUME_ID = 'zreader_backend_data'
BACKEND_ID = 'zreader_backend'

# --------------------------------------------------Worker Variables----------------------------------------------------

CELERY_BROKER = os.getenv('CELERY_BROKER', default='pyamqp://guest@localhost')
CELERY_BACKEND = os.getenv('CELERY_BACKEND', default='redis://localhost')
CELERY_WORKERS = int(os.getenv('CELERY_WORKERS', default=1))
WORKER_PID = CONFIG_DIR / 'worker.pid'

# -------------------------------------------------Inference Variables--------------------------------------------------

INFERENCE_PARAMS_PATH = Path(os.getenv('INFERENCE_PARAMS_PATH', default=INFERENCE_DIR / 'params.json'))
INFERENCE_WEIGHTS_PATH = Path(os.getenv('INFERENCE_WEIGHTS_PATH', default=INFERENCE_DIR / 'z_reader.pt'))
CUDA = os.getenv('CUDA', default='').lower() != 'false'
MAX_NOISE = int(os.getenv('MAX_NOISE', default=13))


# -------------------------------------------------Services Variables---------------------------------------------------

class PoolType(str, Enum):
    prefork = 'prefork'
    eventlet = 'eventlet'
    gevent = 'gevent'
    processes = 'processes'
    solo = 'solo'


class LogLevel(str, Enum):
    debug = 'debug'
    info = 'info'
    warning = 'warning'
    error = 'error'
    critical = 'critical'


DEFAULT_CONFIG = {
    'dashboard': {'host': STREAMLIT_HOST, 'port': STREAMLIT_PORT, 'loglevel': 'info'},
    'api': {'host': FASTAPI_HOST, 'port': FASTAPI_PORT, 'loglevel': 'info', 'concurrency': FASTAPI_WORKERS},
    'worker': {'name': 'ZReaderWorker', 'pool': 'solo', 'loglevel': 'info', 'concurrency': CELERY_WORKERS,
               'broker_url': CELERY_BROKER, 'backend_url': CELERY_BACKEND},
    'broker': {'port': BROKER_PORT, 'ui_port': BROKER_UI_PORT, 'auto_remove': False},
    'backend': {'port': BACKEND_PORT, 'auto_remove': False}
}
