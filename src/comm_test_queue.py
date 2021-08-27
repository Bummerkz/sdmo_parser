from threading import Thread, Event
from queue import Queue, Empty
from logging import getLogger
from time import sleep

LOGGER_NAME = 'main'

class DeviceCommunicate():
    TIMEOUT = 1  # seconds

    def __init__(self, recv_callback: callable = None,
                 recv_queue: Queue = None, send_queue: Queue = None):
        self._recvCallback = recv_callback
        self._recvQueue = recv_queue # Queue() if recv_queue is None else recv_queue
        self._sendQueue = Queue() if send_queue is None else send_queue
        self._stopEvent = Event()
        self._status = Event()
        self._thread = None
        self._logger = getLogger(LOGGER_NAME)

    def _start_listen(self):
        if isinstance(self._thread, Thread):
            if self._thread.isAlive():
                self._logger.debug('Already listening')
                return True
            else:
                self._thread = None
        self._thread = Thread(name='ListenThread', target=self._listen_thread)
        self._thread.start()
        self._logger.info('Started listen')
        return True

    def _stop_listen(self):
        if isinstance(self._thread, Thread):
            if self._thread.isAlive():
                self._logger.info('Stopping listening')
                self._stopEvent.set()
                self._thread.join()
                self._logger.debug('Stopped')
                return True
            else:
                self._thread = None
                return True
        return True

    def _listen_thread(self):
        self._logger.info('Started listening thread')
        while 1:
            if self._stopEvent.is_set():
                self._logger.info('Stopping listening server')
                break
            msg = {
                'test': 'message',
            }
            try:
                self._recvQueue.put(msg)
            except Empty:
                pass
            else:
                self._logger.info('Recieved message: testing')
            sleep(10)

    def get_send_queue(self):
        return self._sendQueue

    def get_recv_queue(self):
        if self._recvQueue is None:
            self._recvQueue = Queue()
        return self._recvQueue