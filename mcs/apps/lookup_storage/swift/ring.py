from hashlib import md5
from random import shuffle
from struct import unpack_from
from time import time
from django.conf import settings


class Ring(object):
    def __init__(self, clouds, part2cloud):
        self.clouds = clouds
        self.part2cloud = part2cloud

    def lookup(self, key):
        # data_id = str(data_id)
        # dich phai k bit la chia cho 2 mu k
        # tuong duong lay k bit dau
        # md5 mac dinh la 32 bit
        # part = unpack_from('>I',md5(data_id).digest())[0] >> settings.PARTITION_SHIFT



        if not (isinstance(key, int) or isinstance(key, long)):
            key = long(key)
        part = key
        cloud = self.part2cloud[part]
        clouds_lookup = [cloud]
        cloud_lookup_types = [cloud.type]
        clouds_lookup = [self.part2cloud[part]]
        # types = [self.clouds[cloud[0]]]
        for replica in xrange(1, settings.REPLICAS):
            # cong while: kiem tra xem khi part +1 thi node = part2cloud[part] co trung voi node cu va zone ko?
            while self.part2cloud[part] in clouds_lookup:
                part += 1
                if part >= len(self.part2cloud):
                    part = 0

            if len(cloud_lookup_types) >= 2:
                pass
            else:

                while self.part2cloud[part].type in cloud_lookup_types:
                    part += 1
                    if part >= len(self.part2cloud):
                        part = 0
            clouds_lookup.append(self.part2cloud[part])
            cloud_lookup_types.append(self.part2cloud[part].type)

        for cloud in clouds_lookup:
            print cloud.name, cloud.address, cloud.type

        return clouds_lookup


def build_ring(clouds):
    begin = time()
    parts = 2 ** settings.PARTITION_POWER
    total_weight = float(0)
    for cloud in clouds:
        total_weight += cloud.weight

    for cloud in clouds:
        cloud.desired_parts = parts / total_weight * cloud.weight

    part2cloud = []
    for part in xrange(2 ** settings.PARTITION_POWER):
        for cloud in clouds:
            if cloud.desired_parts >= 1:
                cloud.desired_parts -= 1
                part2cloud.append(cloud)
                break
        else:
            for cloud in clouds:
                if cloud.desired_parts >= 0:
                    cloud.desired_parts -= 1
                    part2cloud.append(cloud)
                    break
    shuffle(part2cloud)
    ring = Ring(clouds, part2cloud)
    print '%.02fs to build ring' % (time() - begin)
    return ring
