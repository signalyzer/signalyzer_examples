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

# loads signalyzer TCL interface
# load libsignalyzer-tcl.so
load signalyzer-tcl.dll

# SIGNALYZER_HAL_INTERFACE_TYPE_LIBFTD2XX
set hal_type 0x01 

# SIGNALYZER_LIST_TYPE_DESCRIPTION
set list_type 0x02

# SIGNALYZER_DEVICE_TYPE_SIGNALYZER_H4
set device_type 0x02

# first create a signalyzer channel
if { [catch {set s0 [signalyzer new]} err] } {
    puts stderr "error creating signalyzer channel ($err)\n"
	exit 1
}
puts "channel $s0 was created"

# display current library version
if { [catch {set lib_version [signalyzer read_u32 $s0 0 "CORE_API_VERSION" 0]} err] } {
    puts stderr "error read_u32 ($err)\n"
	exit 1
}

puts "signalyzer library version is $lib_version"

# Set HAL for signalyzer library. Currently H2 and H4 devices support only LIBFTD2XX HAL (FTDI drivers)
if { [catch {signalyzer write_u32 $s0 0 "CORE_HAL_INTERFACE" 0 $hal_type} err] } {
    puts stderr "error write_u32 ($err)\n"
	exit 1
}

# specify what devices will be listed
if { [catch {signalyzer write_u32 $s0 0 "CORE_DEVICE_TYPE" 0 $device_type} err] } {
    puts stderr "error write_u32 ($err)\n"
	exit 1
}

# here a list of found serial numbers will be read

# SIGNALYZER_LIST_TYPE_SERIAL_NUMBER
set list_type 0x01

if { [catch {signalyzer write_u32 $s0 0 "CORE_LIST_TYPE" 0 $list_type} err] } {
    puts stderr "error write_u32 ($err)\n"
	exit 1
}

if { [catch {set dev_list [signalyzer list $s0]} err] } {
    puts stderr "error list ($err)\n"
	exit 1
}

if {[llength $dev_list] > 0} then { 
	puts stdout "Serial number based search found [llength $dev_list] device(s)\n"

	foreach r $dev_list \
	{
		puts "found: $r \n"
	}
}

# open device
if { [catch {signalyzer open $s0  [lindex $dev_list 0]} err] } {
    puts stderr "error open ($err)\n"
	exit 1
}


set port 1

# activate 5V on Connector A (pin 2 and 26)
# this is not really necessary for I2C operation, but aux power can be used to power external circuits
if { [catch {signalyzer write_u32 $s0 $port "AUX_VIO" 1 1} err] } {
    puts stderr "error setting AUX_VIO ($err)\n"
	exit 1
}	

# set operating mode to I2C
if { [catch {signalyzer write_u32 $s0 $port "PORT_OPERATING_MODE" 0 2} err] } {
    puts stderr "error setting operating mode ($err)\n"
	exit 1
}

# set bus clock rate to 100 kHz
if { [catch {signalyzer write_u32 $s0 $port "I2C_CLOCK_RATE" 0 100000} err] } {
    puts stderr "error setting I2C CLK freq ($err)\n"
	exit 1
}



#---------------------------------------------------------------------------------------------
# simple I2C write transaction (non-queued):
# start : control_word : address_byte : data_byte : stop

# generate start condition
if { [catch {signalyzer write_u32 $s0 $port "I2C_START_CONDITION" 0 1} err] } {
    puts stderr "error generating start condition ($err)\n"
	exit 1
}

# write control word
if { [catch {signalyzer write_u8 $s0 $port "I2C_DATA" 0 0xA0} err] } {
    puts stderr "error writing control word ($err)\n"
	exit 1
}

# write address
if { [catch {signalyzer write_u8 $s0 $port "I2C_DATA" 0 0x00} err] } {
    puts stderr "error writing address ($err)\n"
	exit 1
}


# write value
if { [catch {signalyzer write_u8 $s0 $port "I2C_DATA" 0 0x55} err] } {
    puts stderr "error writing data ($err)\n"
	exit 1
}

# generate stop condition
if { [catch {signalyzer write_u32 $s0 $port "I2C_STOP_CONDITION" 0 1} err] } {
    puts stderr "error generating stop condition ($err)\n"
	exit 1
}

after 50 {}

#---------------------------------------------------------------------------------------------
# read operations, non-queued transfer first with single byte read

# generate start condition
if { [catch {signalyzer write_u32 $s0 $port "I2C_START_CONDITION" 0 1} err] } {
    puts stderr "error generating start condition ($err)\n"
	exit 1
}

# write control word
if { [catch {signalyzer write_u8 $s0 $port "I2C_DATA" 0 0xA0} err] } {
    puts stderr "error writing control word ($err)\n"
	exit 1
}

# write address
if { [catch {signalyzer write_u8 $s0 $port "I2C_DATA" 0 0x00} err] } {
    puts stderr "error writing address ($err)\n"
	exit 1
}

# generate repeated start condition
if { [catch {signalyzer write_u32 $s0 $port "I2C_START_CONDITION" 0 1} err] } {
    puts stderr "error generating start condition ($err)\n"
	exit 1
}

# write control word
if { [catch {signalyzer write_u8 $s0 $port "I2C_DATA" 0 0xA1} err] } {
    puts stderr "error writing control word ($err)\n"
	exit 1
}

# read value
if { [catch {set read_value [signalyzer read_u8 $s0 $port "I2C_DATA" 0] } err] } {
    puts stderr "error writing data ($err)\n"
	exit 1
}
puts "read value = $read_value"

# generate stop condition
if { [catch {signalyzer write_u32 $s0 $port "I2C_STOP_CONDITION" 0 1} err] } {
    puts stderr "error generating stop condition ($err)\n"
	exit 1
}


# close device
if { [catch {signalyzer close $s0} err] } {
    puts stderr "error close ($err)\n"
	exit 1
}



# and dispose the channel
# signalyzer dispose $s0

puts "done"

