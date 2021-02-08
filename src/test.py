def crc16(data, offset, length):
    if data is None or offset < 0 or offset > len(data) - 1 and offset + length > len(data):
        return 0
    # print("uzunluk=", len(data))
    # print(data)

    crc = 0xFFFF
    for i in range(length):
        crc ^= data[offset + i]
        for j in range(8):
            # print(crc)
            if ((crc & 0x1) == 1):
                # print("bb1=", crc)
                crc = int((crc / 2)) ^ 40961
                # print("bb2=", crc)
            else:
                crc = int(crc / 2)
    return crc & 0xFFFF

def crc16_ascii(data):
    xor_in = 0x0000  # initial value
    xor_out = 0x0000  # final XOR value
    poly = 0x8005  # generator polinom (normal form)

    reg = xor_in
    for octet in data:
        # reflect in
        for i in range(8):
            topbit = reg & 0x8000
            if octet & (0x80 >> i):
                topbit ^= 0x8000
            reg <<= 1
            if topbit:
                reg ^= poly
        reg &= 0xFFFF
        # reflect out
    return reg ^ xor_out

arr = [0x80, 0x00]

print(crc16(arr, 0, 2))