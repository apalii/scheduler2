#from app_tasks.models import Ips
from random import random


class SetRemoteAddr(object):
    def process_request(self, request):
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            pass
        else:
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
            # Take just the first one.
            real_ip = real_ip.split(",")[0]
            request.META['REMOTE_ADDR'] = real_ip
            request.META['REMOTE_USER'] = "TEST_USER" + str(random())[6:] 
            """if request.META['PATH_INFO'] == '/':
                ins, created = Ips.objects.get_or_create(ip=real_ip)
                if not created:
                    ins.counter += 1
                    ins.save()"""