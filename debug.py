#!/usr/bin/env python3

import logging
import time

from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

SLEEP = 1.0
modbus = ModbusClient(host='10.0.3.185', port=502, unit_id=1, auto_open=True, timeout=1)


def main():
    logging.getLogger().setLevel(logging.INFO)
    while True:
        read_modbus()
        time.sleep(SLEEP)


def read_modbus():
    print('4000 Serial number:              {0}'.format(read_address_as_hex(0x4000, 2)))
    print('4002 Meter code:                 {0}'.format(read_address_as_hex(0x4002, 1)))
    print('4012 L1 current direction:       {0}'.format(read_address_as_hex(0x4012, 1)))
    print('4013 L2 current direction:       {0}'.format(read_address_as_hex(0x4013, 1)))
    print('4014 L3 current direction:       {0}'.format(read_address_as_hex(0x4014, 1)))
    print('4016 Power-down counter:         {:d}\n'.format(read_address_as_int(0x4016)))

    print('5002 L1 voltage:                 {:.3F}*V'.format(read_address_as_float(0x5002, 2)))
    print('5004 L2 voltage:                 {:.3F}*V'.format(read_address_as_float(0x5004, 2)))
    print('5006 L3 voltage:                 {:.3F}*V'.format(read_address_as_float(0x5006, 2)))
    print('5008 Frequency:                  {:.2F}*Hz\n'.format(read_address_as_float(0x5008, 2)))

    print('500C L1 current:                 {:.3F}*A'.format(read_address_as_float(0x500C, 2)))
    print('500E L2 current:                 {:.3F}*A'.format(read_address_as_float(0x500E, 2)))
    print('5010 L3 current:                 {:.3F}*A\n'.format(read_address_as_float(0x5010, 2)))

    print('5012 Total active power:         {:.3F}*kW'.format(read_address_as_float(0x5012, 2)))
    print('5014 L1 active power:            {:.3F}*kW'.format(read_address_as_float(0x5014, 2)))
    print('5016 L2 active power:            {:.3F}*kW'.format(read_address_as_float(0x5016, 2)))
    print('5018 L3 active power:            {:.3F}*kW\n'.format(read_address_as_float(0x5018, 2)))

    print('502A Power factor:               {:.2F}'.format(read_address_as_float(0x502A, 2)))
    print('502C L1 power factor:            {:.2F}'.format(read_address_as_float(0x502C, 2)))
    print('502E L2 power factor:            {:.2F}'.format(read_address_as_float(0x502E, 2)))
    print('5030 L3 power factor:            {:.2F}\n'.format(read_address_as_float(0x5030, 2)))

    print('5032 L1-L2 voltage:              {:.3F}*V'.format(read_address_as_float(0x5032, 2)))
    print('5034 L1-L3 voltage:              {:.3F}*V'.format(read_address_as_float(0x5034, 2)))
    print('5036 L2-L3 voltage:              {:.3F}*V\n'.format(read_address_as_float(0x5036, 2)))

    print('6000 Total active energy:        {:.3F}*kWh'.format(read_address_as_float(0x6000, 2)))
    print('6002 T1 active energy:           {:.3F}*kWh'.format(read_address_as_float(0x6002, 2)))
    print('6004 T2 active energy:           {:.3F}*kWh'.format(read_address_as_float(0x6004, 2)))
    print('604B T3 active energy:           {:.3F}*kWh'.format(read_address_as_float(0x604B, 2)))
    print('604D T4 active energy:           {:.3F}*kWh\n'.format(read_address_as_float(0x604D, 2)))

    print('600C Active energy import:       {:.3F}*kWh'.format(read_address_as_float(0x600C, 2)))
    print('600E T1 active energy import:    {:.3F}*kWh'.format(read_address_as_float(0x600E, 2)))
    print('6010 T2 active energy import:    {:.3F}*kWh'.format(read_address_as_float(0x6010, 2)))
    print('604F T3 active energy import:    {:.3F}*kWh'.format(read_address_as_float(0x604F, 2)))
    print('6051 T4 active energy import:    {:.3F}*kWh'.format(read_address_as_float(0x6051, 2)))

    print('6018 Active energy export:       {:.3F}*kWh'.format(read_address_as_float(0x6018, 2)))
    print('601A T1 active energy export:    {:.3F}*kWh'.format(read_address_as_float(0x601A, 2)))
    print('601C T2 active energy export:    {:.3F}*kWh'.format(read_address_as_float(0x601C, 2)))
    print('6053 T3 active energy export:    {:.3F}*kWh'.format(read_address_as_float(0x6053, 2)))
    print('6055 T4 active energy export:    {:.3F}*kWh\n'.format(read_address_as_float(0x6055, 2)))

    print('6048 Tariff:                     {:d}\n'.format(read_address_as_int(0x6048)))

    print('6006 L1 Total active energy:     {:.3F}*kWh'.format(read_address_as_float(0x6006, 2)))
    print('6012 L1 Active energy import:    {:.3F}*kWh'.format(read_address_as_float(0x6012, 2)))
    print('601E L1 Active energy export:    {:.3F}*kWh\n'.format(read_address_as_float(0x601E, 2)))

    print('6008 L2 Total active energy:     {:.3F}*kWh'.format(read_address_as_float(0x6008, 2)))
    print('6014 L2 Active energy import:    {:.3F}*kWh'.format(read_address_as_float(0x6014, 2)))
    print('6020 L2 Active energy export:    {:.3F}*kWh\n'.format(read_address_as_float(0x6020, 2)))

    print('600A L2 Total active energy:     {:.3F}*kWh'.format(read_address_as_float(0x600A, 2)))
    print('6016 L2 Active energy import:    {:.3F}*kWh'.format(read_address_as_float(0x6016, 2)))
    print('6022 L2 Active energy export:    {:.3F}*kWh\n'.format(read_address_as_float(0x6022, 2)))

    print('608B Resettable day register L1  {:.3F}*kWh'.format(read_address_as_float(0x608B, 2)))
    print('608D Resettable day register L2  {:.3F}*kWh'.format(read_address_as_float(0x608D, 2)))
    print('608F Resettable day register L3  {:.3F}*kWh'.format(read_address_as_float(0x608F, 2)))
    print('-----------------------------------------------')


def read_address_as_float(address, length):
    read = modbus.read_holding_registers(int(address), length)
    floats = [utils.decode_ieee(f) for f in utils.word_list_to_long(read)]
    return floats[0]


def read_address_as_hex(address, length):
    read = modbus.read_holding_registers(int(address), length)
    if length > 1:
        return hex(utils.word_list_to_long(read)[0])
    else:
        return hex(read[0])


def read_address_as_int(address):
    read = modbus.read_holding_registers(int(address), 1)
    return int(read[0])


if __name__ == '__main__':  # pragma: no cover
    main()
