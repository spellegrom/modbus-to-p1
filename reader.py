#!/usr/bin/env python3

import datetime
import logging
import time

from ctypes import c_ushort
import requests

from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

SLEEP = 0.8

API_SERVERS = (
    ('https://***API-URL***/api/v1/datalogger/dsmrreading',
     '***API-KEY***'),
)

MODBUS_CLIENT_HOST = '1.2.4.5'
MODBUS_CLIENT_PORT = 502
MODBUS_CLIENT_UNITID = 1


def main():
    """
    Main process loop
    """
    logging.getLogger().setLevel(logging.INFO)
    logging.info('[%s] Starting Modbus poller...', datetime.datetime.now())

    # init modbus client
    connection = ModbusClient(host=MODBUS_CLIENT_HOST, port=MODBUS_CLIENT_PORT, unit_id=MODBUS_CLIENT_UNITID,
                              auto_open=True, timeout=5)

    while True:
        for telegram in read_modbus(connection):
            logging.info('[%s] P1 telegram generated', datetime.datetime.now())
            print(telegram)

            for current_server in API_SERVERS:
                current_api_url, current_api_key = current_server
                logging.info('[%s] Sending telegram to DSMR-reader at: %s', datetime.datetime.now(), current_api_url)

                try:
                    send_telegram_to_remote_dsmrreader(
                        telegram=telegram,
                        api_url=current_api_url,
                        api_key=current_api_key
                    )
                except Exception as error:
                    logging.exception(error)

        time.sleep(SLEEP)


def send_telegram_to_remote_dsmrreader(telegram, api_url, api_key):
    """
    Send the P1 telegram to DSMR-readers API.
    :param str telegram: Complete P1 telegram, including CRC16.
    :param str api_url: DSMR-readers API URL.
    :param str api_key: DSMR-readers API key, can be found in the settings webpage.
    """
    response = requests.post(
        api_url,
        headers={'Authorization': 'Token {}'.format(api_key)},
        data={'telegram': telegram},
        timeout=10,
    )

    if response.status_code != 201:
        logging.error('[%s] DSMR-reader API error: HTTP %d - %s', datetime.datetime.now(), response.status_code,
                      response.text)


def read_modbus(connection):
    """
    Reads the Modbus interface and generates a P1 telegram from it.
    :param connection: Modbus TCP connection to poll.
    :return str: P1 telegram, including CRC16.
    """
    now = datetime.datetime.now()

    buffer = '/Modbus to ESMR 5.0\ \r\n'
    buffer += '\r\n'
    buffer += '1-3:0.2.8(50)\r\n'
    buffer += '0-0:1.0.0(' + now.strftime("%y%m%d%H%M%S") + 'S)\r\n'
    buffer += '0-0:96.1.1({:s})\r\n'.format(read_address_as_hex(connection, 0x4000)[2:])

    buffer += '1-0:1.8.1({:010.3f}*kWh)\r\n'.format(read_address_as_float(connection, 0x600E))
    buffer += '1-0:1.8.2({:010.3f}*kWh)\r\n'.format(read_address_as_float(connection, 0x6010))
    buffer += '1-0:2.8.1({:010.3f}*kWh)\r\n'.format(read_address_as_float(connection, 0x601A))
    buffer += '1-0:2.8.2({:010.3f}*kWh)\r\n'.format(read_address_as_float(connection, 0x601C))

    buffer += '0-0:96.14.0({:04d})\r\n'.format(read_address_as_integer(connection, 0x6048))

    active_power = read_address_as_float(connection, 0x5012)
    if active_power < 0:
        buffer += '1-0:1.7.0({:06.3f}*kW)\r\n'.format(0.0)
        buffer += '1-0:2.7.0({:06.3f}*kW)\r\n'.format(abs(active_power))
    else:
        buffer += '1-0:1.7.0({:06.3f}*kW)\r\n'.format(active_power)
        buffer += '1-0:2.7.0({:06.3f}*kW)\r\n'.format(0.0)

    # Wago's 0x4016 "Power down counter" is the closest to P1's "number of power failures in any phase"
    buffer += '0-0:96.7.21({:05d})\r\n'.format(read_address_as_integer(connection, 0x4016))

    buffer += '1-0:32.7.0({:.1f}*V)\r\n'.format(read_address_as_float(connection, 0x5002))
    buffer += '1-0:52.7.0({:.1f}*V)\r\n'.format(read_address_as_float(connection, 0x5004))
    buffer += '1-0:72.7.0({:.1f}*V)\r\n'.format(read_address_as_float(connection, 0x5006))

    buffer += '1-0:31.7.0({:03.0f}*A)\r\n'.format(abs(read_address_as_float(connection, 0x500C)))
    buffer += '1-0:51.7.0({:03.0f}*A)\r\n'.format(abs(read_address_as_float(connection, 0x500E)))
    buffer += '1-0:71.7.0({:03.0f}*A)\r\n'.format(abs(read_address_as_float(connection, 0x5010)))

    current_flow_l1 = read_address_as_float(connection, 0x5014)
    current_flow_l2 = read_address_as_float(connection, 0x5016)
    current_flow_l3 = read_address_as_float(connection, 0x5018)
    if current_flow_l1 < 0:
        buffer += '1-0:21.7.0({:06.3f}*kW)\r\n'.format(0.0)
        buffer += '1-0:22.7.0({:06.3f}*kW)\r\n'.format(abs(current_flow_l1))
    else:
        buffer += '1-0:21.7.0({:06.3f}*kW)\r\n'.format(current_flow_l1)
        buffer += '1-0:22.7.0({:06.3f}*kW)\r\n'.format(0.0)

    if current_flow_l2 < 0:
        buffer += '1-0:41.7.0({:06.3f}*kW)\r\n'.format(0.0)
        buffer += '1-0:42.7.0({:06.3f}*kW)\r\n'.format(abs(current_flow_l2))
    else:
        buffer += '1-0:41.7.0({:06.3f}*kW)\r\n'.format(current_flow_l2)
        buffer += '1-0:42.7.0({:06.3f}*kW)\r\n'.format(0.0)

    if current_flow_l3 < 0:
        buffer += '1-0:61.7.0({:06.3f}*kW)\r\n'.format(0.0)
        buffer += '1-0:62.7.0({:06.3f}*kW)\r\n'.format(abs(current_flow_l3))
    else:
        buffer += '1-0:61.7.0({:06.3f}*kW)\r\n'.format(current_flow_l3)
        buffer += '1-0:62.7.0({:06.3f}*kW)\r\n'.format(0.0)

    buffer += '!'

    crc = calculate_crc16(buffer)
    buffer += '{:0>4}\r\n'.format(hex(crc)[2:].upper())

    yield buffer


def read_address_as_hex(connection, address):
    """
    Reads the specified address and returns the registers value as hex.
    :param connection: Modbus TCP connection.
    :param address: Address of the register to read, in hex.
    :return hex: Value in the register as hex.
    """
    read = connection.read_holding_registers(int(address), 2)
    return hex(utils.word_list_to_long(read)[0])


def read_address_as_float(connection, address):
    """
    Reads the specified address and returns the registers value as float.
    :param connection: Modbus TCP connection.
    :param address: Address of the register to read, in hex.
    :return float: Value in the register as float.
    """
    read = connection.read_holding_registers(int(address), 2)
    floats = [utils.decode_ieee(f) for f in utils.word_list_to_long(read)]
    return floats[0]


def read_address_as_integer(connection, address):
    """
    Reads the specified address and returns the registers value as integer.
    :param connection: Modbus TCP connection.
    :param address: Address of the register to read, in hex.
    :return int: Value in the register as integer.
    """
    read = connection.read_holding_registers(int(address), 1)
    return int(read[0])


def calculate_crc16(telegram):
    """
    Calculate the CRC16 checksum for the given telegram
    :param str telegram: Complete P1 telegram, from start (/) to finish (!)
    :return: Calculated CRC16 checksum.
    """
    crc16_tab = []
    crc_value = 0x0000

    if len(crc16_tab) == 0:
        for i in range(0, 256):
            crc = c_ushort(i).value
            for j in range(0, 8):
                if crc & 0x0001:
                    crc = c_ushort(crc >> 1).value ^ 0xA001
                else:
                    crc = c_ushort(crc >> 1).value
            crc16_tab.append(hex(crc))

    for char in telegram:
        d = ord(char)
        tmp = crc_value ^ d
        rotated = c_ushort(crc_value >> 8).value
        crc_value = rotated ^ int(crc16_tab[(tmp & 0x00FF)], 0)

    return crc_value


if __name__ == '__main__':
    main()
