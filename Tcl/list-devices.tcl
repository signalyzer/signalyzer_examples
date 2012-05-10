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
if { [catch {set lib_version [signalyzer read32 $s0 0 "CORE_API_VERSION" 0]} err] } {
    puts stderr "error read32 ($err)\n"
	exit 1
}

puts "signalyzer library version is $lib_version"

# Set HAL for signalyzer library. Currently H2 and H4 devices support only LIBFTD2XX HAL (FTDI drivers)
if { [catch {signalyzer write32 $s0 0 "CORE_HAL_INTERFACE" 0 $hal_type} err] } {
    puts stderr "error write32 ($err)\n"
	exit 1
}

# specify what devices will be listed
if { [catch {signalyzer write32 $s0 0 "CORE_DEVICE_TYPE" 0 $device_type} err] } {
    puts stderr "error write32 ($err)\n"
	exit 1
}

# specify format of the list library will return. 
# The API can return either an array of serial numbers, array of device descriptions, or an array of structures signalyzer_device_info_node_t
if { [catch {signalyzer write32 $s0 0 "CORE_LIST_TYPE" 0 $list_type} err] } {
    puts stderr "error write32 ($err)\n"
	exit 1
}

# retrieve device list containing device description of each found device
if { [catch {set dev_list [signalyzer list $s0]} err] } {
    puts stderr "error write32 ($err)\n"
	exit 1
}

if {[llength $dev_list] > 0} then { 
	puts stdout "Description based search found [llength $dev_list] device(s)\n"

	foreach r $dev_list \
	{
		puts "found: $r \n"
	}
}


# next example will show how to retrieve device list containing an array of signalyzer_device_info_node_t structures

# SIGNALYZER_LIST_TYPE_INFO_NODE
set list_type 0x03

if { [catch {signalyzer write32 $s0 0 "CORE_LIST_TYPE" 0 $list_type} err] } {
    puts stderr "error write32 ($err)\n"
	exit 1
}


if { [catch {set dev_list [signalyzer list $s0]} err] } {
    puts stderr "error write32 ($err)\n"
	exit 1
}

if {[llength $dev_list] > 0} then { 
	puts stdout "signalyzer_device_info_node_t based search found [llength $dev_list] device(s)\n"

	foreach r $dev_list \
	{
		puts "found: $r \n"
	}
}

# here a list of found serial numbers will be read

# SIGNALYZER_LIST_TYPE_SERIAL_NUMBER
set list_type 0x01

if { [catch {signalyzer write32 $s0 0 "CORE_LIST_TYPE" 0 $list_type} err] } {
    puts stderr "error write32 ($err)\n"
	exit 1
}

if { [catch {set dev_list [signalyzer list $s0]} err] } {
    puts stderr "error write32 ($err)\n"
	exit 1
}

if {[llength $dev_list] > 0} then { 
	puts stdout "Serial number based search found [llength $dev_list] device(s)\n"

	foreach r $dev_list \
	{
		puts "found: $r \n"
	}
}

# and dispose the channel
signalyzer dispose $s0

puts "done"

