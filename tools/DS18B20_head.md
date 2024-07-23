# DS18B20 library/driver for Raspberry Pi using the w1_therm kernel driver

Skip to [API documentation](#links)

This module provides a clean and complete(*) interface for using DS18B20 temperature sensors 
using the w1_therm kernel driver.  

Supports:
- Reading temperatures
- Bulk parallel conversion of temperatures for all sensors on the bus
- Resolution setting and Alarm thresholds setting in scratchpad
- Scratchpad save/restore to/from EEPROM
- Multiple w1 busses


(*) NOTE:  Alarm search is not currently supported.  I've not found any useful documentation for triggering an alarm search nor reading back 
the in-alarm sensor list.  I'm happy to add the feature if I only knew how.

Do read the fine [datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf).

<br>

## Command Line Interface and Demo

Once installed (pip install DS18B20), a cli tool is available.  The cli tool provides some useful debug and configuration features (such as setting and permanently saving 
the resolution setting), and also a few demonstration cases (such as triggering a bulk/parallel conversion on multiple sensors and reading back their values).

```
$ DS18B20cli -h
usage: DS18B20cli [-h] [-m MODE] [-n NAME] [-r RESOLUTION] [-L TL] [-H TH] [-v] [-V] [DeviceID]

DS18B20 driver and CLI/demo for Raspberry Pi

Modes:
    0:  Dump info for all sensors (-m 0)  (DeviceID is optional, don't care)
    1:  Get current temp (-m 1)
    2:  Read scratchpad (-m 2)
    3:  Get current resolution (-m 3)
    4:  Set resolution (-m 4 -r 9)
    5:  Get current alarm temps (-m 5)
    6:  Set alarm temps (-m 6 -L 20 -H 30)
    7:  Send bulk_convert_trigger (-m 7)
    8:  Save scratchpad to EEPROM (-m 8)
    9:  Restore EEPROM to scratchpad (-m 9)
    10: Demonstrate saving alarm/resolution to EEPROM and restoring (-m 10)
    11: Demonstrate bulk/parallel temperature conversions and sensor reads (-m 11)
    20: Minimal example for README (-m 20)
1.0

positional arguments:
  DeviceID              ID of target device, eg 28-0b2280337113

optional arguments:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  Test mode select (default 0)
  -n NAME, --name NAME  Name of the sensor to be displayed (default DS18B20)
  -r RESOLUTION, --resolution RESOLUTION
                        Resolution value (9, 10, 11, or 12) to be set with --mode 4 (default 12)
  -L TL, --TL TL        TL alarm value (degrees C) to be set with --mode 6 (default -25)
  -H TH, --TH TH        TH alarm value (degrees C) to be set with --mode 6 (default 50)
  -v, --verbose         Print debug-level status and activity messages
  -V, --version         Print version number and exit
```

<br>

## A Minimal Example

In its simplest form, to use this library simply declare (instantiate) a sensor using its ID then issue a read_temperature() call.
The cli tool mode 20 demonstrates this:

```
    if args.mode == 20:                     # Minimal example for README
        sensor = DS18B20(args.DeviceID, args.name)
        logging.info (f"Current temperature for sensor {sensor.device_name} / {sensor.device_id}:  {sensor.read_temperature(tempunits='F'):7.3f} F")
```

... And resultant output:

```
$ DS18B20cli 28-0b228004203c --name "My_Sensor" --mode 20
INFO:root:Current temperature for sensor My_Sensor / 28-0b228004203c:   76.212 F
```

<br>

## Useful for debug

Mode 2 calls `read_scratchpad()` which invokes a dump and parse of a sensor's return results register, `w1_slave`:

```
$ DS18B20cli 28-0b228004203c --name "My_Sensor" --mode 2 --verbose
DEBUG:root:28-0b228004203c / My_Sensor - w1_slave file content:
84 01 0a 00 7f ff 7f 10 a6 : crc=a6 YES
84 01 0a 00 7f ff 7f 10 a6 t=24250
DEBUG:root:28-0b228004203c / My_Sensor - temperature code:  01 84   24.250 C,   75.650 F,  297.400 K
DEBUG:root:28-0b228004203c / My_Sensor - High alarm limit:  0a      10 C,       50.000 F,  283.150 K
DEBUG:root:28-0b228004203c / My_Sensor - Low  alarm limit:  00       0 C,       32.000 F,  273.150 K
DEBUG:root:28-0b228004203c / My_Sensor - Resolution:        7f      12
DEBUG:root:28-0b228004203c / My_Sensor - Sensor root directory:      /sys/bus/w1/devices/28-0b228004203c
DEBUG:root:28-0b228004203c / My_Sensor - Bus master root directory:  /sys/bus/w1/devices/w1_bus_master1
INFO:root:['84', '01', '0a', '00', '7f', 'ff', '7f', '10', 'a6', ':', 'crc=a6', 'YES']
```

<br>

## References
    - https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf
    - https://docs.kernel.org/w1/slaves/w1_therm.html
    - https://docs.kernel.org/w1/w1-generic.html

