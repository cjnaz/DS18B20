# DS18B20 high-featured library/driver for Raspberry Pi using the w1_therm kernel driver

**NOTE:  _This is the working version._  Pay no attention to the PyPI version named `DS18B20-driver 1.1.2`.  That version 
is broken (package naming problems that lead to a broken install), and there's no way to delete it.**

Skip to [API documentation](#links)

This module provides a clean and mostly complete (*) API for DS18B20 temperature sensors 
using the w1_therm kernel driver.  It also provides a command line interface for interactive dev/debug.

Supports:
- Reading temperatures
- Bulk parallel conversion of temperatures for all sensors on the bus
- Resolution setting and Alarm thresholds setting in scratchpad
- Setting and measuring actual conversion (temperature measurement) time
- Scratchpad save/restore to/from EEPROM
- Multiple w1 busses

(*) Not supported:
 - Alarm search - I've not found any useful documentation for triggering an alarm search nor reading back 
   the in-alarm sensor list.  I'm happy to add the feature if I only knew how.
 - 'features' register (conversion error check and poll for completion)
 - async_io (just needs development)
 - Other sensor models

Tested on Python 3.9.2 and kernel version 6.1.21-v7+ #1642 SMP Mon Apr  3 17:20:52 BST 2023, and should work on similar kernel versions since about 2020.

Do read the fine [datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf).

<br>

## Command Line Interface and Demo

Once installed (pip install DS18B20dvr), a cli tool is available.  The cli tool provides some useful debug and configuration features (such as setting and permanently saving 
the resolution setting), and also a few demonstration cases (such as triggering a bulk/parallel conversion on multiple sensors and reading back their values).

```
$ DS18B20cli -h
usage: DS18B20cli [-h] [-m MODE] [-n NAME] [-r RESOLUTION] [-L TL] [-H TH] [-c CONV_TIME] [-v] [-V] [DeviceID]

DS18B20 driver and CLI/demo for Raspberry Pi

Modes:
    0:  Dump info for all sensors (-m 0)  (DeviceID is optional, ignored)
    1:  Get current temp (-m 1)
    2:  Read scratchpad (-m 2)
    3:  Get current resolution (-m 3)
    4:  Set resolution (-m 4 -r 9)
    5:  Get current alarm temps (-m 5)
    6:  Set alarm temps (-m 6 -L 20 -H 30)
    7:  Send bulk_convert_trigger (-m 7)
    8:  Save scratchpad to EEPROM (-m 8)
    9:  Restore EEPROM to scratchpad (-m 9)
    10: Get current conversion time (-m 10)
    11: Set conversion time or start measurement (-m 11 -c 1)
    12: Get parasitic/external power status (-m 12)

    20: Minimal example for README (-m 20)
    21: Demonstrate saving alarm/resolution to EEPROM and restoring (-m 21)
    22: Demonstrate bulk/parallel temperature conversions and sensor reads (-m 22)
1.2

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
  -c CONV_TIME, --conv-time CONV_TIME
                        Conversion time setting or trigger measurement operation  (default 0 - set to spec value)
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
8b 01 3c 0f 7f ff 7f 10 6c : crc=6c YES
8b 01 3c 0f 7f ff 7f 10 6c t=24687
DEBUG:root:28-0b228004203c / My_Sensor - temperature code:  01 8b   24.688 C,   76.438 F,  297.837 K
DEBUG:root:28-0b228004203c / My_Sensor - High alarm limit:  3c      60 C,      140.000 F,  333.150 K
DEBUG:root:28-0b228004203c / My_Sensor - Low  alarm limit:  0f      15 C,       59.000 F,  288.150 K
DEBUG:root:28-0b228004203c / My_Sensor - Resolution:        7f      12
DEBUG:root:28-0b228004203c / My_Sensor - Sensor root directory:     /sys/bus/w1/devices/28-0b228004203c
DEBUG:root:28-0b228004203c / My_Sensor - Bus master root directory: /sys/bus/w1/devices/w1_bus_master1
INFO:root:['8b', '01', '3c', '0f', '7f', 'ff', '7f', '10', '6c', ':', 'crc=6c', 'YES']
```

Mode 0 (the default mode) invokes a similar dump for every sensor found on the host, across all w1 busses, and includes conversion time and external power status:

```
$ DS18B20cli 
DEBUG:root:
Sensor </sys/bus/w1/devices/28-0b228004203c> on bus master </sys/bus/w1/devices/w1_bus_master1>:
DEBUG:root:28-0b228004203c / DS18B20 - w1_slave file content:
8c 01 3c 0f 7f ff 7f 10 bc : crc=bc YES
8c 01 3c 0f 7f ff 7f 10 bc t=24750
DEBUG:root:28-0b228004203c / DS18B20 - temperature code:  01 8c   24.750 C,   76.550 F,  297.900 K
DEBUG:root:28-0b228004203c / DS18B20 - High alarm limit:  3c      60 C,      140.000 F,  333.150 K
DEBUG:root:28-0b228004203c / DS18B20 - Low  alarm limit:  0f      15 C,       59.000 F,  288.150 K
DEBUG:root:28-0b228004203c / DS18B20 - Resolution:        7f      12
DEBUG:root:28-0b228004203c / DS18B20 - Sensor root directory:     /sys/bus/w1/devices/28-0b228004203c
DEBUG:root:28-0b228004203c / DS18B20 - Bus master root directory: /sys/bus/w1/devices/w1_bus_master1
DEBUG:root:28-0b228004203c / DS18B20 - Current conversion time:   750
DEBUG:root:28-0b228004203c / DS18B20 - External power status:     1
DEBUG:root:
Sensor </sys/bus/w1/devices/28-0b2280337113> on bus master </sys/bus/w1/devices/w1_bus_master1>:
DEBUG:root:28-0b2280337113 / DS18B20 - w1_slave file content:
7a 01 3c 0f 7f ff 7f 10 08 : crc=08 YES
7a 01 3c 0f 7f ff 7f 10 08 t=23625
DEBUG:root:28-0b2280337113 / DS18B20 - temperature code:  01 7a   23.625 C,   74.525 F,  296.775 K
DEBUG:root:28-0b2280337113 / DS18B20 - High alarm limit:  3c      60 C,      140.000 F,  333.150 K
DEBUG:root:28-0b2280337113 / DS18B20 - Low  alarm limit:  0f      15 C,       59.000 F,  288.150 K
DEBUG:root:28-0b2280337113 / DS18B20 - Resolution:        7f      12
DEBUG:root:28-0b2280337113 / DS18B20 - Sensor root directory:     /sys/bus/w1/devices/28-0b2280337113
DEBUG:root:28-0b2280337113 / DS18B20 - Bus master root directory: /sys/bus/w1/devices/w1_bus_master1
DEBUG:root:28-0b2280337113 / DS18B20 - Current conversion time:   750
DEBUG:root:28-0b2280337113 / DS18B20 - External power status:     1
```


<br>

## References
  - [https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf](https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf)
  - [https://docs.kernel.org/w1/slaves/w1_therm.html](https://docs.kernel.org/w1/slaves/w1_therm.html)
  - [https://docs.kernel.org/w1/w1-generic.html](https://docs.kernel.org/w1/w1-generic.html)
  - [https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-driver-w1_therm](https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-driver-w1_therm)



<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [ds18b20](#ds18b20)
- [read_temperature](#read_temperature)
- [read_temperature2](#read_temperature2)
- [read_scratchpad](#read_scratchpad)
- [get_resolution](#get_resolution)
- [set_resolution](#set_resolution)
- [get_alarm_temps](#get_alarm_temps)
- [set_alarm_temps](#set_alarm_temps)
- [copy_scratchpad](#copy_scratchpad)
- [recall_e2](#recall_e2)
- [bulk_convert_trigger](#bulk_convert_trigger)
- [bulk_convert_status](#bulk_convert_status)
- [get_conv_time](#get_conv_time)
- [set_conv_time](#set_conv_time)
- [get_ext_power](#get_ext_power)



<br/>

<a id="ds18b20"></a>

---

# Class DS18B20 (device_id, device_name='DS18B20') - DS18B20 library/driver for Raspberry Pi using the w1_therm kernel driver

### Parameters
`device_id` (str)
- As listed in /sys/bus/w1/devices/, eg '28-0b228004203c'

`device_name` (str, default 'DS18B20')
- User friendly name for the sensor

### Class variables

`device_id` (str)
- device_id from sensor instantiation

`device_name` (str, default 'DS18B20')
- device_name from sensor instantiation

`sensor_path` (Path)
- full pathlib path to the sensor directory

`bus_master_path` (Path)
- full pathlib path the w1 bus master for the sensor

    
<br/>

<a id="read_temperature"></a>

---

# read_temperature (tempunits='C') - Return the temperature from w1_slave file, with CRC check

***DS18B20() class member function***

### Parameter
`tempunits` (str, default 'C')
- Must be 'C', 'F' or 'K', else ValueError is raised.

### Returns
- (float) Read temperature in tempunits
- (int) -255:  CRC_ERROR
- (int) -256:  READ_ERROR
- Raises `ValueError` if tempunits is not valid
        
<br/>

<a id="read_temperature2"></a>

---

# read_temperature2 (tempunits='C') - Return the temperature from temperature file.  Used with bulk_convert_trigger().

***DS18B20() class member function***

If a bulk_convert_trigger() was previously executed, return the previously captured temperature, else take
and return a new measurement.

### Parameter
`tempunits` (str, default 'C')
- Must be 'C', 'F' or 'K', else ValueError is raised.

### Returns
- (float) Read temperature in tempunits
- (int) -256:  READ_ERROR
- Raises `ValueError` if tempunits is not valid
        
<br/>

<a id="read_scratchpad"></a>

---

# read_scratchpad () - Return the w1_slave file line 1.  Forces a new temperature conversion.

***DS18B20() class member function***

With debug logging, logs full w1_slave file, temperature (bytes 0 & 1), TH and TL (bytes 2 & 3), and resolution in the config register (byte 4).

### Returns
- (str) Just line 1 (9 bytes and CRC calc/confirmation) from the w1_slave file (not the second line which include 't=xxxxx')
- (int) -256:  READ_ERROR
        
<br/>

<a id="get_resolution"></a>

---

# get_resolution () - Return the current resolution setting in the config register

***DS18B20() class member function***

### Returns
- (int) Current resolution setting in the config register, eg 12
        
<br/>

<a id="set_resolution"></a>

---

# set_resolution (resolution) - Set the configuration register resolution field.  Requires root privilege (sudo).

***DS18B20() class member function***

### Parameter
`resolution` (int or str)
- 9, 10, 11, or 12

### Returns
- (int) New resolution setting, eg 12
        
<br/>

<a id="get_alarm_temps"></a>

---

# get_alarm_temps () - Return the current <TH TL> alarm settings

***DS18B20() class member function***

### Returns
- (str) Current <TL TH> alarm settings pair, eg '-15 20'
- Values are degrees C
        
<br/>

<a id="set_alarm_temps"></a>

---

# set_alarm_temps (TL, TH) - Set the alarm TL and TH registers.  Requires root privilege (sudo).

***DS18B20() class member function***

Values must be between -55C and +125C.  w1_therm sets TL to the lower of the two temps, TH to the higher.

### Parameters
`TL` (int or str)
- Low temp alarm threshold in degrees C

`TH` (int or str)
- High temp alarm threshold in degrees C

### Returns
- (str) The newly set <TL TH> alarm settings pair, eg '-15 20'
- Raises `ValueError` if TL or TH value is not valid or out of range

        
<br/>

<a id="copy_scratchpad"></a>

---

# copy_scratchpad () - write scratchpad TH, TL, and resolution to EEPROM.  Requires root privilege (sudo).

***DS18B20() class member function***

### Returns
- None
        
<br/>

<a id="recall_e2"></a>

---

# recall_E2 () - Restore EEPROM TH, TL, and resolution to scratchpad.  Requires root privilege (sudo).

***DS18B20() class member function***

### Returns
- None
        
<br/>

<a id="bulk_convert_trigger"></a>

---

# bulk_convert_trigger () - Trigger parallel temp conversions for all sensors on this sensor's bus.

***DS18B20() class member function***

Requires root privilege (sudo), or <chmod 666 /sys/bus/w1/devices/w1_bus_masterX/therm_bulk_read>.
Note that the chmod must be redone after each boot.

Follow with calls to <sensor>.read_temperature2() for each sensor on the bus.

### Returns
- (int) 1 on successful trigger.  Returns after the parallel conversion time of all sensors on the bus.
- (int) 0 if trigger was not successful
- (int) -1 if at least one sensor is still in conversion
        
<br/>

<a id="bulk_convert_status"></a>

---

# bulk_convert_status () - Return the status of bulk/parallel sensor conversions and reading on this sensor's bus.

***DS18B20() class member function***

### Returns
- (int) 1 if any sensor on this sensor's bus has not yet be read with read_temperature2()
- (int) 0 if all sensors on this sensor's bus have been read
- (int) -1 if at least one sensor is still in conversion
        
<br/>

<a id="get_conv_time"></a>

---

# get_conv_time () - Return the current conversion time setting

***DS18B20() class member function***

### Returns
- (int) Currently set conversion time in milliseconds, eg 750
        
<br/>

<a id="set_conv_time"></a>

---

# set_conv_time (conv_setting) - Set the conversion time for temperature measurements.  Requires root privilege (sudo).

***DS18B20() class member function***

### Parameter
`conv_setting` (int or str)
- 0: Set the default conversion time from the datasheet based on the current resolution (eg 750ms for 12-bit resolution)
- 1: Trigger measurement of the actual required conversion time, and set future conversions
  to the measured time.  Note that this value is guardbanded 20% higher than the actual measured
  time, and thus may be higher than the specification time.
- \>1: Set conversion time to `conv_setting`, resolution milliseconds

### Returns
- (int) Currently set conversion time in milliseconds as a result of the `conv_setting` operation
        
<br/>

<a id="get_ext_power"></a>

---

# get_ext_power () - Return the external power status

***DS18B20() class member function***

### Returns
- (int) 0: Parasitic powered
- (int) 1: Externally powered
        