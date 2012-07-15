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

#ifdef _WINDOWS
#include <windows.h>
#endif

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <conio.h>

#include "signalyzer.h"

/*
 * This simple example shows how to list attached signalyzer devices.
 *
 */

int main(int argc, char *argv[])
{	
	signalyzer_status_t status = SIGNALYZER_STATUS_OK;
	signalyzer_handle_t signalyzer_handle = NULL;

	uint32_t library_version = 0x0;
	uint32_t number_of_devices = 0;
	char device_list[10][64];
	struct signalyzer_device_info_node_t device_info_node[10];
	const char * error_description = NULL;
	uint32_t i;

	// create signalyzer context
	status = signalyzer_new(&signalyzer_handle);

	if ((signalyzer_handle == NULL) || (status != SIGNALYZER_STATUS_OK))
	{
		printf("error creating signalyzer context, exiting\r\n");
		return -1;
	}

	// Read library version
	// Note: all SIGNALYZER_CORE_* attributes do not require connection to be open prior operation
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_read_u32(signalyzer_handle, 0, SIGNALYZER_ATTRIBUTE_CORE_API_VERSION, 0, &library_version);

	if (status == SIGNALYZER_STATUS_OK)
		printf("signalyzer library version: 0x%.8X\r\n", library_version);

	// Set HAL for signalyzer library. Currently H2 and H4 devices support only LIBFTD2XX HAL (FTDI drivers)
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, 0, SIGNALYZER_ATTRIBUTE_CORE_HAL_INTERFACE, 0, SIGNALYZER_HAL_INTERFACE_TYPE_LIBFTD2XX);

	// specify what devices will be listed
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, 0, SIGNALYZER_ATTRIBUTE_CORE_DEVICE_TYPE, 0, SIGNALYZER_DEVICE_TYPE_H4);

	// specify format of the list library will return. 
	// The API can return either an array of serial numbers, array of device descriptions, or an array of structures signalyzer_device_info_node_t
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, 0, SIGNALYZER_ATTRIBUTE_CORE_LIST_TYPE, 0, SIGNALYZER_LIST_TYPE_DESCRIPTION);

	// retrieve device list containing device description of each found device
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_get_device_list(signalyzer_handle, device_list, &number_of_devices);

	if (status == SIGNALYZER_STATUS_OK)
	{
		printf("Description based search found %d device(s)\r\n", number_of_devices);

		if (number_of_devices)
		{
			for (i = 0; i < number_of_devices; i++)
				printf("found: %s\r\n", device_list[i]);
		}
	}

	// next example will show how to retrieve device list containing an array of signalyzer_device_info_node_t structures
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, 0, SIGNALYZER_ATTRIBUTE_CORE_LIST_TYPE, 0, SIGNALYZER_LIST_TYPE_INFO_NODE);

	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_get_device_list(signalyzer_handle, device_info_node, &number_of_devices);

	if (status == SIGNALYZER_STATUS_OK)
	{
		printf("signalyzer_device_info_node_t based search found %d device(s)\r\n", number_of_devices);

		if (number_of_devices)
		{
			for (i = 0; i < number_of_devices; i++)
				printf("found: %s, %s, %d\r\n", device_info_node[i].serial_number, device_info_node[i].description, device_info_node[i].device_type);
		}
	}


	// here a list of found serial numbers will be read
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, 0, SIGNALYZER_ATTRIBUTE_CORE_LIST_TYPE, 0, SIGNALYZER_LIST_TYPE_SERIAL_NUMBER);

	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_get_device_list(signalyzer_handle, device_list, &number_of_devices);

	if (status == SIGNALYZER_STATUS_OK)
	{
		printf("Serial number based search found %d device(s)\r\n", number_of_devices);

		if (number_of_devices)
		{
			for (i = 0; i < number_of_devices; i++)
				printf("found: %s\r\n", device_list[i]);
		}
	}

	// in case of error, retrieve an error description and display it
	if (status != SIGNALYZER_STATUS_OK)
	{
		signalyzer_read(signalyzer_handle, 0, SIGNALYZER_ATTRIBUTE_PORT_ERROR_DESCRIPTION, 0, (void *)&error_description, 0);
		printf("The following error occurred: 0x%08X (%s)\r\n", status, error_description);
	}

	// dispose signalyzer context and release memory
	status = signalyzer_dispose(signalyzer_handle);

	printf ("press Enter to exit\r\n");
	getchar();
	
	return 0;
}
