using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Signalyzer;

namespace list_devices
{
    class Program
    {
        static void Main(string[] args)
        {
	        SIGNALYZER_STATUS status = SIGNALYZER_STATUS.OK;	
	        UInt32 library_version = 0x0;
	        UInt32 number_of_devices = 0;
	        string[] device_list = new string[1];
            DeviceInfoNode[] device_info_node = new DeviceInfoNode[1];
            UInt32 port = 1;
            byte read_value = 0;

            SignalyzerDevice signalyzer = new SignalyzerDevice();

	        if (status == SIGNALYZER_STATUS.OK)
		        status = signalyzer.ReadU32(0, SIGNALYZER_ATTRIBUTE.CORE_API_VERSION, 0,  out library_version);

	        if (status == SIGNALYZER_STATUS.OK)
		        Console.WriteLine("library version: 0x" + library_version.ToString("X"));
	        else
		        Console.WriteLine("error reading version information");

	        // Set HAL for signalyzer library. Currently H2 and H4 devices support only LIBFTD2XX HAL (FTDI drivers)
	        if (status == SIGNALYZER_STATUS.OK)
		        status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE.CORE_HAL_INTERFACE, 0, (UInt32)SIGNALYZER_HAL_INTERFACE_TYPE.LIBFTD2XX);

	        // specify what devices will be listed
	        if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE.CORE_DEVICE_TYPE, 0, (UInt32)SIGNALYZER_DEVICE_TYPE.H4);

	        // specify format of the list library will return. 
	        // The API can return either an array of serial numbers, array of device descriptions, or an array of structures signalyzer_device_info_node_t

	        // here a list of found serial numbers will be read
	        if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE.CORE_LIST_TYPE, 0, (UInt32)SIGNALYZER_LIST_TYPE.SERIAL_NUMBER);

	        if (status == SIGNALYZER_STATUS.OK)
		        status = signalyzer.GetDeviceList(out device_list, out number_of_devices);

	        if (status == SIGNALYZER_STATUS.OK)
	        {
		        Console.WriteLine("Serial number based search found " + number_of_devices.ToString() + " device(s)");

		        if (number_of_devices > 0)
		        {
			        foreach(string s in device_list)
				        Console.WriteLine("found: " + s);
		        }
	        }

            if (number_of_devices > 0)
            {
                if (status == SIGNALYZER_STATUS.OK)
                    status = signalyzer.Open(device_list[0]);
            }

            // activate 5V on Connector A (pin 2 and 26)
            // this is not really necessary for I2C operation, but aux power can be used to power external circuits
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(port, SIGNALYZER_ATTRIBUTE.AUX_VIO, 1, 1);

            // set operating mode to I2C
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(port, SIGNALYZER_ATTRIBUTE.PORT_OPERATING_MODE, 0, 2);

            // set bus clock rate to 100 kHz
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(port, SIGNALYZER_ATTRIBUTE.I2C_CLOCK_RATE, 0, 100000);

            //---------------------------------------------------------------------------------------------
            // simple I2C write transaction (non-queued):
            // start : control_word : address_byte : data_byte : stop

            // generate start condition
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(port, SIGNALYZER_ATTRIBUTE.I2C_START_CONDITION, 0, 1);

            // write control word
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU8(port, SIGNALYZER_ATTRIBUTE.I2C_DATA, 0, 0xA0);

            // write address
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU8(port, SIGNALYZER_ATTRIBUTE.I2C_DATA, 0, 0x00);

            // write value
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU8(port, SIGNALYZER_ATTRIBUTE.I2C_DATA, 0, 0x55);

            // generate stop condition
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(port, SIGNALYZER_ATTRIBUTE.I2C_STOP_CONDITION, 0, 1);


            //---------------------------------------------------------------------------------------------
            // read operations, non-queued transfer first with single byte read

            // generate start condition
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(port, SIGNALYZER_ATTRIBUTE.I2C_START_CONDITION, 0, 1);

            // write control word
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU8(port, SIGNALYZER_ATTRIBUTE.I2C_DATA, 0, 0xA0);

            // write address
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU8(port, SIGNALYZER_ATTRIBUTE.I2C_DATA, 0, 0x00);

            // generate repeated start condition
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(port, SIGNALYZER_ATTRIBUTE.I2C_START_CONDITION, 0, 1);

            // write control word
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU8(port, SIGNALYZER_ATTRIBUTE.I2C_DATA, 0, 0xA1);

            // read value
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.ReadU8(port, SIGNALYZER_ATTRIBUTE.I2C_DATA, 0, out read_value);

            Console.WriteLine("read_value = 0x" + read_value.ToString("X"));

            // generate stop condition
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(port, SIGNALYZER_ATTRIBUTE.I2C_STOP_CONDITION, 0, 1);


            //---------------------------------------------------------------------------------------------
            // close the previously opened connection
            if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.Close();

	        // note: in case of error, the error description can't be retrieved because signalyzer connection was never opened in this example and
	        // none of the ports were initialized
            if (status != SIGNALYZER_STATUS.OK)
                Console.WriteLine("The following error occurred 0x" + status.ToString("X"));

            signalyzer.Dispose();

	        Console.WriteLine("Press any key");
    	    Console.ReadKey();

        }
    }
}
