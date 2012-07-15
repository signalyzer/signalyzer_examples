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
	s.write_u32(port, 'I2C_CLOCK_RATE', 0, 400000);

	#---------------------------------------------------------------------------------------------
	# simple I2C write transaction (queued):
	# start : control_word : address_byte : data_byte : stop

	# select queue with id = 1 for operation.
	# from this point everything will be stored in queue to be executed later
	s.write_u32(port, 'QUEUE_ACTIVE', 0, 1);

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

	# now we run the queue to perform the bus transaction
	# write_value parameter for QUEUE_RUN attribute sets what operation will be performed on the queue
	# it is a bitfied
	# 0x0001 - RUN
	# 0x0002 - FLUSH_TXB, the tx buffer will be flushed after queue execution
	# 0x0004 - FLUSH_RXB, the rx buffer will be flushed afte queue execution
	# for example, here queue will be executed but both tx-buffer and rx-buffer will be saved, 
	#the rx buffer is irrelevant here as this is write operation
	s.write_u32(port, 'QUEUE_RUN', 1, 5);
	
	# delay here to ensure eeprom memory chip gets time to complete its own write operation
	time.sleep(0.1);
	
	# since txb buffer was not flushed during last operation, the queue can be re-run over and over without need for reconstructing it
	s.write_u32(port, 'QUEUE_RUN', 1, 5);
	
	# delay here to ensure eeprom memory chip gets time to complete its own write operation
	time.sleep(0.1);

	s.write_u32(port, 'QUEUE_RUN', 1, 5);
	
	# now we are done with queue, just flush buffers
	s.write_u32(port, 'QUEUE_RUN', 1, 6);    
	
	# queue id = 0 is for non-queued operation. switch back to non-queue mode if needed
	s.write_u32(port, 'QUEUE_ACTIVE', 0, 0);

	time.sleep(0.1);

	#---------------------------------------------------------------------------------------------
	# read operations, queued transfer first with single byte read

	# select queue with id = 1 for operation.
	# from this point everything will be stored in queue to be executed later
	s.write_u32(port, 'QUEUE_ACTIVE', 0, 1);

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

	# read value (note: this read operation will not return a value because queued mode is being used)
	s.read_u8(port, 'I2C_DATA', 0);

	# generate stop condition
	s.write_u32(port, 'I2C_STOP_CONDITION', 0, 1);

	# now we run the queue to perform the bus transaction
	s.write_u32(port, 'QUEUE_RUN', 1, 1);

	# read value
	read_value = s.read(port, 'QUEUE_RX_DATA', 0, 8);

	print read_value

	# queue id = 0 is for non-queued operation. switch back to non-queue mode if needed
	s.write_u32(port, 'QUEUE_ACTIVE', 0, 0);

	time.sleep(0.1);

except Exception, e:
    print 'Exception {0}'.format(e)

s.dispose()