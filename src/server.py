# -*- coding:utf-8 -*-
import logging
import devices
import config
# from modbus import ModbusDevice
from find_devices import FindDevices
from advancedhttpserver import *
from advancedhttpserver import __version__

class Handler(RequestHandler):
    def on_init(self):
        self.handler_map['^setReg.php$'] = self.set_reg
        self.handler_map['^getReg.php$'] = self.get_reg
        self.handler_map['^setDevice.php$'] = self.set_device
        self.handler_map['^clearDevice.php$'] = self.clear_device
        self.handler_map['^setParam.php$'] = self.set_param
        self.handler_map['^exception$'] = self.res_exception
        self.handler_map['^getSetup.php$'] = self.get_setup
        self.handler_map['^setSetup.php$'] = self.set_setup
        self.handler_map['^setOscParam.php$'] = self.set_osc
        self.handler_map['^test.php$'] = self.test_devices
        self.handler_map['^$'] = self.home

    def home(self, query):
        message = """<!DOCTYPE html>
                    <html>
                        <head>
                            <meta charset="utf-8">
                            <title>SDMO Parser</title>
                        </head>
                        <body> 
                            <h1>Сервер запущен</h1>
                        </body>
                    </html>
                  """
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(message))
        self.end_headers()
        self.wfile.write(message)
        return

    def set_osc(self, query):
        # $type = $_REQUEST['type'];
        # $value = $_REQUEST['value'];
        # $device = $_REQUEST['device'];

        # switch ($_REQUEST['type']) {

        # case 'update_osc' : 
        # if($reg = $fc_osc_reg[$_REQUEST['value']]) {
        #     $url = "http://".$ip."/setOscParam.php?n=".$device."&".$reg;
        message = "setOsc"
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(message))
        self.end_headers()
        self.wfile.write(message)
        return

    def set_setup(self, query):
        r = query.get('r', [''])[0]
        v = query.get('v', [''])[0]
        cfg = config.get_config()
        if r == '1':
            cfg['Server']['id'] = v
        elif r == '2':
            cfg['Server']['ip'] = v
        elif r == '3':
            cfg['Server']['port'] = v
        elif r == '4':
            cfg['Server']['mode'] = v
        elif r == '5':
            cfg['Server']['server_timeout'] = v
        elif r == '6':
            cfg['Server']['cmd_interval'] = v
        elif r == '6':
            cfg['Server']['status'] = v
        elif r == '7':
            cfg['Server']['sd_interval'] = v
        elif r == '8':
            cfg['Server']['debug_lvl'] = v
        elif r == '9':
            cfg['Server']['reboot'] = v
        elif r == '10':
            cfg['Server']['modbus_only'] = v

        if config.update_config(cfg):
            message = "OK"
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(message))
            self.end_headers()
            self.wfile.write(message)
        else:
            message = "Конфигурация не обновлена!"
            self.send_response(200) # исправить код response
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(message))
            self.end_headers()
            self.wfile.write(message)

        # switch ($_REQUEST['type']) {
        # case 'update_id':
        #     if($value == NULL)
        #         $value = '';
        #     $url = "http://".$ip."/setSetup.php?r=1&v=".$value;
        #     break;
        # case 'update_ip':
        #     $url = "http://".$ip."/setSetup.php?r=2&v=".$value;
        #     break;
        # case 'update_port':
        #     $url = "http://".$ip."/setSetup.php?r=3&v=".$value;
        #     break;
        # case 'update_mode':
        #     $url = "http://".$ip."/setSetup.php?r=4&v=".$value;
        #     break;
        # case 'update_server_timeout':
        #     $url = "http://".$ip."/setSetup.php?r=5&v=".$value;
        #     break;
        # case 'update_cmd_interval':
        #     $url = "http://".$ip."/setSetup.php?r=6&v=".$value;
        #     break;
        # case 'update_status':
        #     $url = "http://".$ip."/setSetup.php?r=6&v=".$value;
        #     break;
        # case 'update_sd_interval':
        #     $url = "http://".$ip."/setSetup.php?r=7&v=".$value;
        #     break;
        # case 'update_debug_lvl':
        #     $url = "http://".$ip."/setSetup.php?r=8&v=".$value;
        #     break;
        # case 'update_reboot':
        #     $url = "http://".$ip."/setSetup.php?r=9&v=".$value;
        #     break;
        # case 'update_Modbus_only':
        #     $url = "http://".$ip."/setSetup.php?r=10&v=".$value;
        #     break;
        return

    def get_setup(self, query):
        cfg = config.get_config()
        sorted_devices = sorted(cfg['Devices'])
        message = """<html><head></head><body>SDMO Parser версия {version}<br>
                    <br>
                    Server:<br>
                    [1] id={id}<br>
                    [2] ip={ip}<br>
                    [3] port={port}<br>
                    [4] mode={mode} (0-by one, 1-all)<br>
                    [5] server timeout={server_timeout} sec<br>
                    [6] cmd interval={cmd_interval} sec<br>
                    <br>
                    SD card:<br>
                    [7] storage SD interval={SD_card_storage_interval} days<br>
                    <br>
                    Service:<br>
                    [8] debug_level={debug_level}<br>
                    [9] reboot on disconnect={reboot}<br>
                    <br>""".format(**cfg['Server'])
        message = message + """
                    Pump:<br>
                    [10] K1={K1}<br>
                    [11] K={K}<br>
                    [12] L={L}<br>
                    [13] R={R}<br>
                    [14] Rm={Rm}<br>
                    [15] H={H}<br>
                    [16] G={G}<br>
                    [17] T={T}<br>
                    [18] Mr={Mr}<br>
                    [19] N={N}<br>
                    [20] angle={angle}<br>
                    [21] H0={H0}<br>
                    [22] H50={H50}<br>
                    [23] Hmax={Hmax}<br>
                    [24] Hmin={Hmin}<br>
                    [25] coeff={coeff}<br>
                    [26] interval={interval} sec<br>
                    [27] dynamo_type={dynamo_type}<br>
                    [28] pistole_x={pistole_x}<br>
                    [29] pistole_y={pistole_y}<br>
                    [30] pump_diam={pump_diam}<br>
                    <br>""".format(**cfg['Pump'])

        for i in sorted_devices:
            device = cfg['Devices'][i]
            if device['port'] == 1:
                port_set = 'RS485,{},{},{},{}'.format(device['baudrate'], device['bytesize'], device['parity'], device['stopbits'])
            elif device['port'] == 0:
                port_set = 'RS232,{},{},{},{}'.format(device['baudrate'], device['bytesize'], device['parity'], device['stopbits'])
            regs = ''
            
            for idx, (k, v) in enumerate(device['regs'].items()):
                regs = regs + k + '(' + v + '),'

            osc_regs = ''
            for idx, (k, v) in enumerate(device['osc_registers'].items()):
                osc_regs = osc_regs + k + '(' + v + '),'

            message = message + "Device {}:<br>".format(i)
            message = message + """
                                name={name}<br>
                                type={type}<br>
                                addr={addr}<br>""".format(**device)
            message = message + "port={}<br>".format(port_set)
            message = message + "send interval={send_interval} sec<br>".format(**device)
            message = message + "regs={}<br>".format(regs)
            message = message + """
                                osc send interval={osc_send_interval} sec (0 - off)<br>
                                osc duration={osc_duration} sec<br>
                                osc frequency={osc_frequency} times/sec<br>
                                osc registers={}<br>
                                <br>""".format(osc_regs, **device)

        message = message + "</body></html>"
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(message))
        self.end_headers()
        self.wfile.write(message)
        return

    def test_devices(self, query):
        # dev = FindDevices
        mess = FindDevices().find_all()
        message = "\n".join(mess)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', len(message))
        self.end_headers()
        self.wfile.write(message)
        return

    def set_param(self, query):
        # case 'update_reg' : 
        #     $reg = $fc_reg[$_REQUEST['pump_type']][$_REQUEST['addtitonal_info']];
        #     $url = "http://".$ip."/setParam.php?n=".$device."&".$reg;
        # set_params_1 = 'setParam.php?n=1&r=1543,1549,1610,1612,1613,1614,1616,1617,1622,1630,1634,1639,1660,1900,1901,1902,1903,1904,1908,1909,1910,1912,1915,1917,1918,1922,1923,1924,1925,1926,1927,1928,1931,1945,1946,1947,1951,1953,1955,1956,1957,1959,1969,1971,1991,1993,1995,1997,1999,1998&v=7,7,3,5,5,3,3,3,2,5,4,4,5,5,5,5,5,5,5,5,5,5,5,2,5,5,5,5,5,5,5,2,2,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,3,5&m=1,1,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,0'
        device_id = query.get('n', [''])[0]
        r_value = query.get('r', [''])[0]
        v_value = query.get('v', [''])[0]
        m_value = query.get('m', [''])[0]
        
        cfg = config.get_config()

        regs = r_value.split(',')
        units = v_value.split(',')
        mode = m_value.split(',')

        new_regs = {}

        for i, reg in enumerate(regs):
            if units[i] == '1': # i1 не подтверждено
                new_regs.update({reg: 'i1'})   
            elif units[i] == '2': # i2
                new_regs.update({reg: 'i2'})   
            elif units[i] == '3': # i4
                new_regs.update({reg: 'i4'})   
            elif units[i] == '4': # u1
                new_regs.update({reg: 'u1'})   
            elif units[i] == '5': # u2
                new_regs.update({reg: 'u2'})   
            elif units[i] == '6': # f не подтверждено
                new_regs.update({reg: 'f'})   
            elif units[i] == '7': # str
                new_regs.update({reg: 'str'})   

        cfg['Devices'][device_id]['regs'] = new_regs

        if config.update_config(cfg):
            message = "OK"
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(message))
            self.end_headers()
            self.wfile.write(message)
        else:
            message = "Конфигурация не обновлена!"
            self.send_response(200) # исправить код response
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(message))
            self.end_headers()
            self.wfile.write(message)
        return

    def clear_device(self, query):
        device_id = query.get('n', [''])[0]
        cfg = devices.clear_device(device_id)
        
        if cfg is not None and cfg != 'no_device':
            self.cfg = cfg
            message = 'Устройство {} удалено!'.format(device_id)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(message))
            self.end_headers()
            self.wfile.write(message)
        else:
            message = 'Ошибка при удалении устройства!'
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(message))
            self.end_headers()
            self.wfile.write(message)
        return

        try:
            del cfg['Devices'][device_id]
            self.cfg = cfg
            message = b'Устройство {} удалено!'.format(device_id)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(message))
            self.end_headers()
            self.wfile.write(message)
        except KeyError as e:
            message = e
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(message))
            self.end_headers()
            self.wfile.write(message)

    def set_device(self, query): # надо реализовать добавление только FC и MERCURY
        # n=0&v=fc,1,1,1,19200,8,E,1,120,10800,30,5
		# http://192.168.1.71/setDevice.php?n=0&v=fc,1,1,1,19200,8,E,1,120,10800,30,5
        # if $device == 'fc'
        #     $url = "http://".$ip."/setDevice.php?n=0&v=fc,1,1,".$_REQUEST['addtitonal_info'];
        # elseif($device == 'modbus')
        #     $url = "http://".$ip."/setDevice.php?n=0&v=modbus,1,0,".$_REQUEST['addtitonal_info'];
        # elseif($device == 'neva')
        #     $url = "http://".$ip."/setDevice.php?n=0&v=IEC,1,2,".$_REQUEST['addtitonal_info'];
        # elseif($device == 'mercury')
        #     $url = "http://".$ip."/setDevice.php?n=0&v=mercury,1,3,".$_REQUEST['addtitonal_info'];
        # elseif($device == 'psh')
        #     $url = "http://".$ip."/setDevice.php?n=0&v=psh,1,4,".$_REQUEST['addtitonal_info'];
        # param = query.get('v', [''])[0]
        # cfg = devices.add_new_device(param)
        # cfg = config.get_config()

        # if cfg is not None:
        #     self.cfg = cfg
        #     message = 'Устройство добавлено!'
        #     self.send_response(200)
        #     self.send_header('Content-Type', 'text/plain')
        #     self.send_header('Content-Length', len(message))
        #     self.end_headers()
        #     self.wfile.write(message)
        # else:
        #     message = 'Ошибка при добавлении нового устройства!'
        #     self.send_response(500)
        #     self.send_header('Content-Type', 'text/plain')
        #     self.send_header('Content-Length', len(message))
        #     self.end_headers()
        #     self.wfile.write(message)
        return

    def get_reg(self, query): # надо реализовать
        n_value = query.get('n', [''])[0]
        # mb = ModbusDevice(n_value)
        # mb.modbus_connect()
        # message = "\n".join(mb.get_modbus_fc(True))
        # mb.modbus_client.close()
        # logging.info(message)
        # self.send_response(200)
        # self.send_header('Content-Type', 'text/plain')
        # self.send_header('Content-Length', len(message))
        # self.end_headers()
        # self.wfile.write(message)
        return

    def set_reg(self, query): # надо реализовать
        # n_value = query.get('n', [''])[0]
        # r_value = query.get('r', [''])[0]
        # v_value = query.get('v', [''])[0]
        # t_value = query.get('t', [''])[0]
        # mb = ModbusDevice(n_value)
        # mb.modbus_connect()
        # r = r_value.split(',')
        # regs = list(map(int, r))
        # v = v_value.split(',')
        # values = list(map(int, v))
        # mb.write_modbus(regs, values)
        # message = b'n value: ' + n_value.encode('utf-8') + \
        #           ', r_value: ' + r_value.encode('utf-8') + \
        #           ', v_value: ' + v_value.encode('utf-8') + \
        #           ', t_value: ' + t_value.encode('utf-8')
        # self.send_response(200)
        # self.send_header('Content-Type', 'text/plain')
        # self.send_header('Content-Length', len(message))
        # self.end_headers()
        # self.wfile.write(message)
        return

    def res_exception(self, query):
        raise Exception('this is an exception, oh noes!')

def StartServer():
    print("AdvancedHTTPServer version: {0}".format(__version__))
    # logging.getLogger('').setLevel(logging.DEBUG)
    # console_log_handler = logging.StreamHandler()
    # console_log_handler.setLevel(logging.INFO)
    # console_log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
    # logging.getLogger('').addHandler(console_log_handler)

    server = AdvancedHTTPServer(Handler)
    server.server_version = 'AdvancedHTTPServer'
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
    return 0