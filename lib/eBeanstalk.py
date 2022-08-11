import errno
import threading
import beanstalkc

from lib.logger import Logger

__author__ = 'P.A'
_TIMEOUT = 30
_LANG = ["id", "my", "en"]
logger = Logger('eBeanstalk')

class Pusher(threading.Thread):
    beans = None
    connected = False
    running = True
    tube = None

    def __init__(self, tube, host="localhost"):
        threading.Thread.__init__(self)
        self.beans = beanstalkc.Connection(host)
        self.connect()
        self.beans.use(tube)
        self.tube = tube

    def connect(self):
        if self.connected is not True:
            self.beans.connect()
            self.connected = True

    def getBuriedJob(self):
        job = self.beans.peek_buried()
        return job

    def kick(self, n=None):
        if n:
            return self.beans.kick(n)
        return self.beans.kick()

    def getStat(self):
        return self.beans.stats_tube(self.tube)

    def releaseJob(self, job, priority=None, delay=0):
        if priority:
            job.release(priority, delay)
        else:
            job.release(delay=delay)

    def buriedJob(self, job):
        job.bury()

    def setJob(self, job_message, priority=None, delay=0, ttr=360000):
        if priority:
            self.beans.put(str(job_message), priority, delay, ttr)
        else:
            self.beans.put(str(job_message), delay=delay, ttr=ttr)

    def deleteJob(self, job):
        job.delete()

    def close(self):
        self.beans.close()


class Worker(threading.Thread):
    beanstalk = None
    worker_id = None
    running = True

    def __init__(self, tube, worker_id, host="localhost"):
        threading.Thread.__init__(self)
        self.beanstalk = beanstalkc.Connection(host=host)
        self.beanstalk.connect()
        self.tube = tube
        self.beanstalk.watch(tube)
        self.worker_id = worker_id
        self.watchTube(tube)

    def isWaiting(self):
        stat = self.beanstalk.stats_tube(self.tube)
        if stat['current-waiting'] > 0:
            return True
        return False

    def getTubes(self):
        tubes = self.beanstalk.tubes()
        return tubes

    def watchTube(self, tube):
        self.beanstalk.watch(tube)
        # self.ignoreTubes(tube)

    def ignoreTubes(self, tube):
        tubes = self.getTubes()
        for t in tubes:
            if t != tube:
                self.beanstalk.ignore(t)

    def getJob(self, timeout=30):
        try:
            job = self.beanstalk.reserve(timeout)
        except IOError as e:
            if e.errno == errno.EPIPE:
                self.beanstalk.connect()
                job = self.beanstalk.reserve(timeout)
            else:
                raise IOError(e)
        return job

    def releaseJob(self, job, priority=None, delay=0):
        if priority:
            job.release(priority, delay)
        else:
            job.release(delay=delay)

    def deleteJob(self, job):
        job.delete()

    def buriedJob(self, job):
        job.bury()

    def getStat(self):
        return self.beanstalk.stats_tube(self.tube)

    def stop(self):
        self.running = False
        # print "Worker " + self.worker_id + " stopped"
        logger.log('worker {} stopped'.format(self.worker_id))

    def run(self):
        import time
        self.running = True
        # print "Worker " + self.worker_id + " running"
        logger.log('worker {} running'.format(self.worker_id))
        i = 1
        while self.running:
            job = self.beanstalk.reserve()
            # print "Worker "+self.worker_id+" get message "+job.body
            logger.log('Worker {} get message {}'.format(self.worker_id, job.body))
            time.sleep(1)
            job.delete()
            i += 1

    # def close(self):
    #     self.beanstalk.close()
