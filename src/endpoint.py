from devices import AbstractDevice, DanfossDevice, MercuryDevice, NevaDevice


class AbstractEndpoint:
    DEVICE_CLASSES = {}


class Double485Endpoint(AbstractEndpoint):
    DEVICE_CLASSES = {
        DanfossDevice.DEVICE_ID: DanfossDevice,
        MercuryDevice.DEVICE_ID: MercuryDevice,
        NevaDevice.DEVICE_ID: NevaDevice,
    }

    def __init__(self):
        self._devices = {}

    # def _get_device_obj(self, dev_type):
    #     dev = self._devices.get(dev_type)
    #     if dev is not None:
    #         return dev
    #     dev_class = self.DEVICE_CLASSES.get(dev_type)
    #     if dev_class is None:
    #         raise IncorrectDeviceException
    #     self._devices[dev_type] = dev_class()
    #     return self._devices[dev_type]

    # def process(self, data: bytes):
    #     packet_type = data[0]
    #     dev_type = data[1]
    #     if packet_type in self.PACKET_TYPES_CURRENT_DATA:
    #         device = self._get_device_obj(dev_type)
    #         endpoint_data = EndpointData()
    #         endpoint_data.endpointId = self.apiId
    #         endpoint_data.data = device.process(data[2:])
    #     elif packet_type in self.PACKET_TYPES_SETTINGS:
    #         device = self._get_device_obj(dev_type)
    #         endpoint_data = EndpointData()
    #         endpoint_data.endpointId = self.apiId
    #         endpoint_data.data = device.process_settings(data[2:])
    #     elif packet_type in self.PACKET_TYPES_RESPONSE:
    #         endpoint_data = self._process_response(data)
    #         if isinstance(endpoint_data, EndpointData):
    #             endpoint_data.endpointId = self.apiId
    #         return endpoint_data
    #     else:
    #         return None
    #     endpoint_data.deviceId = device.API_ID
    #     return endpoint_data

    # def _process_response(self, packet: bytes):
    #     port = packet[1]
    #     func = packet[2]
    #     if port == self.DEVPORT_SETTINGS:
    #         if func == self.DEVFUNC_WRITE_DSETTINGS:
    #             reg_count = len(packet[3:]) // 3
    #             device = self._get_device_obj(self.PRIMARY_DEVICE)
    #             endpoint_data = EndpointData()
    #             endpoint_data.deviceId = device.API_ID
    #             endpoint_data.isResult = True
    #             for i in range(reg_count):
    #                 offset = 3 + i * 3
    #                 reg_addr = int(packet[offset:offset + 2].hex(), 16)
    #                 reg_raw = packet[offset + 2:offset + 3]
    #                 reg = device.get_result_reg(reg_addr, reg_raw)
    #                 endpoint_data.data.append(reg)
    #             return endpoint_data
    #         elif func == self.DEVFUNC_READ_DSETTINGS:
    #             reg_count = len(packet[3:]) // 6
    #             device = self._get_device_obj(self.PRIMARY_DEVICE)
    #             endpoint_data = EndpointData()
    #             endpoint_data.deviceId = device.API_ID
    #             for i in range(reg_count):
    #                 offset = 3 + i * 6
    #                 reg_addr = int(packet[offset:offset + 2].hex(), 16)
    #                 reg_raw = packet[offset + 2:offset + 6]
    #                 rreg = device.get_result_reg(reg_addr)
    #                 reg = device.get_register(rreg.id)
    #                 reg.raw = reg_raw
    #                 endpoint_data.data.append(reg)
    #             return endpoint_data
    #     else:
    #         pass

    # def set_primary_settings(self, reg_ids: list, reg_values: list):
    #     device = self._get_device_obj(self.PRIMARY_DEVICE)
    #     regs = []
    #     for reg_id, reg_value in zip(reg_ids, reg_values):
    #         regs.append(device.get_register(int(reg_id), int(reg_value)))
    #     return self._prepare_dsettings_packet(regs), self.DEVPORT_SETTINGS

    # def read_primary_settings(self, reg_ids: list):
    #     device = self._get_device_obj(self.PRIMARY_DEVICE)
    #     regs = []
    #     for reg_id in reg_ids:
    #         regs.append(device.get_register(int(reg_id)))
    #     return self._prepare_dsettings_read_packet(regs), self.DEVPORT_SETTINGS

    # def _prepare_dsettings_packet(self, regs: list):
    #     packet = bytes([self.DEVFUNC_WRITE_DSETTINGS])
    #     for reg in regs:
    #         if len(reg.raw) != 4:
    #             raise IncorrectSettingTypeException
    #         packet += bytes([(reg.addr >> 8) & 0xFF])
    #         packet += bytes([reg.addr & 0xFF])
    #         packet += reg.raw
    #     return packet

    # def _prepare_dsettings_read_packet(self, regs: list):
    #     packet = bytes([self.DEVFUNC_READ_DSETTINGS])
    #     for reg in regs:
    #         packet += bytes([(reg.addr >> 8) & 0xFF])
    #         packet += bytes([reg.addr & 0xFF])
    #     return packet

    # def req_all_settings(self):
    #     packet = bytes([self.DEVFUNC_GET_ALL_SETTINGS])
    #     return packet, self.DEVPORT_SETTINGS


# Endpoint Data Container
class EndpointData:
    def __init__(self):
        self.deviceId = None
        self.data = []
        self.time = None
        self.isResult = False


class EndpointException(Exception):
    pass


class IncorrectDeviceException(EndpointException):
    pass


class IncorrectSettingTypeException(EndpointException):
    pass
