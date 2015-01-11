import time
import random

from . import exceptions


class ServerList(list):
    def __init__(self, servers, retry_time=10, timeout=None):
        list.__init__(self, servers)
        self.dead = []
        self.retry_time = retry_time
        self.timeout = timeout

    def get(self):
        if self.dead:
            retry_time, server = self.dead.pop()
            if retry_time > time.time():
                self.dead.append((retry_time, server))
            else:
                self.append(server)
        if not self:
            raise exceptions.NoServerAvailable()

        return random.choice(self)

    def mark_dead(self, server):
        self.remove(server)
        self.dead.insert(0, (time.time() + self.retry_time, server))
