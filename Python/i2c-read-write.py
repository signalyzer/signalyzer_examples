 # Copyright (C) 2012 by Xverve Technologies Inc.
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documentation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sub license, and/or sell
 # copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
import time
import signalyzer

s = signalyzer.new()

try:
	ver = s.read_u32(0, 'CORE_API_VERSION', 0)
	print 'library version = 0x{0:08x}'.format(ver)

	ver = s.read_u32(0, 0xF01, 0)
	print 'library version = 0x{0:08x}'.format(ver)

	# Set HAL for signalyzer library. Currently H2 and H4 devices support only LIBFTD2XX HAL (FTDI drivers)
	# SIGNALYZER_HAL_INTERFACE_TYPE_LIBFTD2XX
	s.write_u32(0, 'CORE_HAL_INTERFACE', 0, 0x01)

	# specify what devices will be listed
	# SIGNALYZER_DEVICE_TYPE_SIGNALYZER_H4
	s.write_u32(0, 'CORE_DEVICE_TYPE', 0, 0x02)

	# specify format of the list library will return. 
	# The API can return either an array of serial numbers, array of device descriptions, or an array of structures signalyzer_device_info_node_t

	# SIGNALYZER_LIST_TYPE_SERIAL_NUMBER
	s.write_u32(0, 'CORE_LIST_TYPE', 0, 0x01)

	print 'list devices by serial number:'
	device_list = s.get_device_list();
	print device_list

	# open device
	s.open(device_list[0])

	#i2c transactions will be done on port 1
	port = 1;

	# activate 5V on Connector A (pin 2 and 26)
	# this is not really necessary for I2C operation, but aux power can be used to power external circuits
	s.write_u32(port, 'AUX_VIO', 1, 1);

	# set operating mode to I2C
	# SIGNALYZER_OPERATING_MODE_I2C	= 0x02
	s.write_u32(port, 'PORT_OPERATING_MODE', 0,  2);

	# set bus clock rate to 100 kHz
	s.write_u32(port, 'I2C_CLOCK_RATE', 0, 100000);

	#---------------------------------------------------------------------------------------------
	# simple I2C write transaction (non-queued):
	# start : control_word : address_byte : data_byte : stop

	# generate start condition
	s.write_u32(port, 'I2C_START_CONDITION', 0, 1);

	# write control word
	s.write_u8(port, 'I2C_DATA', 0, 0xA0);

	# write address
	s.write_u8(port, 'I2C_DATA', 0, 0x00);

	# write value
	s.write_u8(port, 'I2C_DATA', 0, 0x55);

	# generate stop condition
	s.write_u32(port, 'I2C_STOP_CONDITION', 0, 1);

	time.sleep(0.1);

	#---------------------------------------------------------------------------------------------
	# read operations, non-queued transfer first with single byte read

	# generate start condition
	s.write_u32(port, 'I2C_START_CONDITION', 0, 1);

	# write control word
	s.write_u8(port, 'I2C_DATA', 0, 0xA0);

	# write address
	s.write_u8(port, 'I2C_DATA', 0, 0x00);

	# generate repeated start condition
	s.write_u32(port, 'I2C_START_CONDITION', 0, 1);

	# write control word
	s.write_u8(port, 'I2C_DATA', 0, 0xA1);

	# read value
	read_value = s.read_u8(port, 'I2C_DATA', 0);

	print read_value

	# generate stop condition
	s.write_u32(port, 'I2C_STOP_CONDITION', 0, 1);

	time.sleep(0.1);

except Exception, e:
    print 'Exception {0}'.format(e)

s.dispose()