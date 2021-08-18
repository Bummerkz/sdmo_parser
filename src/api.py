from http.client import HTTPConnection, HTTPSConnection, HTTPException
from urllib.parse import urlencode
from socket import error
from datetime import datetime
from logging import getLogger

from endpoint import EndpointData

LOGGER_NAME = 'main'


class Api:
    BASE_PATH = 'data'  # No leading /

    DANFOSS_PATH = 'setReg.php'
    DANFOSS_RESULT_PATH = 'setRegResult.php'
    ELECTRIC_PATH = 'setElectric.php'

    def __init__(self, addr: str):
        self._logger = getLogger(LOGGER_NAME)
        if addr.startswith('https://'):
            self._connClass = HTTPSConnection
            self._addr = addr[len('https://'):]
            self._logger.debug('Api connects through HTTPS to %s' % self._addr)
        elif addr.startswith('http://'):
            self._connClass = HTTPConnection
            self._addr = addr[len('http://'):]
            self._logger.debug('Api connects through HTTP to %s' % self._addr)
        else:
            raise IncorrectAddressException(
                'Addr: %s. Should start with http:// or https://' % addr)

    def send_data(self, path, data):
        conn = self._connClass(self._addr)
        url = '/%s?%s' % (path, urlencode(data))
        self._logger.debug('Sending data %s to %s' % (data, path))
        try:
            conn.request('GET', url)
        except (HTTPException, error):
            self._logger.warning('No connection to host %s' % self._addr)
            raise NoConnectionException
        response = conn.getresponse()
        if response.getcode() == 200:
            return response.read().decode('utf-8')
        else:
            self._logger.warning('Got http error code %d with message: %s' % (
                response.code, response.reason))

    def _prepare_data(self, data: EndpointData):
        reg_list = []
        reg_vals = []
        for reg in data.data:
            reg_list.append(str(reg.id))
            reg_vals.append(str(reg.value))

        request = {
            'd': str(data.time),
            'id': data.endpointId,
            'n': data.deviceId,
            'r': ','.join(reg_list),
            'v': ','.join(reg_vals)
        }

        return request

    def send_danfoss_data(self, data: EndpointData):
        request = self._prepare_data(data)
        self._logger.info('Sending Danfoss data %s' % request)
        if data.isResult:
            self.send_data(self.BASE_PATH + '/' + self.DANFOSS_RESULT_PATH, request)
        else:
            self.send_data(self.BASE_PATH + '/' + self.DANFOSS_PATH, request)

    def send_electric_data(self, data: EndpointData):
        request = self._prepare_data(data)
        self._logger.info('Sending Electric data %s' % request)
        self.send_data(self.BASE_PATH + '/' + self.ELECTRIC_PATH, request)


class ApiException(Exception):
    pass


class NoConnectionException(ApiException):
    pass


class IncorrectAddressException(ApiException):
    pass
