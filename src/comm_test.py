import random

class Modbus():
    def __init__(self):
        pass

    def read_registers(self):
        regs = random.sample(range(1600, 1650), 5)
        values = random.sample(range(0, 100), 5)

        return regs, values