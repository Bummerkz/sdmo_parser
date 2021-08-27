from queue import Queue
from devices import AbstractDevice

recvQueue = Queue()

recvQueue.put(AbstractDevice())

msg = recvQueue.get_nowait()

print(msg)