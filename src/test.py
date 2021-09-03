from threading import Thread, Event, enumerate
from queue import Queue, Empty
from logging import getLogger, basicConfig, DEBUG
import time

LOGGER_NAME = 'main'
LOGGER_NAME = 'main'
FORMAT = '[%(asctime)s][%(threadName)s][%(levelname)s] %(message)s'

def prepare_logger():
    logger = getLogger(LOGGER_NAME)
    logger.setLevel(DEBUG)

    basicConfig(format=FORMAT)
    # handler = RotatingFileHandler(LOG_PATH + '\\' + 'main.log', maxBytes=10485760,
    #                               backupCount=20)
    # formatter = Formatter(format)
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    return logger


class Device():
    def __init__(self, interval, msg, name):
        self._interval = interval
        self._msg = msg
        self._recvQueue = Queue() 
        self._writeQueue = Queue()
        self._stopEvent = Event()
        self._thread = None
        self._status = Event()
        self._name = name

    def start(self):
        if self._thread is None:
            self._stopEvent.clear()
            self._thread = Thread(name='{}DeviceThread'.format(self._name), target=self.process)
            self._thread.start()

    def stop(self):
        self._stopEvent.set()
        if isinstance(self._thread, Thread) and self._thread.is_alive():
            self._thread.join()
        self._thread = None

    def is_running(self):
        if isinstance(self._thread, Thread):
            return self._thread.is_alive()
        return False

    def process(self):
        while True:
            rawData = self.readData()
            self._recvQueue.put(rawData)
            time.sleep(15)
    
    def readData(self):
        return '2134123421342135123512'

    def getRecvQueue(self):
        return self._recvQueue

class DeviceManager:
    TIMEOUT = 1  # seconds

    def __init__(self, recv_queue: Queue = None, write_queue: Queue = None):
        # self._recvCallback = recv_callback
        self._recvQueue = Queue() if recv_queue is None else recv_queue
        self._writeQueue = Queue() if write_queue is None else write_queue
        self._stopEvent = Event()
        self._status = Event()
        self._thread = None
        self._logger = getLogger(LOGGER_NAME)
        self._devices = []

    def start(self):
        if self._thread is None:
            self._stopEvent.clear()
            self._thread = Thread(name='DevicesManagerThread', target=self.process)
            self._thread.start()

    # def _start_listen(self):
    #     if isinstance(self._thread, Thread):
    #         if self._thread.isAlive():
    #             self._logger.debug('Already listening')
    #             return True
    #         else:
    #             self._thread = None
    #     self._thread = Thread(name='ListenThread', target=self._listen_thread)
    #     self._thread.start()
    #     self._logger.info('Started listen')
    #     return True

    # def _stop_listen(self):
    #     if isinstance(self._thread, Thread):
    #         if self._thread.isAlive():
    #             self._logger.info('Stopping listening')
    #             self._stopEvent.set()
    #             self._thread.join()
    #             self._logger.debug('Stopped')
    #             return True
    #         else:
    #             self._thread = None
    #             return True
    #     return True

    def process(self):
        self._logger.info('Started listening thread')

        while True:
            if self._stopEvent.is_set():
                self._logger.info('Stopping listening server')
                break

            try:
                msg = self._writeQueue.get_nowait()
                print(msg)
            except Empty:
                pass
            else:
                self._logger.info('Sending message to device %s')
                
                for device in self._devices:
                    msg = device.getRecvQueue().get_nowait()
                    self._recvQueue.put(msg)
            
            time.sleep(1)

    def write(self, value):
        self._writeQueue.put('Write {} to register'.format(value))

    def get_write_queue(self):
        return self._writeQueue

    def get_recv_queue(self):
        if self._recvQueue is None:
            self._recvQueue = Queue()
        return self._recvQueue
    
    def stop(self):
        self._stopEvent.set()
        if isinstance(self._thread, Thread) and self._thread.is_alive():
            self._thread.join()
        self._thread = None

    def is_running(self):
        if isinstance(self._thread, Thread):
            return self._thread.is_alive()
        return False


class Scheduler():
    def __init__(self, device_write_queue: Queue, device_recv_queue: Queue):
        self._writeQueue = device_write_queue
        self._recvQueue = device_recv_queue
        self._thread = None
        self._stopEvent = Event()

    def start(self):
        if self._thread is None:
            self._stopEvent.clear()
            self._thread = Thread(name='SchedulerThread', target=self.process)
            self._thread.start()

    def process(self):
        while True:
            try:
                msg = self._recvQueue.get_nowait()
                print (msg)
            except Empty:
                pass
                
    def stop(self):
        self._stopEvent.set()
        if isinstance(self._thread, Thread) and self._thread.is_alive():
            self._thread.join()
        self._thread = None

    def is_running(self):
        if isinstance(self._thread, Thread):
            return self._thread.is_alive()
        return False

# prepare_logger()

device_manager = DeviceManager()
device_manager.start()

scheduler = Scheduler(device_manager.get_write_queue(), device_manager.get_recv_queue())
scheduler.start()

# for thread in enumerate(): 
#     print(thread.name)

# device_manager.write('1')
# time.sleep(5)
# device_manager.write('2')
# time.sleep(0.2)
# device_manager.write('3')
# time.sleep(0.2)
# device_manager.write('4')

while True:
    print('Statuses:')
    print('is Scheduler alive: {}'.format(scheduler.is_running()))
    print('is Device Manager alive: {}'.format(device_manager.is_running()))
    print('----------------------------------------------------------------')
    if scheduler.is_running():
        pass
    else:
        scheduler.stop()
        scheduler.start()

    if device_manager.is_running():
        pass
    else:
        device_manager.stop()
        device_manager.start()

    device_manager.write('4')

    print('Active Threads:')
    for thread in enumerate(): 
        print(thread.name)

    time.sleep(5)