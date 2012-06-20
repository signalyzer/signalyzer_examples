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
                status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE.CORE_DEVICE_TYPE, 0, (UInt32)SIGNALYZER_DEVICE_TYPE.SIGNALYZER_H4);

	        // specify format of the list library will return. 
	        // The API can return either an array of serial numbers, array of device descriptions, or an array of structures signalyzer_device_info_node_t
	        if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE.CORE_LIST_TYPE, 0, (UInt32)SIGNALYZER_LIST_TYPE.DESCRIPTION);

	        // retrieve device list containing device description of each found device
	        if (status == SIGNALYZER_STATUS.OK)
		        status = signalyzer.GetDeviceList(out device_list, out number_of_devices);

	        if (status == SIGNALYZER_STATUS.OK)
	        {
		        Console.WriteLine("Description based search found " + number_of_devices.ToString() + " device(s)");

		        if (number_of_devices > 0)
		        {
                    foreach(string s in device_list)                   
				    Console.WriteLine("found: " + s);
		        }
	        }

	        // next example will show how to retrieve device list containing an array of signalyzer_device_info_node_t structures
	        if (status == SIGNALYZER_STATUS.OK)
                status = signalyzer.WriteU32(0, SIGNALYZER_ATTRIBUTE.CORE_LIST_TYPE, 0, (UInt32)SIGNALYZER_LIST_TYPE.INFO_NODE);

	        if (status == SIGNALYZER_STATUS.OK)
		        status = signalyzer.GetDeviceList(out device_info_node, out number_of_devices);

	        if (status == SIGNALYZER_STATUS.OK)
	        {
		        Console.WriteLine("signalyzer_device_info_node_t based search found " + number_of_devices.ToString() + " device(s)");

		        if (number_of_devices > 0)
		        {
                    foreach(DeviceInfoNode s in device_info_node)
				        Console.WriteLine("found: " + s.SerialNumber + " " + s.Description + " " + s.Type.ToString());
		        }
	        }

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
