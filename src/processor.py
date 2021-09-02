from logging import getLogger
from http_server import HTTPGetRequest
# import message
from endpoint import Double485Endpoint
from api import Api
from time import sleep
from queue import Queue, Empty
from threading import Event, Thread

LOGGER_NAME = 'main'


class Processor:

    SET_REG_HTTP_COMMAND = '/setReg.php' # изменить значения регистров
    # GET_ALL_SETTINGS_COMMAND = '/getSettings.php' #
    GET_SETTING_COMMAND = '/getReg.php' # получить значения регистров

    SET_DEVICE_COMMAND = '/setDevice.php' # добавить или изменить устройство
    CLEAR_DEVICE_COMMAND = '/clearDevice.php' # удалить устройство
    SET_PARAM_COMMAND = '/setParam.php' # изменить конфигурацию регистров
    GET_SETUP_COMMAND = '/getSetup.php' # получить конфигурацию сервера и устройств
    SET_SETUP_COMMAND = '/setSetup.php' # изменить конфигурацию сервера
    TEST_COMMAND = '/test.php' # опрос устройств

    ENDPOINTS = {
        'A83CCB814F9DCB6A': {
            'id': 82,
            'name': 'Скважина 72'
        },
        'A83CCB42E0182308': {
            'id': 180,
            'name': 'Скважина 184'
        },
        'A83CCBDC053698DD': {
            'id': 219,
            'name': 'Скважина 281'
        },
        'A83CCBF04484564E': {
            'id': 0,
            'name': '-=TEST-485=-'
        }
    }

    def __init__(self, device_communicate_queue: Queue, http_request_queue: Queue, CFG):
        self._endpoints = {}
        self._cfg = CFG
        self._endpoints_by_id = {}
        for dev_eui in self.ENDPOINTS.keys():
            self._endpoints[dev_eui] = Double485Endpoint(dev_eui,
                                                         self.ENDPOINTS[dev_eui]['id'])
            self._endpoints_by_id[self.ENDPOINTS[dev_eui]['id']] = self._endpoints[
                dev_eui]
        # self._api = api
        self._logger = getLogger(LOGGER_NAME)
        # self._vegaRecvQueue = vega_recv_queue
        # self._vegaSendQueue = vega_send_queue
        self._deviceCommunicateQueue = device_communicate_queue

        self._httpRequestQueue = http_request_queue
        self._stopEvent = Event()
        self._thread = None

    def start(self):
        if self._thread is None:
            self._thread = Thread(name='DeviceProcessorThread', target=self.message_processor)
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

    def message_processor(self):
        self._logger.info('Started message processor')
        while 1:
            if self._stopEvent.is_set():
                self._logger.info('Stopping message processor')
                break
            
            # try:
            #     msg = self._vegaRecvQueue.get_nowait()
            # except Empty:
            #     pass
            # else:
            #     self.process_message(msg)

            try:
                msg = self._deviceCommunicateQueue.get_nowait()
            except Empty:
                pass
            else:
                self._logger.info(msg)
            
            try:
                req = self._httpRequestQueue.get_nowait()
            except Empty:
                pass
            else:
                self.process_http_req(req)

            if self._httpRequestQueue.empty():
                sleep(5)

    # def process_message(self, msg: message.AbstractMessage):
    #     self._logger.debug('Got a message: %s' % str(msg))
    #     if isinstance(msg, message.DataMessage):
    #         self._logger.info('Got a data message: %s' % str(msg))
    #         endpoint = self._endpoints.get(msg.devEui)
    #         if endpoint is None:
    #             self._logger.debug('Unknown devEui: %s' % msg.devEui)
    #             return None
    #         self._logger.debug('Endpoint is %s' % self.ENDPOINTS[msg.devEui]['name'])
    #         if len(msg.data) == 0:
    #             self._logger.warning('Empty data n message')
    #             return None
    #         endpoint_data = endpoint.process(msg.data)
    #         if endpoint_data is None:
    #             self._logger.debug('Got unknown packet type. Not processing.')
    #             return None
    #         endpoint_data.time = msg.time
    #         if endpoint_data.deviceId == 1:
    #             self._api.send_danfoss_data(endpoint_data)
    #         elif endpoint_data.deviceId == 2:
    #             self._api.send_electric_data(endpoint_data)
    #         else:
    #             self._logger.warning('Unknown device id %d' % endpoint_data.deviceId)
    #             return None

    def process_http_req(self, req: HTTPGetRequest):
        self._logger.debug('Got a http GET request: %s' % str(req))

        if req.name == self.SET_REG_HTTP_COMMAND:
            self._logger.info('Got a command to set device registers')
        
            if len(req.params) == 0 or req.params.get('r') is None or req.params.get(
                'v') is None or req.params.get('id') is None:
                self._logger.warning('Got empty or wrong setReg request')
                return
            
            self.set_reg(req)

        elif req.name == self.GET_SETTING_COMMAND:
            self._logger.info('Got a command to get some device registers')
            
            if len(req.params) == 0 or req.params.get('id') is None:
                self._logger.warning('Got empty or wrong getReg request')
                return
            
            self.get_reg(req)

    def set_reg(self, req: HTTPGetRequest):

        regs = req.params.get('r').split(',')
        values = req.params.get('v').split(',')
        
        if len(regs) != len(values):
            self._logger.warning('Got wrong setReg request (length of v and r not equal)')
            return
        if len(regs) > 8:
            self._logger.warning('Got more than 8 regs. Sending only first 8.')
            regs = regs[0:8]
            values = values[0:8]
        
        try:
            dev_id = int(req.params['id'])
        except ValueError:
            self._logger.warning('Incorrect device id %s' % req.params['id'])
            return
        
        endpoint = self._endpoints_by_id.get(dev_id)
        
        if endpoint is None:
            self._logger.warning('Unknown device id %s' % dev_id)
            return
        
        packet, port = endpoint.set_primary_settings(regs, values)
        msg = message.DeviceSendMessage()
        msg.devEui = endpoint.devEui
        msg.data = packet
        msg.port = port
        
        self._logger.debug('Sending message to %s' % endpoint.devEui)
        self._vegaSendQueue.put(msg)

    def get_reg(self, req: HTTPGetRequest):

        try:
            dev_id = int(req.params['id'])
        except ValueError:
            self._logger.warning('Incorrect device id %s' % req.params['id'])
            return
        endpoint = self._endpoints_by_id.get(dev_id)
        if endpoint is None:
            self._logger.warning('Unknown device id %s' % dev_id)
            return
        regs = req.params.get('r').split(',')
        if len(regs) > 8:
            self._logger.warning('Got more than 8 regs. Sending only first 8.')
            regs = regs[0:8]
        packet, port = endpoint.read_primary_settings(regs)
        msg = message.DeviceSendMessage()
        msg.devEui = endpoint.devEui
        msg.data = packet
        msg.port = port
        self._logger.debug('Sending message to %s' % endpoint.devEui)
        self._vegaSendQueue.put(msg)
    
    def set_device(self):
        pass

    def clear_device(self):
        pass
    
    def set_param(self):
        pass

    def get_setup(self):
        pass

    def set_setup(self):
        pass

    def test(self):
        pass
