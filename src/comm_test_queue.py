from threading import Thread, Event
from queue import Queue, Empty
from logging import getLogger
from time import sleep

LOGGER_NAME = 'main'

class DeviceCommunicate():

    def __init__(self, queue: Queue = None):
        self._queue = queue # Queue() if recv_queue is None else recv_queue
        self._stopEvent = Event()
        self._status = Event()
        self._thread = None
        self._logger = getLogger(LOGGER_NAME)

    def _start_listen(self):
        if isinstance(self._thread, Thread):
            if self._thread.isAlive():
                self._logger.debug('Already started')
                return True
            else:
                self._thread = None
        self._thread = Thread(name='CommThread', target=self._listen_thread)
        self._thread.start()
        self._logger.info('Started devices thread')
        return True

    def _stop_listen(self):
        if isinstance(self._thread, Thread):
            if self._thread.isAlive():
                self._logger.info('Stopping...')
                self._stopEvent.set()
                self._thread.join()
                self._logger.debug('Stopped')
                return True
            else:
                self._thread = None
                return True
        return True

    def _listen_thread(self):
        self._logger.info('Started devices polling thread')
        while 1:
            if self._stopEvent.is_set():
                self._logger.info('Stopping devices polling thread')
                break
            msg = {
                'test': 'message',
            }
            try:
                self._queue.put(msg)
            except Empty:
                pass
            else:
                self._logger.info('Recieved message: ')
            sleep(1)

    def get_queue(self):
        if self._queue is None:
            self._queue = Queue()
        return self._queue