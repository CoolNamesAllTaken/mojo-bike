import time
import sys
import iothub_client
import os
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult, IoTHubError

CONNECTION_STRING = "HostName=MojoHub.azure-devices.net;DeviceId=Pi1;SharedAccessKey=hVqjaFV5ltQ40s5sbXCaBoTnzD+WnTj4KjiBSH8xCqQ="
PROTOCOL = IoTHubTransportProvider.HTTP

PATHTOFILE = "text.txt"
FILENAME = "most-recent-data.csv"

def blob_upload_conf_callback(result, user_context):
    if str(result) == 'OK':
        print ( "...file uploaded successfully." )
    else:
        print ( "...file upload callback returned: " + str(result) )


def iothub_file_upload_sample_run():
    print ( "IoT Hub file upload sample, press Ctrl-C to exit" )

    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)

    f = open(PATHTOFILE, "r")
    content = f.read()

    client.upload_blob_async(FILENAME, content, len(content), blob_upload_conf_callback, 0)

    print ( "" )
    print ( "File upload initiated..." )


iothub_file_upload_sample_run()

