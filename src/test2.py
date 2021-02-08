import journal
from datetime import datetime
import time

# now =
now = unicode(datetime.now().replace(microsecond = 0))
n = 1
r = '1,2,3'
v = 'a,b,c'
payload = {'d': now, 'id': 'ID', 'n': n, 'r': r, 'v': v}
# for x in range(6
# 5000):
#     data.append([datetime.now(), 'another payload'])

journal.saveData(payload, 'fc', 90, dev=True)

records = journal.upload('fc', dev=True)
print (records)

for payload in records:
    print(payload[1])

server = '123'
port = 8080
dest = {'server': server, 'port': port}
url = 'http://{server}:{port}/data/setReg.php'.format(server=server, port=port)