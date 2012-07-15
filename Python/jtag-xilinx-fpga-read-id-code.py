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

# jtag mode attributes
# JTAG_DATA (variable size) - data to be shifted into or from jtag chain
# JTAG_CLOCK_RATE (uint32_t size) - TCK clock rate in Hz (min 100, max 30000000)
# JTAG_TAP_STATE (uint32_t size) - instructs state machine to advance to a particular state
# JTAG_TAP_END_STATE (uint32_t size) - state which state machine shall be left at after DR or IR scan with JTAG_DATA
# JTAG_CLOCK_TCK (uint32_t size) - clocks TCK specified number of clock cycles

# 
SIGNALYZER_JTAG_TAP_STATE = enum(
	DREXIT2 = 0x00,
	DREXIT1	= 0x01,
	DRSHIFT = 0x02,
	DRPAUSE = 0x03,
	IRSELECT = 0x04,
	DRUPDATE = 0x05,
	DRCAPTURE = 0x06,
	DRSELECT = 0x07,
	IREXIT2	= 0x08,
	IREXIT1	= 0x09,
	IRSHIFT	= 0x0A,
	IRPAUSE	= 0x0B,
	IDLE = 0x0C,
	IRUPDATE = 0x0D,
	IRCAPTURE = 0x0E,
	RESET = 0x0F,
	INVALID	= 0xFF)

SIGNALYZER_JTAG_TAP_SCAN = enum(DR = 0, IR = 1)

s = signalyzer.new()

try:
	# read signalyzer library version
	ver = s.read_u32(0, 'CORE_API_VERSION', 0)
	print 'signalyzer library version = 0x{0:08x}'.format(ver)

	# attribute supplied to the call can be string, as it shown above, or its numeric value
	ver = s.read_u32(0, 0xF01, 0)
	print 'signalyzer library version = 0x{0:08x}'.format(ver)

	# read python wrapper version information
	ver = s.version()
	print 'signalyzer library python wrapper version = 0x{0:08x}'.format(ver)
	
	# Set HAL for signalyzer library. Currently H2 and H4 devices support only LIBFTD2XX HAL
	s.write_u32(0, 'CORE_HAL_INTERFACE', 0, SIGNALYZER_HAL_INTERFACE_TYPE.LIBFTD2XX)

	# specify what devices will be listed
	
	s.write_u32(0, 'CORE_DEVICE_TYPE', 0, SIGNALYZER_DEVICE_TYPE.H2)

	# specify format of the list library will return. 
	# The API can return either an array of serial numbers, array of device descriptions, 
	# or an array of structures signalyzer_device_info_node_t
	s.write_u32(0, 'CORE_LIST_TYPE', 0, SIGNALYZER_LIST_TYPE.SERIAL_NUMBER)

	print 'list devices by serial number:'
	device_list = s.get_device_list();
	print device_list

	# open device
	s.open(device_list[1])

	# depending on a mode of signalyzer two or more ports is available for use. 
	# H2 supports two ports, H4 supports 4 ports (but only first two can be used for I2C, SPI or JTAG)

	#jtag interface will utilize port 1
	port = 1;

	# activate 5V on Connector A (pin 2 and 26)
	# this is not necessary for JTAG operation, but aux power can be used to power external circuits
	s.write_u32(port, 'AUX_VIO', 1, 1);

	# set operating mode to JTAG
	s.write_u32(port, 'PORT_OPERATING_MODE', 0,  SIGNALYZER_OPERATING_MODE.JTAG);

	# set bus clock rate to 1000 kHz
	s.write_u32(port, 'JTAG_CLOCK_RATE', 0, 1000000);

	# set where JTAG TAP state machine must get after executing any read/write.
	s.write_u32(port, 'JTAG_TAP_END_STATE', 0, SIGNALYZER_JTAG_TAP_STATE.DRSHIFT)
	
	# ---------------------------------------------------------------------------------------------
	# initialize FPGA JTAG state machine

	# steps controller into RESET state
	s.write_u32(port, 'JTAG_TAP_STATE', 0, SIGNALYZER_JTAG_TAP_STATE.RESET)

	# steps controller into IDLE state
	s.write_u32(port, 'JTAG_TAP_STATE', 0, SIGNALYZER_JTAG_TAP_STATE.IDLE)

	# TAP state machine is now in a known state

	# this is just example of JTAG_CLOCK_TCK command (not required for fpga id code read)
	# it issue 1000 tck clock cycles
	s.write_u32(port, 'JTAG_CLOCK_TCK', 0, 1000)

	# ---------------------------------------------------------------------------------------------
	# read ID code from xilinx fpga

	# clock bits into IRSHIFT register. The address field/parameter specifies if DRSHIFT or IRSHIFT should receive the bits.
	# Here 6 bits are being clocked into IRSHIFT register, and the data value being clocked into IRSHIFT is 0x09
	txd = (0x09,)
	s.write(port, 'JTAG_DATA', SIGNALYZER_JTAG_TAP_STATE .IRSHIFT, txd, 6)	

	# clock in 32 bits from DRSHIFT and store it in fpga_id_code. 
	# for JTAG write/read operation address parameter specifies if either DRSHIFT or IRSHIFT should be used, here we're reding from DRSHIFT
	fpga_id_code  = s.read(port, "JTAG_DATA", SIGNALYZER_JTAG_TAP_STATE.DRSHIFT, 32)
	
	# the library returns read data in the same byte order as data is read from TDO pin.
	print 'RAW received data = [ 0x%02X, 0x%02X, 0x%02X, 0x%02X ]' % fpga_id_code

	# since returned data is in the same byte order as it read from TDO pin, in some cases byte order must be reversed
	print 'FPGA ID_CODE = 0x%02X%02X%02X%02X' % (fpga_id_code[3], fpga_id_code[2], fpga_id_code[1], fpga_id_code[0])

# in case of error the error number and brief error description will be returned
except Exception, e:
    print 'Exception {0}'.format(e)

s.dispose()