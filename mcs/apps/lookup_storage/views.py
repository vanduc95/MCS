import hashlib
import os.path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpResponse

from lookup_storage import forms
from lookup_storage import utils
from lookup_storage.swift.ring import Ring
from lookup_storage.swift.ring import build_ring

from mcs.wsgi import RINGS


@login_required(login_url='/auth/login/')
def init_ring(request):
    """Init Ring per user"""
    # Setup pickle file path

    username = request.user.username
    pickle_name = hashlib.md5(username).hexdigest()
    pickle_path = settings.MEDIA_ROOT + '/configs/' + username + '-' + pickle_name + '.pickle'

    if os.path.exists(pickle_path):
        try:
            ring = utils.load(pickle_path)
            RINGS[username] = ring

        except Exception as e:
            messages.error(request, 'Error when load ring: %s' % str(e))
        messages.info(request, 'Ring is loaded')
        return redirect('home')

    else:
        if request.method == 'POST':
            form = forms.UploadCloudConfigsForm(request.POST, request.FILES)
            if form.is_valid():
                # Init Cloud objects.
                clouds = utils.load_cloud_configs(request, username,
                                                  request.FILES['cloud_configs'])
                if clouds:
                    total_quota = 0
                    # for cloud in clouds:
                    #     utils.set_quota_cloud(cloud)
                    #     utils.set_usage_cloud(cloud)
                    #     total_quota += cloud.quota

                    for i in range(len(clouds)):
                        clouds[i].quota = settings.CLOUDS_QUOTA[i]
                        utils.set_usage_cloud(clouds[i])
                        total_quota += clouds[i].quota

                    for cloud in clouds:
                        cloud.set_weight(total_quota)
                        print cloud.quota

                    ring = build_ring(clouds)
                    RINGS[username] = ring
                    # Temporary
                    utils.save(ring, pickle_path)
                    messages.info(request, 'Ring is saved')
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid config format!')
        else:
            form = forms.UploadCloudConfigsForm()
        return render(request, 'lookup_storage/config.html',
                      {
                          'form': form,
                          'username': request.user.username,
                      })
