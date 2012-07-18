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

# new()
# create signalyzer context

# dispose()
# dispose signalyzer context

# version()
# read signalyzer library python wrapper version. 
# note: this is wrapper version, version of signalyzer library is read using attribute

# get_device_list()
# retrieves list of attached signalyzer devices.

# open(device_identifier)
# opens connection with specified device

# close()
# closes connection with previously opened device

# write_u8(port, attribute_id, address, write_value)
# writes 8-bit value to specified attribute

# write_u16(port, attribute_id, address, write_value)
# writes 16-bit value to specified attribute

# write_u32(port, attribute_id, address, write_value)
# writes 32-bit value to specified attribute

# write_u64(port, attribute_id, address, write_value)
# writes 64-bit value to specified attribute

# write(port, attribute_id, address, write_array, bits_to_write)
# writes specified number of bits to specified attribute

# read_u8(port, attribute_id, address)
# reads 8-bit value from specified attribute

# read_u16(port, attribute_id, address)
# reads 16-bit value from specified attribute

# read_u32(port, attribute_id, address)
# reads 32-bit value from specified attribute

# read_u64(port, attribute_id, address)
# reads 64-bit value from specified attribute

# read(port, attribute_id, address, bits_to_read)
# reads specified number of bits from specified attribute

# write_read_u8(port, attribute_id, address, write_value)
# writes and read 8-bit value to/from specified attribute

# write_read_u16(port, attribute_id, address, write_value)
# writes and read 16-bit value to/from specified attribute

# write_read_u32(port, attribute_id, address, write_value)
# writes and read 32-bit value to/from specified attribute

# write_read_u64(port, attribute_id, address, write_value)
# writes and read 64-bit value to/from specified attribute

# write_read(port, attribute_id), address, write_array, bits_to_write)
# writes and reads specified number of bits to/from specified attribute

def enum(**enums):
	return type('Enum', (), enums)
	
SIGNALYZER_DEVICE_TYPE = enum(UNDEFINED = 0x00, H2 = 0x01, H4 = 0x02, H2xx = 0x10, H4xx = 0x20, H6xx = 0x40, ALL = 0xFFFFFFFF)
SIGNALYZER_LIST_TYPE = enum(UNDEFINED = 0x00, SERIAL_NUMBER	= 0x01, DESCRIPTION = 0x02, INFO_NODE = 0x03)
SIGNALYZER_HAL_INTERFACE_TYPE = enum(UNDEFINED = 0x00, LIBFTD2XX = 0x01, LIBFTDI = 0x02)
SIGNALYZER_OPERATING_MODE = enum (UNDEFINED = 0x00, SPI = 0x01, I2C = 0x02, JTAG = 0x03, SWD = 0x04)

def signalyzer_set_clk_freq(device_signalyzer, device_port, clk_rate):	
	updated_rate = clk_rate / 5
	
	device_signalyzer.write_u32(device_port, 'HAL_CLK_FREQUENCY', 0,  updated_rate)

def signalyzer_set_mode(device_signalyzer, device_port, pin_bitmask_direction):	
	# set the direction of the port. note: this and next command must always be executed in the same order
	device_signalyzer.write_u32(device_port, 'HAL_BIT_MODE_IO_MASK', 0,  pin_bitmask_direction)
	
	# 1 = asynchronous and 4 = synchronous bit-bang modes
	device_signalyzer.write_u32(device_port, 'HAL_BIT_MODE', 0,  4)

def signalyzer_bitbang_write(device_signalyzer, device_port, write_data):
	l = len(write_data)
	l_bits = l * 8

	# bitbang uses raw data mode
	device_signalyzer.write(device_port, 'HAL_DATA', 0,  write_data, l_bits);	
	
	start = time.clock()

	# in sync bitbang mode for every byte written out, one byte is read back
	# need to read all bytes back
	
	# wait for data to be read
	while True:
		bytes_in_rx = device_signalyzer.read_u32(device_port, 'HAL_BYTES_IN_RX_BUFFER', 0)
		
		if bytes_in_rx >= l:
			break
			
		elapsed = time.clock() - start
		
		if elapsed >= 1:
			raise Exception("Did not receive data in time")
	
	# read and discard datat
	device_signalyzer.read(device_port, 'HAL_DATA', 0, l_bits)

def signalyzer_bitbang_write_read(device_signalyzer, device_port, write_data):
	l = len(write_data)
	l_bits = l * 8

	# bitbang uses raw data mode
	device_signalyzer.write(device_port, 'HAL_DATA', 0,  write_data, l_bits);	
	
	start = time.clock()

	# in sync bitbang mode for every byte written out, one byte is read back
	# need to read all bytes back
	
	# wait for data to be read
	while True:
		bytes_in_rx = device_signalyzer.read_u32(device_port, 'HAL_BYTES_IN_RX_BUFFER', 0)
		
		if bytes_in_rx >= l:
			break
			
		elapsed = time.clock() - start
		
		if elapsed >= 1:
			raise Exception("Did not receive data in time")
	
	#read data and return it	
	return device_signalyzer.read(device_port, 'HAL_DATA', 0, l_bits)
	
s = signalyzer.new()

try:
	# read signalyzer library version
	ver = s.read_u32(0, 'CORE_API_VERSION', 0)
	print 'library version = 0x%08x' % ver

	# attribute supplied to the call can be string, as it shown above, or its numeric value
	ver = s.read_u32(0, 0xF01, 0)
	print 'library version = 0x%08x' % ver

	# read python wrapper version information
	ver = s.version()
	print 'signalyzer library python wrapper version = 0x%08x' %ver
	
	# Set HAL for signalyzer library. Currently H2 and H4 devices support only LIBFTD2XX HAL
	s.write_u32(0, 'CORE_HAL_INTERFACE', 0, SIGNALYZER_HAL_INTERFACE_TYPE.LIBFTD2XX)

	# specify what devices will be listed	
	s.write_u32(0, 'CORE_DEVICE_TYPE', 0, SIGNALYZER_DEVICE_TYPE.H4)

	# specify format of the list library will return. 
	# The API can return either an array of serial numbers, array of device descriptions, 
	# or an array of structures signalyzer_device_info_node_t
	s.write_u32(0, 'CORE_LIST_TYPE', 0, SIGNALYZER_LIST_TYPE.SERIAL_NUMBER)

	print 'list devices by serial number:'
	device_list = s.get_device_list();
	print device_list

	# open device
	s.open(device_list[0])

	# depending on a mode of signalyzer two or more ports is available for use. 
	# H2 supports two ports, H4 supports 4 ports

	# connector A: port 1 and port 2
	# connector B: port 3 and port 4
	p1 = 1
	p2 = 2
	p3 = 3
	p4 = 4
	
	# activate 5V on Connector A (pin 2 and 26)
	# this is not necessary for JTAG operation, but aux power can be used to power external circuits
	s.write_u32(p1, 'AUX_VIO', 1, 1);

	# activate 5V on Connector B (pin 2 and 26)
	# this is not necessary for JTAG operation, but aux power can be used to power external circuits
	s.write_u32(p3, 'AUX_VIO', 1, 1);

	# see http://www.signalyzer.com/wiki/doku.php?id=signalyzer:hardware:h4-pinout
	# for pin assignment
	# 1 is output, 0 is input

	#set-up all 4 signalyzer ports
	
	# port 1: 7654 3210 ( connector A: pins 3 - 10)
	#         0000 1011 = 0x0B
	signalyzer_set_mode(s, p1, 0x0B)

	# port 2: 7654 3210 ( connector A: pins 11 - 18)
	#         0000 1111 = 0x0F
	signalyzer_set_mode(s, p2, 0x0F)

	# port 3: 7654 3210 ( connector C: pins 3 - 10)
	#         1111 1111 = 0xFF
	signalyzer_set_mode(s, p3, 0xFF)

	# port 4: 7654 3210 ( connector D: pins 11 - 18)
	#         0000 0000 = 0xFF
	signalyzer_set_mode(s, p4, 0x00)

	# set bus clock rate for each of the ports.
	signalyzer_set_clk_freq(s, p1, 1000000);
	signalyzer_set_clk_freq(s, p2, 2000000);
	signalyzer_set_clk_freq(s, p3, 3000000);
	signalyzer_set_clk_freq(s, p4, 4000000);
	
	# now everything is setup for bitbang
	
	# write
	# variable length arrays can be written out to any of the opened ports
	
	signalyzer_bitbang_write(s, p1, (0xAA, 0x00, 0xAA, 0x00, 0xAA, 0x00, 0xAA, 0x00, 0xAA, 0x00))
	signalyzer_bitbang_write(s, p2, (0x02, 0x03))
	signalyzer_bitbang_write(s, p3, (0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF))
	signalyzer_bitbang_write(s, p4, (0x03,))
	
	# write-read
	# write_read calls will return same number of bytes as number of bytes being written out
	
	print 'write_read for port 1'
	print signalyzer_bitbang_write_read(s, p1, (0xAA, 0x00, 0xAA, 0x00, 0xAA, 0x00, 0xAA, 0x00, 0xAA, 0x00))
	
	print 'write_read for port 2'
	print signalyzer_bitbang_write_read(s, p2, (0x02, 0x03))
	
	print 'write_read for port 3'
	print signalyzer_bitbang_write_read(s, p3, (0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF))
	
	print 'write_read for port 4'
	print signalyzer_bitbang_write_read(s, p4, (0x03,))
	
	# read only is not possible as for every byte written out, one byte is read back.
	# read would have to be done with write_read and supplying pin state to be output
	
	# for example, if state of the outputs must be 0x01 i.e. only lsb bit is at logic 1, and 10 pin samples are required a call would look like:
	# due to synchronous nature of spi and jtag interfaces this will be rarely used
	print signalyzer_bitbang_write_read(s, p1, (0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01))
	
# in case of error the error number and brief error description will be returned
except Exception, e:
    print 'Exception %s' % e

s.dispose()