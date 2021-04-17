import datetime
import sys
import os
import csv
import logging
import boto3
from botocore.exceptions import ClientError

use_profile = False

regions = ['ap-southeast-1', 'ap-southeast-2', 'eu-central-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

# The following 3 lines can be used to find all available AWS regions to setup the variable 'regions'
#region_client = boto3.client('ec2')
#regions = [region['RegionName'] for region in region_client.describe_regions()['Regions']]
#regions = ['af-south-1', 'eu-north-1', 'ap-south-1', 'eu-west-3', 'eu-west-2', 'eu-south-1', 'eu-west-1', 'ap-northeast-3', 'ap-northeast-2', 'me-south-1', 'ap-northeast-1', 'sa-east-1', 'ca-central-1', 'ap-east-1', 'ap-southeast-1', 'ap-southeast-2', 'eu-central-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

# Set up global variables, the include_filter is used with the function get_region_instances_include_filter
# The exluce filter is used with get_region_instances_no_owner_tag
include_filter = [{
	'Name': 'tag:Owner',
	'Values': ['kguo',]
    },
#	{
#	'Name': 'instance-state-name',
#	'Values': ['running',]
#	}
	]

exclude_filter = ['Owner', 'owner']

filename = "find_instances.csv"
csv_custom_column1 = "Notes"

# Construct csv headers and return
def make_csv_header():
    csv_headers = [
            'Instance ID',
            'Instance Name',
            'Instance Type',
            'Region',
            'Notes'
        ]
    return csv_headers

# function to write to csv
def write_to_csv(instance, instance_notes, region_name, csvwriter):
	csvwriter.writerow([
    	instance.id,
    	instance_notes['instance_name'],
    	instance.instance_type,
    	region_name,
    	instance_notes[csv_custom_column1]
    ])

# Get instance name from the instance object if tag exist and
# collect Owner tag info
def get_aws_instance_info(instance):
	if not instance.tags:
		instance_name = ''
		column1_val = 'No tags exist'
	else:
		if exclude_filter not in [t['Key'] for t in instance.tags]:
			column1_val = "No Owner tag"

		for tag in instance.tags:
			if tag['Key'] == 'Name':
				instance_name = tag['Value']
				continue
			if tag['Key'] == ('Owner' or 'owner'):
				column1_val = 'Owner tag is '+ tag['Value']
				continue

	instance_notes = {'instance_name': instance_name, csv_custom_column1 : column1_val} 
	
	return instance_notes

# Function to find all instances with no owner tag
def get_region_instances_no_owner_tag(region):
	# Create boto3 session
	if use_profile:
		session = boto3.session.Session(region_name=region, profile_name=profile)
	else:
		session = boto3.session.Session(region_name=region)

	try:
		ec2 = session.resource('ec2')
		instances = ec2.instances.all()

		instances_result = []

		for instance in instances:
			# instances with no tags are added to the output list
			if not instance.tags:
				instances_result.append(instance)
			else:
				# if "Owner" or "owner" (exclude filter) is not in any of the tags' Keys
				# then add the instance to the output list
				if all((owner not in [t['Key'] for t in instance.tags]) for owner in exclude_filter):
					# print(instance.tags)
					instances_result.append(instance)

	except ClientError as e:
					print(e)
	return instances_result

# Function to find all instances with the provided filter
def get_region_instances_include_filter(region):
	# Create boto3 session
	if use_profile:
		session = boto3.session.Session(region_name=region, profile_name=profile)
	else:
		session = boto3.session.Session(region_name=region)

	try:
		ec2 = session.resource('ec2')
		instances_result = ec2.instances.filter(Filters=include_filter)

	except ClientError as e:
					print(e)
	return instances_result

# Write the results to a CSV file
with open(filename, 'w') as csvfile:
    # initialize csv writer
    csvwriter = csv.writer(
        csvfile,
        delimiter=',',
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL)

    csv_headers = make_csv_header()
    csvwriter.writerow(csv_headers)

    for region in regions:
    	# Call the function which finds instances with the defined Filters
    	# Or call get_region_instances_no_owner_tag(region) to 
    	# find instances with no Owner tag
    	instances = get_region_instances_include_filter(region)
    	for instance in instances:
    		print(instance.id)
    		instance_notes_dict = get_aws_instance_info(instance)
    		write_to_csv(instance, instance_notes_dict, region, csvwriter)
