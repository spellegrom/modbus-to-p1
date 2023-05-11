# Modbus to ESR5 P1
Modbus-to-P1 is a set of Python scripts build to read a 
Wago 879-3000 MID-meter via Modbus over TCP and create ESMR 5.0-style
P1 telegrams from it. By generating P1 telegrams, one is able to feed the
data into tools like [DSMR-reader](https://github.com/dsmrreader/dsmr-reader).

Modbus-to-P1 is een set Python-scripts gemaakt om Wago 879-3000 MID-meters via 
een Modbus TCP connectie uit te lezen en ESMR 5 P1-telegrams te genereren. Hiermee
wordt het mogelijk de data rechtstreeks in tools als [DSMR-reader](https://github.com/dsmrreader/dsmr-reader)
te lezen.


### Installation
Create a virtualenv and install the dependencies via pip
```
python3 -m venv ~/modbus-tcp/.venv/
~/modbus-tcp/.venv/bin/python3 -m pip install requests==2.30.0 pyModbusTCP==0.2.0 pyserial==3.5
```

And run
```
cd ~/modbus-tcp/
~/modbus-tcp/.venv/bin/python3 reader.py
```


### Readable fields
Not all fields that common smart meters can provide are available in our setup. We're able to map:
```
96.1.1 Serial number -> Modbus 0x4000
1.8.1 Electricity delivered to client T1 -> Modbus 0x600E
1.8.2 Electricity delivered to client T2 -> Modbus 0x6010
2.8.1 Electricity delivered by client T1 -> Modbus 0x601A
2.8.2 Electricity delivered by client T2 -> Modbus 0x601C
96.14.0 Tariff indicator -> Modbus 0x6048

1.7.0 Actual electricity power delivered -> Modbus 0x5012
2.7.0 Actual electricity power received -> Modbus 0x5012

96.7.21 Number of power failures -> Modbus 0x4016 (power down counter)
    Long power failures, power failure event log and voltage sags- and swells are unavailable.

32.7.0 Instantaneous voltage L1 -> Modbus 0x5002
52.7.0 Instantaneous voltage L2 -> Modbus 0x5004
72.7.0 Instantaneous voltage L3 -> Modbus 0x5006

31.7.0 Instantaneous current L1 -> Modbus 0x500C
51.7.0 Instantaneous current L2 -> Modbus 0x500E
71.7.0 Instantaneous current L3 -> Modbus 0x5010

21.7.0 Instantaneous active power L1 (+P) -> Modbus 0x5014
41.7.0 Instantaneous active power L2 (+P) -> Modbus 0x5016
61.7.0 Instantaneous active power L3 (+P) -> Modbus 0x5018

22.7.0 Instantaneous active power L1 (-P) -> Modbus 0x5014
42.7.0 Instantaneous active power L2 (-P) -> Modbus 0x5016
62.7.0 Instantaneous active power L3 (-P) -> Modbus 0x5018
    Active power is read from the same Modbus register and placed into the correct field (+P/-P) depending
    on the Modbus value being negative or not.

!Calculated CRC16 checksum
```

P1 only supports tariff indicator T1 and T2, Wago's T3 and T4 are not used. One could modify the code to add
T3 to T1's values and T4 to T2's values for example if necessary.

### Our hardware setup
We use Wago 879-3000 meters for measuring PV installations, EV chargers and in (sub)leasing
constructions where only one allocation point/meter is provided by the electrical company. The Modbus RTU is
converted to TCP via a cheap [converter](https://www.amazon.nl/dp/B0BGHVRMPJ/) bought on Amazon, powered over
PoE or with a separate DC power supply.

Generated example telegram:
```
/Modbus to ESMR 5.0\

1-3:0.2.8(50)
0-0:1.0.0(230511122720S)
0-0:96.1.1(22010469)
1-0:1.8.1(000000.680*kWh)
1-0:1.8.2(000000.012*kWh)
1-0:2.8.1(000478.836*kWh)
1-0:2.8.2(000026.396*kWh)
0-0:96.14.0(0002)
1-0:1.7.0(00.000*kW)
1-0:2.7.0(02.256*kW)
0-0:96.7.21(00009)
1-0:32.7.0(230.0*V)
1-0:52.7.0(234.9*V)
1-0:72.7.0(240.0*V)
1-0:31.7.0(003*A)
1-0:51.7.0(003*A)
1-0:71.7.0(003*A)
1-0:21.7.0(00.000*kW)
1-0:22.7.0(00.737*kW)
1-0:41.7.0(00.000*kW)
1-0:42.7.0(00.751*kW)
1-0:61.7.0(00.000*kW)
1-0:62.7.0(00.768*kW)
!0173
```

My personal setup, measuring a polyphase PV-system in my house, feeding the
telegrams into DSMR-reader v5:
![DSMR example 1](https://dump.pellegrom.org/modbus-dsmr-ex1.png)
![DSMR example 2](https://dump.pellegrom.org/modbus-dsmr-ex2.png)
![DSMR example 3](https://dump.pellegrom.org/modbus-dsmr-ex3.png)

Single-phase test setup:
![Test setup](https://dump.pellegrom.org/modbus-test-setup.jpg)
