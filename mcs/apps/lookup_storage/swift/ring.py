from hashlib import md5
from random import shuffle
from struct import unpack_from
from time import time
from django.conf import settings


class Ring(object):

    def __init__(self, clouds, part2node):
        self.clouds = clouds
        self.part2node = part2node


    def lookup(self, key):
        # data_id = str(data_id)
        # dich phai k bit la chia cho 2 mu k
        # tuong duong lay k bit dau
        # md5 mac dinh la 32 bit
        # part = unpack_from('>I',md5(data_id).digest())[0] >> settings.PARTITION_SHIFT

        if not (isinstance(key, int) or isinstance(key, long)):
            key = long(key)
        part = key
        clouds_lookup = [self.part2node[part]]
        # types = [self.clouds[cloud[0]]]
        for replica in xrange(1, settings.REPLICAS):
            # cong while: kiem tra xem khi part +1 thi node = part2node[part] co trung voi node cu va zone ko?
            while self.part2node[part] in clouds_lookup:
                part += 1
                if part >= len(self.part2node):
                    part = 0
            clouds_lookup.append(self.part2node[part])
            # types.append(self.nodes[cloud[-1]])
        for cloud in clouds_lookup:
            print cloud.name
        return clouds_lookup

def build_ring(clouds):
    begin = time()
    parts = 2 ** settings.PARTITION_POWER
    total_weight = float(0)
    for cloud in clouds:
        total_weight += cloud.weight

    for cloud in clouds:
        cloud.desired_parts = parts / total_weight * cloud.weight

    part2node = []
    for part in xrange(2 ** settings.PARTITION_POWER):
        for cloud in clouds:
            if cloud.desired_parts >= 1:
                cloud.desired_parts -= 1
                part2node.append(cloud)
                break
        else:
            for cloud in clouds:
                if cloud.desired_parts >= 0:
                    cloud.desired_parts -= 1
                    part2node.append(cloud)
                    break
    shuffle(part2node)
    ring = Ring(clouds, part2node)
    print '%.02fs to build ring' % (time() - begin)
    return ring
