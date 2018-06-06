from __future__ import absolute_import, unicode_literals

import gc
import os
from calplus.client import Client
from django.contrib import messages
from django.conf import settings

from dashboard import exceptions
from dashboard.models import File

from mcs.celery_tasks import app
from mcs.wsgi import RINGS

COUNT = 0


@app.task
def upload_object(cloud, file):
    """Upload object to cloud node with absolute_name
    :param cloud: object of model Cloud.
    :param file: object of model File.
    """
    connector = Client(version='1.0.0', resource='object_storage',
                       provider=cloud.provider)
    # Create container named = username if it doesnt exist
    container = file.owner.username
    try:
        with open(settings.MEDIA_ROOT + '/' + file.name) as content:
            global COUNT
            COUNT += 1
            connector.upload_object(container, file.path.strip('/'),
                                    contents=content.read(),
                                    content_length=file.size,
                                    metadata={'status': 'UPDATED'})
            # Remove saved file
            try:
                if COUNT == 3:
                    os.remove(settings.MEDIA_ROOT + '/' + file.name)
                    COUNT = 0
            except OSError:
                pass
    except exceptions.UploadObjectError:
        return None
    finally:
        # Delete connector when everything was done.
        del connector
        gc.collect()


def upload_file(request, file, content):
    """Upload file
    :param file: object of model File.
    :param content: content of file (stream
.    """
    # ring = RINGS[file.owner.username]
    # node = ring.lookup(long(file.identifier))
    # update_status_file(request, file.path, File.NOT_AVAILABLE)
    # for cloud in node.clouds:
    #     # Put task to queue 'default'
    #     # _content = copy.deepcopy(content)
    #     upload_object.delay(cloud, file)

    ring = RINGS[file.owner.username]
    clouds = ring.lookup(long(file.identifier))
    update_status_file(request, file.path, File.NOT_AVAILABLE)
    for cloud in clouds:
        # Put task to queue 'default'
        # _content = copy.deepcopy(content)
        upload_object.delay(cloud, file)


def download_file(file):
    """Download object from Cloud
    :param file: object of model File.
    """
    ring = RINGS[file.owner.username]
    clouds = ring.lookup(long(file.identifier))
    container = file.owner.username
    for cloud in clouds:
        # Init cloud's connector
        connector = Client(version='1.0.0', resource='object_storage',
                           provider=cloud.provider)
        try:
            object_stat = connector.stat_object(container,
                                                file.path.strip('/'))
        except Exception:
            continue

        # Temporary handle.
        stream_key = 1

        # drop cause not cloud s3 amazon <if have s3, need uncomment>
        # if cloud.type == 'amazon':
        #     object_stat = object_stat['Metadata']
        #     stream_key = 'Body'


        object_status = [object_stat[key]
                         for key in object_stat.keys() if 'status' in key]

        if object_status[0] == 'UPDATED':
            file_content = connector.download_object(container, file.path.strip('/'))[stream_key]
            del connector
            gc.collect()
            # if cloud.type == 'amazon':
            #     return file_content.read()
            return file_content
    return None


def set_status_file(request, file):
    """Check object's status then set file's status
    depend on it"""
    # ring = RINGS[file.owner.username]
    # node = ring.lookup(long(file.identifier))
    # container = file.owner.username
    # done = 0
    # for cloud in node.clouds:
    #     if get_status_object(cloud, container, file.path.strip('/')):
    #         done += 1
    # if 0 < done < len(node.clouds):
    #     update_status_file(request, file.path, File.AVAILABLE)
    # elif done == len(node.clouds):
    #     update_status_file(request, file.path, File.UPDATE)


    ring = RINGS[file.owner.username]
    clouds = ring.lookup(long(file.identifier))
    container = file.owner.username
    done = 0
    for cloud in clouds:
        if get_status_object(cloud, container, file.path.strip('/')):
            done += 1
    if 0 < done < len(clouds):
        update_status_file(request, file.path, File.AVAILABLE)
    elif done == len(clouds):
        update_status_file(request, file.path, File.UPDATE)


def update_status_file(request, file_path, new_status):
    """Update status of file
    :param file_path: path of file.
    :param new_status: new status of file.
    """
    try:
        username = request.user.username
        file = File.objects.filter(
            owner__username=username).get(path=file_path)
        file.status = new_status
        file.save()
    except File.DoesNotExist as e:
        messages.error(request, 'Update status of file failed: %s' % str(e))


def get_status_file(request, file_path):
    """Get File object's status"""
    try:
        username = request.user.username
        file = File.objects.filter(
            owner__username=username).get(path=file_path)
        return file.status
    except File.DoesNotExist as e:
        messages.error(request, 'Get status of file failed: %s' % str(e))


def get_status_object(cloud, container, object):
    connector = Client(version='1.0.0', resource='object_storage',
                       provider=cloud.provider)
    try:
        return connector.stat_object(container, object)
    except Exception:
        return None
    finally:
        # Delete connector when everything was done.
        del connector
        gc.collect()


def update_status_object(request, cloud, container, object, new_status):
    """Upload exist object's status
    :param cloud: object of class Cloud.
    :param container: container name.
    :param object: object name.
    :param new_status: new status of file.
    """
    connector = Client(version='1.0.0', resource='object_storage',
                       provider=cloud.provider)
    try:
        connector.update_object(container, object,
                                metadata={'status': new_status})
        messages.info(request, 'Update status file %(file)s from cloud %(cloud)s successfully!' % ({
            'cloud': cloud.name,
            'file': file.name
        }))
    except exceptions.UpdateObjectError as e:
        messages.error(request, 'Update status file %(file)s from cloud %(cloud)s failed: %(error)s!' % ({
            'cloud': cloud.name,
            'file': file.name,
            'error': str(e),
        }))
    finally:
        # Delete connector when everything was done.
        del connector
        gc.collect()


def delete_file(request, file):
    """Delete file
    :param file: object of model File.
    """
    ring = RINGS[file.owner.username]
    clouds = ring.lookup(long(file.identifier))
    container = file.owner.username
    for cloud in clouds:
        connector = Client(version='1.0.0', resource='object_storage',
                           provider=cloud.provider)
        try:
            connector.delete_object(container, file.path.strip('/'))
            # messages.info(request, 'Delete file %(file)s from cloud %(cloud)s successfully!' % ({
            #     'cloud': cloud.name,
            #     'file': file.name
            # }))
        except Exception as e:
            messages.error(request, 'Delete file %(file)s from cloud %(cloud)s failed: %(error)s!' % ({
                'cloud': cloud.name,
                'file': file.name,
                'error': str(e),
            }))
        finally:
            # Delete connector when everything was done.
            del connector
            gc.collect()
