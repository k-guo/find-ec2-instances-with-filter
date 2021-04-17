This script fetches all EC2 instances with a defined user define filter per https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#instance

It also include a function to collect information on all instances with no "Owner" tag.

The output of the results are written to a CSV file (default name of find_instances.csv).

### Pre-requisites Installation

1. Install packages:

pip3 install -r requirements.txt

2. Configure the AWS CLI:

aws configure

### Script Usage

Run python3 find-instances-with-tag-filter.py