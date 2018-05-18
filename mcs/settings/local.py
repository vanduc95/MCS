from base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mcs',
        'HOST': '127.0.0.1',
        'USER': 'root',
        'PASSWORD': 'admin',
        'PORT': 3306
    }
}

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'
CELERY_ACCEPT_CONTENT = ['application/x-python-serialize']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

PARTITION_POWER = 16
PARTITION_SHIFT = 32 - PARTITION_POWER
REPLICAS = 2
CLOUDS_QUOTA = [10737418240, 21474836480, 32212254720, 42949672960]