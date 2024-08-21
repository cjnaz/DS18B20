#!/usr/bin/env python3
"""DS18B20 library/driver for Raspberry Pi using the w1_therm kernel driver.

See the README.md.
"""

#==========================================================
#
#  Chris Nelson, Copyright 2024
#
# V1.1 240820  New
#
# Changes pending
#   
#==========================================================

import os
import sys
import logging
from pathlib import Path

READ_ERROR =    -256
CRC_ERROR =     -255
ALARM_MIN =     -55
ALARM_MAX =     125
w1_root_path =  Path('/sys/bus/w1/devices/')


#=====================================================================================
#=====================================================================================
#  C l a s s   D S 1 8 B 2 0
#=====================================================================================
#=====================================================================================

class DS18B20:
    """
## Class DS18B20 (device_id, device_name='DS18B20') - DS18B20 library/driver for Raspberry Pi using the w1_therm kernel driver

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

    """
    def __init__(self, device_id, device_name='DS18B20'):
        self.device_id =        device_id
        self.device_name =      device_name
        self.sensor_path =      w1_root_path / device_id
        self.bus_master_path =  w1_root_path / (os.readlink(self.sensor_path).replace('../../../devices/', '').split('/')[0])


#=====================================================================================
#=====================================================================================
#  r e a d _ t e m p e r a t u r e
#=====================================================================================
#=====================================================================================

    def read_temperature(self, tempunits='C'):
        """
## read_temperature (tempunits='C') - Return the temperature from w1_slave file, with CRC check

***DS18B20() class member function***

### Parameter
`tempunits` (str, default 'C')
- Must be 'C', 'F' or 'K', else ValueError is raised.

### Returns
- (float) Read temperature in tempunits
- (int) -255:  CRC_ERROR
- (int) -256:  READ_ERROR
- Raises `ValueError` if tempunits is not valid
        """

        try:
            w1_slave = (self.sensor_path / 'w1_slave').read_text()
                # 8d 01 32 ce 7f ff 7f 10 03 : crc=03 YES
                # 8d 01 32 ce 7f ff 7f 10 03 t=24812
            logging.debug(f"{self.device_id} / {self.device_name} - w1_slave file content:\n{w1_slave[:-1]}")    # trim off trailing '\n'
        except Exception as e:
            logging.debug(f"{self.device_id} / {self.device_name} - w1_slave read failed.\n  {e}")
            return READ_ERROR

        if 'YES' not in w1_slave:
            logging.debug(f"{self.device_id} / {self.device_name} - w1_slave read CRC failed")
            return CRC_ERROR
        
        try:
            temp = w1_slave.split('\n')[1].split('t=')[1]
            temp = float(temp) / 1000
        except Exception as e:
            logging.debug(f"{self.device_id} / {self.device_name} - failed extracting temperature from w1_slave.\n  {e}")
            return READ_ERROR

        temp = convert_T(temp, tempunits)

        logging.debug (f"{self.device_id} / {self.device_name} - temperature:  {temp:7.3f} {tempunits}")
        return temp


#=====================================================================================
#=====================================================================================
#  r e a d _ t e m p e r a t u r e 2
#=====================================================================================
#=====================================================================================

    def read_temperature2(self, tempunits='C'):
        """
## read_temperature2 (tempunits='C') - Return the temperature from temperature file.  Used with bulk_convert_trigger().

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
        """

        try:
            temperature = (self.sensor_path / 'temperature').read_text()
            logging.debug(f"{self.device_id} / {self.device_name} - temperature file content:  {temperature[:-1]}")
        except Exception as e:
            logging.debug(f"{self.device_id} / {self.device_name} - temperature read failed.\n  {e}")
            return READ_ERROR

        try:
            temp = float(temperature) / 1000
        except Exception as e:
            logging.debug(f"{self.device_id} / {self.device_name} - failed extracting temperature from temperature file.\n  {e}")
            return READ_ERROR

        temp = convert_T(temp, tempunits)

        logging.debug (f"{self.device_id} / {self.device_name} - temperature:  {temp:7.3f} {tempunits}")
        return temp


#=====================================================================================
#=====================================================================================
#  r e a d _ s c r a t c h p a d
#=====================================================================================
#=====================================================================================

    def read_scratchpad(self):
        """
## read_scratchpad () - Return the w1_slave file line 1.  Forces a new temperature conversion.

***DS18B20() class member function***

With debug logging, logs full w1_slave file, temperature (bytes 0 & 1), TH and TL (bytes 2 & 3), and resolution in the config register (byte 4).

### Returns
- (str) Just line 1 (9 bytes and CRC calc/confirmation) from the w1_slave file (not the second line which include 't=xxxxx')
- (int) -256:  READ_ERROR
        """
        try:
            w1_slave_file = (self.sensor_path / 'w1_slave').read_text()
                # 8d 01 32 ce 7f ff 7f 10 03 : crc=03 YES
                # 8d 01 32 ce 7f ff 7f 10 03 t=24812
            logging.debug (f"{self.device_id} / {self.device_name} - w1_slave file content:\n{w1_slave_file[:-1]}")
        except:
            logging.debug (f"{self.device_id} / {self.device_name} - w1_slave file read failed")
            return READ_ERROR
        
        line = w1_slave_file.split('\n')[0].split()

        # Decode temperature bytes 0 and 1
        msB = int(line[1], base=16)
        lsB = int(line[0], base=16)
        temp_bytes = ((msB & 0x07) << 8) + lsB
        tempC = (float(temp_bytes)/16-128)  if msB & 0x80  else (temp_bytes/16)
        logging.debug (f"{self.device_id} / {self.device_name} - temperature code:  {line[1]} {line[0]}  {tempC:7.3f} C,  {convert_T(tempC, 'F'):7.3f} F,  {convert_T(tempC, 'K'):7.3f} K")

        # Decode TH and TL bytes 2 and 3
        TH_byte = int(line[2], base=16)
        TH = -(TL_byte & 0x7f)-128  if TH_byte & 0x80  else TH_byte
        logging.debug (f"{self.device_id} / {self.device_name} - High alarm limit:  {line[2]}     {TH:3} C,      {convert_T(TH, 'F'):7.3f} F,  {convert_T(TH, 'K'):7.3f} K")
        TL_byte = int(line[3], base=16)
        TL = (TL_byte & 0x7f)-128  if TL_byte & 0x80  else TL_byte
        logging.debug (f"{self.device_id} / {self.device_name} - Low  alarm limit:  {line[3]}     {TL:3} C,      {convert_T(TL, 'F'):7.3f} F,  {convert_T(TL, 'K'):7.3f} K")

        # Decode resolution code from config register
        resolution = (int(line[4], base=16) >> 5) + 9
        logging.debug (f"{self.device_id} / {self.device_name} - Resolution:        {line[4]}      {resolution}")

        # Log paths
        logging.debug (f"{self.device_id} / {self.device_name} - Sensor root directory:     {self.sensor_path}")
        logging.debug (f"{self.device_id} / {self.device_name} - Bus master root directory: {self.bus_master_path}")

        return line


#=====================================================================================
#=====================================================================================
#  g e t _ r e s o l u t i o n
#=====================================================================================
#=====================================================================================

    def get_resolution(self):
        """
## get_resolution () - Return the current resolution setting in the config register

***DS18B20() class member function***

### Returns
- (int) Current resolution setting in the config register, eg 12
        """
        resolution = int(((self.sensor_path / 'resolution')).read_text()[:-1])
        logging.debug (f"{self.device_id} / {self.device_name} - Current resolution setting:    {resolution}")
        return resolution
    

#=====================================================================================
#=====================================================================================
#  s e t _ r e s o l u t i o n
#=====================================================================================
#=====================================================================================

    def set_resolution(self, resolution):
        """
## set_resolution (resolution) - Set the configuration register resolution field.  Requires root privilege (sudo).

***DS18B20() class member function***

### Parameter
`resolution` (int or str)
- 9, 10, 11, or 12

### Returns
- (int) New resolution setting, eg 12
        """
        try:
            resolution = str(resolution)
        except:
            raise ValueError ("resolution value must be int or str 9, 10, 11 or 12")
        if resolution not in ['9', '10', '11', '12']:
            raise ValueError ("resolution value must be int or str 9, 10, 11 or 12")
        (self.sensor_path / 'resolution').write_text(resolution)
        return self.get_resolution()


#=====================================================================================
#=====================================================================================
#  g e t _ a l a r m _ t e m p s
#=====================================================================================
#=====================================================================================

    def get_alarm_temps(self):
        """
## get_alarm_temps () - Return the current <TH TL> alarm settings

***DS18B20() class member function***

### Returns
- (str) Current <TL TH> alarm settings pair, eg '-15 20'
- Values are degrees C
        """

        alarm_temps = ((self.sensor_path / 'alarms')).read_text()[:-1]
        logging.debug (f"{self.device_id} / {self.device_name} - Current alarm TL TH settings:  {alarm_temps}")
        return alarm_temps
    

#=====================================================================================
#=====================================================================================
#  s e t _ a l a r m _ t e m p s
#=====================================================================================
#=====================================================================================

    def set_alarm_temps(self, TL, TH):
        """
## set_alarm_temps (TL, TH) - Set the alarm TL and TH registers.  Requires root privilege (sudo).

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

        """

        try:
            TL = int(TL)
        except:
            raise ValueError (f"alarm temps must be int or str values between {ALARM_MIN} and {ALARM_MAX}.  Values are degrees C.")
        if TL < ALARM_MIN or TL > ALARM_MAX:
            raise ValueError (f"alarm temps must be int or str values between {ALARM_MIN} and {ALARM_MAX}.  Values are degrees C.")
        try:
            TH = int(TH)
        except:
            raise ValueError (f"alarm temps must be int or str values between {ALARM_MIN} and {ALARM_MAX}.  Values are degrees C.")
        if TH < ALARM_MIN or TH > ALARM_MAX:
            raise ValueError (f"alarm temps must be int or str values between {ALARM_MIN} and {ALARM_MAX}.  Values are degrees C.")
        alarm_temps = f"{str(TL)} {str(TH)}"
        (self.sensor_path / 'alarms').write_text(alarm_temps)
        return self.get_alarm_temps()


#=====================================================================================
#=====================================================================================
#  c o p y _ s c r a t c h p a d
#=====================================================================================
#=====================================================================================

    def copy_scratchpad(self):
        """
## copy_scratchpad () - write scratchpad TH, TL, and resolution to EEPROM.  Requires root privilege (sudo).

***DS18B20() class member function***

### Returns
- None
        """
        (self.sensor_path / 'eeprom_cmd').write_text('save\n')
        logging.debug (f"{self.device_id} / {self.device_name} - scratchpad saved to EEPROM")
    

#=====================================================================================
#=====================================================================================
#  r e c a l l _ E 2
#=====================================================================================
#=====================================================================================

    def recall_E2(self):
        """
## recall_E2 () - Restore EEPROM TH, TL, and resolution to scratchpad.  Requires root privilege (sudo).

***DS18B20() class member function***

### Returns
- None
        """
        (self.sensor_path / 'eeprom_cmd').write_text('restore\n')
        logging.debug (f"{self.device_id} / {self.device_name} - EEPROM restored to scratchpad")


#=====================================================================================
#=====================================================================================
#  b u l k _ c o n v e r t _ t r i g g e r
#=====================================================================================
#=====================================================================================

    def bulk_convert_trigger(self):
        """
## bulk_convert_trigger () - Trigger parallel temp conversions for all sensors on this sensor's bus.

***DS18B20() class member function***

Requires root privilege (sudo), or <chmod 666 /sys/bus/w1/devices/w1_bus_masterX/therm_bulk_read>.
Note that the chmod must be redone after each boot.

Follow with calls to <sensor>.read_temperature2() for each sensor on the bus.

### Returns
- (int) 1 on successful trigger.  Returns after the parallel conversion time of all sensors on the bus.
- (int) 0 if trigger was not successful
- (int) -1 if at least one sensor is still in conversion
        """
        # https://docs.kernel.org/w1/slaves/w1_therm.html
        # A bulk read of all devices on the bus could be done writing trigger to therm_bulk_read 
        # entry at w1_bus_master level. This will send the convert command to all devices on the 
        # bus, and if parasite powered devices are detected on the bus (and strong pullup is enabled 
        # in the module), it will drive the line high during the longer conversion time required 
        # by parasited powered device on the line. Reading therm_bulk_read will return 0 if no bulk 
        # conversion pending, -1 if at least one sensor still in conversion, 1 if conversion is 
        # complete but at least one sensor value has not been read yet. Result temperature is then 
        # accessed by reading the temperature entry of each device, which may return empty if 
        # conversion is still in progress. Note that if a bulk read is sent but one sensor is not 
        # read immediately, the next access to temperature on this device will return the 
        # temperature measured at the time of issue of the bulk read command (not the current 
        # temperature).

        therm_bulk_read_reg = self.bus_master_path / 'therm_bulk_read'
        therm_bulk_read_reg.write_text('trigger\n')
        logging.debug ("therm_bulk_read triggered")
        return self.bulk_convert_status()


#=====================================================================================
#=====================================================================================
#  b u l k _ c o n v e r t _ s t a t u s
#=====================================================================================
#=====================================================================================

    def bulk_convert_status(self):
        """
## bulk_convert_status () - Return the status of bulk/parallel sensor conversions and reading on this sensor's bus.

***DS18B20() class member function***

### Returns
- (int) 1 if any sensor on this sensor's bus has not yet be read with read_temperature2()
- (int) 0 if all sensors on this sensor's bus have been read
- (int) -1 if at least one sensor is still in conversion
        """
        therm_bulk_read_reg = self.bus_master_path / 'therm_bulk_read'
        status = int(therm_bulk_read_reg.read_text()[:-1])
        logging.debug (f"therm_bulk_read status  {status}")
        return status


#=====================================================================================
#=====================================================================================
#  g e t _ c o n v _ t i m e
#=====================================================================================
#=====================================================================================

    def get_conv_time(self):
        """
## get_conv_time () - Return the current conversion time setting

***DS18B20() class member function***

### Returns
- (int) Currently set conversion time in milliseconds, eg 750
        """
        conv_time = int(((self.sensor_path / 'conv_time')).read_text()[:-1])
        logging.debug (f"{self.device_id} / {self.device_name} - Current conversion time:   {conv_time}")
        return conv_time


#=====================================================================================
#=====================================================================================
#  s e t _ c o n v _ t i m e
#=====================================================================================
#=====================================================================================

    def set_conv_time(self, conv_setting):
        """
## set_conv_time (conv_setting) - Set the conversion time for temperature measurements.  Requires root privilege (sudo).

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
        """
        try:
            conv_setting = int(conv_setting)
        except:
            raise ValueError ("conv_setting value must be int or str => 0")
        if conv_setting < 0:
            raise ValueError ("conv_setting value must be int or str => 0")
        (self.sensor_path / 'conv_time').write_text(str(conv_setting))
        return self.get_conv_time()


#=====================================================================================
#=====================================================================================
#  g e t _ e x t _ p o w e r
#=====================================================================================
#=====================================================================================

    def get_ext_power(self):
        """
## get_ext_power () - Return the external power status

***DS18B20() class member function***

### Returns
- (int) 0: Parasitic powered
- (int) 1: Externally powered
        """
        ext_power = int(((self.sensor_path / 'ext_power')).read_text()[:-1])
        logging.debug (f"{self.device_id} / {self.device_name} - External power status:     {ext_power}")
        return ext_power


#=====================================================================================
#=====================================================================================
#  c o n v e r t _ T
#=====================================================================================
#=====================================================================================

def convert_T(tempC, units):
    if units == 'C':
        return tempC
    elif units == 'F':
        return tempC*1.8 +32
    elif units == 'K':
        return tempC + 273.15
    else:
        raise ValueError(f"Temperature units must be C, F, or K.  Received <{units}> ")


#=====================================================================================
#=====================================================================================
#  c l i
#=====================================================================================
#=====================================================================================

def cli():

    import time
    import argparse
    import datetime
    import sys
    import importlib.metadata
    __version__ = importlib.metadata.version(__package__ or __name__)

    desc = """DS18B20 driver and CLI/demo for Raspberry Pi

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
"""

    DEFAULT_NAME = "DS18B20"

    parser = argparse.ArgumentParser(description=desc + __version__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('DeviceID', nargs='?', default='NOT-SPECIFIED',
                        help=f"ID of target device, eg 28-0b2280337113")
    parser.add_argument('-m', '--mode', type=int, default=-0,
                        help=f"Test mode select (default 0)")
    parser.add_argument('-n', '--name', type=str, default=DEFAULT_NAME,
                        help=f"Name of the sensor to be displayed (default {DEFAULT_NAME})")
    parser.add_argument('-r', '--resolution', type=int, default=12,
                        help=f"Resolution value (9, 10, 11, or 12) to be set with --mode 4 (default 12)")
    parser.add_argument('-L', '--TL', type=int, default=-25,
                        help=f"TL alarm value (degrees C) to be set with --mode 6 (default -25)")
    parser.add_argument('-H', '--TH', type=int, default=50,
                        help=f"TH alarm value (degrees C) to be set with --mode 6 (default 50)")
    parser.add_argument('-c', '--conv-time', type=int, default=0,
                        help=f"Conversion time setting or trigger measurement operation  (default 0 - set to spec value)")

    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Print debug-level status and activity messages")
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__,
                        help="Print version number and exit")
    args = parser.parse_args()


    if args.mode == 0:                      # Dump info for all sensors (-m 0)  (DeviceID is optional, ignored)
        logging.getLogger().setLevel(logging.DEBUG)
        sensor_list = sorted(w1_root_path.glob('28*'))
        for sens in sensor_list:
            sensor = DS18B20(sens.stem)
            logging.debug (f"\nSensor <{sens}> on bus master <{sensor.bus_master_path}>:")
            sensor.read_scratchpad()
            sensor.get_conv_time()
            sensor.get_ext_power()
        sys.exit()


    if args.verbose == 0:
        logging.getLogger().setLevel(logging.INFO)
    elif args.verbose == 1:
        logging.getLogger().setLevel(logging.DEBUG)

    sensor = DS18B20(args.DeviceID, args.name)


    if args.mode == 1:                      # Get current temp (-m 1)
        start_dt = datetime.datetime.now()
        temp = sensor.read_temperature()
        logging.info (f"<{temp:7.3f}> C  from read_temperature()  Elapsed time  {(datetime.datetime.now() - start_dt).total_seconds()}\n")
        temp = sensor.read_temperature(tempunits='F')
        logging.info (f"<{temp:7.3f}> F  from read_temperature()  Elapsed time  {(datetime.datetime.now() - start_dt).total_seconds()}\n")
        temp = sensor.read_temperature(tempunits='K')
        logging.info (f"<{temp:7.3f}> K  from read_temperature()  Elapsed time  {(datetime.datetime.now() - start_dt).total_seconds()}\n")
        temp = sensor.read_temperature2()
        logging.info (f"<{temp:7.3f}> C  from read_temperature2() Elapsed time  {(datetime.datetime.now() - start_dt).total_seconds()}\n")


    if args.mode == 2:                      # Read scratchpad (-m 2)
        logging.info (sensor.read_scratchpad())


    if args.mode == 3:                      # Get current resolution (-m 3)
        logging.info (sensor.get_resolution())


    if args.mode == 4:                      # Set resolution (-m 4 -r 9)
        logging.info (sensor.set_resolution(args.resolution))


    if args.mode == 5:                      # Get current alarm temps (-m 5)
        logging.info (sensor.get_alarm_temps())


    if args.mode == 6:                      # Set alarm temps (-m 6 -L 20 -H 30)
        logging.info (sensor.set_alarm_temps(args.TL, args.TH))


    if args.mode == 7:                      # Send bulk_convert_trigger (-m 7)
        logging.info (sensor.bulk_convert_trigger())


    if args.mode == 8:                      # Save scratchpad to EEPROM (-m 8)
        logging.info (sensor.copy_scratchpad())


    if args.mode == 9:                      # Restore EEPROM to scratchpad (-m 9)
        logging.info (sensor.recall_E2())


    if args.mode == 10:                     # Get current conversion time (-m 10)
        logging.info (sensor.get_conv_time())


    if args.mode == 11:                     # Set conversion time or start measurement (-m 11 -c 1)
        logging.info (sensor.set_conv_time(args.conv_time))

    if args.mode == 12:                     # Get parasitic/external power status (-m 12)
        logging.info (sensor.get_ext_power())


    if args.mode == 20:                     # Minimal example for README
        sensor = DS18B20(args.DeviceID, args.name)
        logging.info (f"Current temperature for sensor {sensor.device_name} / {sensor.device_id}:  {sensor.read_temperature(tempunits='F'):7.3f} F")


    if args.mode == 21:                     # Demonstrate saving alarm/resolution to EEPROM and restoring (-m 21)
        logging.info ("\n\nInitial state")
        sensor.read_scratchpad()

        logging.info ("\n\nSet scratchpad to alarms -5 +5 and resolution 9, then save to EEPROM")
        sensor.set_alarm_temps(-5, 5)
        sensor.set_resolution(9)
        sensor.read_scratchpad()
        sensor.copy_scratchpad()
        time.sleep(1)

        logging.info ("\n\nSet scratchpad to alarms -50 +50 and resolution 11")
        sensor.set_alarm_temps(-50, 50)
        sensor.set_resolution(11)
        sensor.read_scratchpad()

        logging.info ("\n\nRestore settings from EEPROM to scratchpad")
        sensor.recall_E2()
        time.sleep(1)
        sensor.read_scratchpad()

        logging.info ("\n\nReset to alarms 15 60 and resolution 12, save to EEPROM")
        sensor.set_alarm_temps(15, 60)
        sensor.set_resolution(12)
        sensor.copy_scratchpad()


    if args.mode == 22:                     # Demonstrate bulk/parallel temperature conversions and sensor reads (-m 22)
        slaves_on_this_bus = ((sensor.bus_master_path / 'w1_master_slaves').read_text()).split('\n')[:-1]   # Throw away last entry blank line
        print (f"Slaves on this bus: {slaves_on_this_bus}")

        start_dt = datetime.datetime.now()
        sensor.bulk_convert_trigger()
        logging.info (f"Elapsed time after bulk_convert_trigger:                     {(datetime.datetime.now() - start_dt).total_seconds()}\n")

        for slave in slaves_on_this_bus:
            _sensor = DS18B20(slave)
            logging.info (_sensor.read_temperature2())
            logging.info (f"Elapsed time after {slave} read:                     {(datetime.datetime.now() - start_dt).total_seconds()}")
            logging.info (f"Expecting <1> until last sensor read:                        {_sensor.bulk_convert_status()}\n")


if __name__ == '__main__':
    sys.exit(cli())
