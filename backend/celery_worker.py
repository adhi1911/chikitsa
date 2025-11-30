import sys 
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.core.celery_config import make_celery

flask_app = create_app()

celery = make_celery(flask_app)

from backend.utils.tasks import *  

# celery -A celery_worker worker --loglevel=info --beat --pool=solo