#!/usr/bin/env python3

# Importing authentication and GCP libraries as well as pprint for the JSON

import argparse
import os
import time
from pprint import pprint

import googleapiclient.discovery
from googleapiclient import discovery
from six.moves import input
from oauth2client.client import GoogleCredentials
import google.auth

# Load our credentials as we run on local machine
credentials, project = google.auth.default()
service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)
# Using our specfied availability zone and naming our disk and bucket
zone = 'us-west1-b'
project = 'total-vertex-291803'
disk = 'demo-instance'
bucket = 'lab-5-vm-snapshot'

snapshot_req = {

    'name': 'base-snapshot-demoinstance'

}

def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation['name']).execute()
        print(result)

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)

def create_instance(compute,project,zone,name,bucket,snapshotname):
    getsourceSnapshot = compute.snapshots().get(project = project , snapshot = snapshotname).execute()
    source_snapshot = getsourceSnapshot['selfLink']

    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()
    image_url = "http://storage.googleapis.com/gce-demo-input/photo.jpg"
    image_caption = "Ready for dessert?"

    config = {
        'name': name,
        'machineType': machine_type,


        # Specify the boot disk and the image to use as a source.
        'disks': [
            {

                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    #'sourceImage': source_disk_image,
                    'sourceSnapshot': source_snapshot


                }
            }
        ],

        # Specify a network interface with NAT to access the internet(public)
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows us to pass deployment scripts to be run
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }, {
                'key': 'url',
                'value': image_url
            }, {
                'key': 'text',
                'value': image_caption
            }, {
                'key': 'bucket',
                'value': bucket
            }]
        }
    }





#
# Stub code - just lists all instances
#
# def list_instances(compute, project, zone):
#     result = compute.instances().list(project=project, zone=zone).execute()
#     return result['items'] if 'items' in result else None
#
# print("Your running instances are:")
# for instance in list_instances(service, project, 'us-west1-b'):
#     print(instance['name'])

    # We create the initial instance(send request) using the config above and return it's response
    our_instance_response = compute.instances().insert(project=project,zone=zone,body=config).execute()

    return our_instance_response

# we send our create snapshot request and store the response
request = service.disks().createSnapshot(project=project, zone=zone , disk=disk , body=snapshot_req)
response = request.execute()



times = []
instance1 = 'instance1'
instance2 = 'instance2'
instance3 = 'instance3'

# Base benchmark to start timing against
t0 = time.time()
run1 = create_instance(service, project, zone, instance1, bucket, snapshot_req['name'])

# Time the creation 3 different times, append them to our list and write the entries to our file
# We use wait_for_operation for timing purposes, taken from stub code
wait_for_operation(service, project, zone, run1)
t1 = time.time()
diff_1 = t1 - t0
times.append(diff_1)

t2 = time.time()
run2 = create_instance(service, project, zone,instance2, bucket, snapshot_req['name'])
wait_for_operation(service, project, zone, run2)
t3 = time.time()
diff_2 = t3 - t2
times.append(diff_2)

t4 = time.time()
run3 = create_instance(service, project, zone, instance3, bucket, snapshot_req['name'])
wait_for_operation(service, project, zone, run3)
t5 = time.time()
diff_3 = t5 - t4
times.append(diff_3)

print(times)

with open('TIMING.md','w') as f:
    for item in times:
        f.write("%s\n" % item)
