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
 * This example shows various i2c transactions. The example is similar to i2c-read-write.c,
 * but it uses queue to improve transfer speed.
 */

int main(int argc, char *argv[])
{	
	signalyzer_status_t status = SIGNALYZER_STATUS_OK;
	signalyzer_handle_t signalyzer_handle = NULL;

	uint32_t library_version = 0x0;
	uint32_t number_of_devices = 0;
	char device_list[10][64];

	const char * error_description = NULL;
	
	signalyzer_port_t port = 1;
	uint32_t i;
	uint32_t operating_mode = 0;
	uint8_t data_buffer[5];

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
		status = signalyzer_write_u32(signalyzer_handle, 0, SIGNALYZER_ATTRIBUTE_CORE_DEVICE_TYPE, 0, SIGNALYZER_DEVICE_TYPE_SIGNALYZER_H4);

	// specify format of the list library will return.
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

	// if at least one device is present, open a connection with first attached device.
	if (number_of_devices)
	{
		if (status == SIGNALYZER_STATUS_OK)
			status = signalyzer_open(signalyzer_handle, device_list[0]);
	}
	else
	{
		// this is just to tell rest of the code below that no signalyzers were found
		status = SIGNALYZER_STATUS_OTHER_ERROR;
	}

	// activate 5V on Connector A (pin 2 and 26)
	// this is not really necessary for I2C operation, but aux power can be used to power external circuits
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_AUX_POWER_CONTROL, 0, 1);

	// set operating mode to I2C
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_PORT_OPERATING_MODE, 0,  SIGNALYZER_OPERATING_MODE_I2C);

	// read operating mode back, this operation is not required and added here just to show read transaction.
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_read_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_PORT_OPERATING_MODE, 0, &operating_mode);

	// set bus clock rate to 100 kHz
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_CLOCK_RATE, 0, 100000);

	printf ("press Enter to continue\r\n");
	getchar();

	//---------------------------------------------------------------------------------------------
	// simple I2C write transaction (non-queued):
	// start : control_word : address_byte : data_byte : stop

	// select queue with id = 1 for operation.
	// from this point everything will be stored in queue to be executed later
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_QUEUE_ACTIVE, 0, 1);

	// generate start condition
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_START_CONDITION, 0, 1);

	// write control word
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u8(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, 0xA0);

	// write address
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u8(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, 0x00);

	// write value
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u8(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, 0x55);

	// generate stop condition
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_STOP_CONDITION, 0, 1);

	// now we run the queue to perform the bus transaction
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_QUEUE_RUN, 0, 1);

	// queue id = 0 is for non-queued operation. switch back to non-queue mode if needed
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_QUEUE_ACTIVE, 0, 0);

	printf ("press Enter to continue\r\n");
	getchar();

	//---------------------------------------------------------------------------------------------
	// another write transaction, but utilizing a buffer write
	// start : control_word : address_byte : data_byte : stop

	// select queue with id = 1 for operation.
	// from this point everything will be stored in queue to be executed later
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_QUEUE_ACTIVE, 0, 1);

	// generate start condition
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_START_CONDITION, 0, 1);

	data_buffer[0] = 0xA0;
	data_buffer[1] = 0x00;
	data_buffer[2] = 0x55;

	// write data bytes
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, data_buffer, (3 * 8));

	// generate stop condition
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_STOP_CONDITION, 0, 1);

	// now we run the queue to perform the bus transaction
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_QUEUE_RUN, 0, 1);

	printf ("press Enter to continue\r\n");
	getchar();

	//---------------------------------------------------------------------------------------------
	// read operations, non-queued transfer first with single byte read

	// select queue with id = 1 for operation.
	// from this point everything will be stored in queue to be executed later
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_QUEUE_ACTIVE, 0, 1);

	// generate start condition
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_START_CONDITION, 0, 1);

	// write control word
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u8(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, 0xA0);

	// write address
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u8(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, 0x00);

	// generate repeated start condition
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_START_CONDITION, 0, 1);

	// write control word
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u8(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, 0xA1);

	// read value
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_read_u8(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, &data_buffer[0]);

	// generate stop condition
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_STOP_CONDITION, 0, 1);

	// now we run the queue to perform the bus transaction
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_QUEUE_RUN, 0, 1);

	printf ("press Enter to continue\r\n");
	getchar();

	//---------------------------------------------------------------------------------------------
	// read three consecutive bytes

	// select queue with id = 1 for operation.
	// from this point everything will be stored in queue to be executed later
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_QUEUE_ACTIVE, 0, 1);

	// generate start condition
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_START_CONDITION, 0, 1);

	// write control word
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u8(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, 0xA0);

	// write address
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u8(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, 0x00);

	// generate repeated start condition
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_START_CONDITION, 0, 1);

	// write control word
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u8(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, 0xA1);

	// read value
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_read(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_DATA, 0, data_buffer, (3 * 8));

	// generate stop condition
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_I2C_STOP_CONDITION, 0, 1);

	// now we run the queue to perform the bus transaction
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_write_u32(signalyzer_handle, port, SIGNALYZER_ATTRIBUTE_QUEUE_RUN, 0, 1);

	printf ("press Enter to continue\r\n");
	getchar();

	//---------------------------------------------------------------------------------------------
	// close the previously opened connection
	if (status == SIGNALYZER_STATUS_OK)
		status = signalyzer_close(signalyzer_handle);

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
