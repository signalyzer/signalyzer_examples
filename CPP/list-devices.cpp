/*
 * Copyright (C) 2012 by Xverve Technologies Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sub license, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include "signalyzer.h"
#include "signalyzer-cpp.h"

#include <iostream>

using namespace std;

int main(int argc, char* argv[])
{
	signalyzer_status_t status = SIGNALYZER_STATUS_OK;
	
	uint32_t library_version = 0x0;
	uint32_t number_of_devices = 0;
	char device_list[10][64];
	struct signalyzer_device_info_node_t device_info_node[10];
	uint32_t i;

	Signalyzer signalyzer;

	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer.ReadU32(0, SIGNALYZER_ATTRIBUTE_CORE_API_VERSION, 0, &library_version);

	if (status == SIGNALYZER_STATUS_OK)
		cout << "library version: 0x" << hex << library_version << endl;
	else
		cout << "error reading version information" << endl;

	// Set HAL for signalyzer library. Currently H2 and H4 devices support only LIBFTD2XX HAL (FTDI drivers)
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE_CORE_HAL_INTERFACE, 0, SIGNALYZER_HAL_INTERFACE_TYPE_LIBFTD2XX);

	// specify what devices will be listed
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE_CORE_DEVICE_TYPE, 0, SIGNALYZER_DEVICE_TYPE_H4);

	// specify format of the list library will return. 
	// The API can return either an array of serial numbers, array of device descriptions, or an array of structures signalyzer_device_info_node_t
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE_CORE_LIST_TYPE, 0, SIGNALYZER_LIST_TYPE_DESCRIPTION);

	// retrieve device list containing device description of each found device
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer.GetDeviceList(device_list, &number_of_devices);

	if (status == SIGNALYZER_STATUS_OK)
	{
		cout << "Description based search found " << dec << number_of_devices << " device(s)" << endl;

		if (number_of_devices)
		{
			for (i = 0; i < number_of_devices; i++)
				cout << "found: " << device_list[i] << endl;
		}
	}

	// next example will show how to retrieve device list containing an array of signalyzer_device_info_node_t structures
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE_CORE_LIST_TYPE, 0, SIGNALYZER_LIST_TYPE_INFO_NODE);

	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer.GetDeviceList(device_info_node, &number_of_devices);

	if (status == SIGNALYZER_STATUS_OK)
	{
		cout << "signalyzer_device_info_node_t based search found " << dec << number_of_devices << " device(s)" << endl;

		if (number_of_devices)
		{
			for (i = 0; i < number_of_devices; i++)
				cout << "found: " << device_info_node[i].serial_number << " " << device_info_node[i].description << " " << dec << device_info_node[i].device_type << endl;
		}
	}

	// here a list of found serial numbers will be read
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE_CORE_LIST_TYPE, 0, SIGNALYZER_LIST_TYPE_SERIAL_NUMBER);

	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer.GetDeviceList(device_list, &number_of_devices);

	if (status == SIGNALYZER_STATUS_OK)
	{
		cout << "Serial number based search found " << dec << number_of_devices <<  " device(s)" << endl;

		if (number_of_devices)
		{
			for (i = 0; i < number_of_devices; i++)
				cout << "found: " << device_list[i] << endl;
		}
	}

	// note: in case of error, the error description can't be retrieved because signalyzer connection was never opened in this example and
	// none of the ports were initialized
	if (status != SIGNALYZER_STATUS_OK)
		cout << "The following error occurred 0x" << hex << status;

	// dispose signalyzer context and release memory
	signalyzer.~Signalyzer();

	cout << "Press any key";
	cin.get();

	return 0;
}

