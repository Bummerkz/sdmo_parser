import config
from fc_regs import REGS

cfg = config.get_config(dev=True)

# import journal
# from datetime import datetime
# import time

# # now =
# now = unicode(datetime.now().replace(microsecond = 0))
# n = 1
# r = '1,2,3'
# v = 'a,b,c'
# payload = {'d': now, 'id': 'ID', 'n': n, 'r': r, 'v': v}
# # for x in range(6
# # 5000):
# #     data.append([datetime.now(), 'another payload'])

# journal.saveData(payload, 'fc', 90, dev=True)

# records = journal.upload('fc', dev=True)
# print (records)

# for payload in records:
#     print(payload[1])

# server = '123'
# port = 8080
# dest = {'server': server, 'port': port}
# url = 'http://{server}:{port}/data/setReg.php'.format(server=server, port=port)

# for i, reg in enumerate(x for x in REGS): 
#     # for i, (k, v) in enumerate(reg.items()):
#     # if reg['lenght']:
#     #     lenght = reg['lenght']
#     try:
#         addr = reg['class']._addr
#         print('Addr: {}'.format(addr))
#     except:
#         pass
    # logging.info('type: {}'.format())
    # reg['class']._value = self.read_fc_register(addr, lenght, unit)

    # if rr != 0:
    #     decoded = decoded.decode_16bit_int()
    #     logging.info('Decoded result: {}'.format(decoded))
    
    # result.append(str(decoded))

regs = cfg["Devices"]['1']["regs"]
print regs['1900']