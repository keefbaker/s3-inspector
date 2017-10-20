import re
import sys
import boto3
import botocore
import requests
import termcolor

from collections import defaultdict

ignored_buckets = []

def grantchecker(grant, grants, explained, groups_to_check):
    permissions = grants[grant]
    perm_to_print = [explained[perm]
                     for perm in permissions]
    termcolor.cprint('Permission: {} by {}'.format(
        termcolor.colored(
            ' & '.join(perm_to_print), 'red'),
        termcolor.colored(groups_to_check[grant], 'red')))

def bucketcheck(bucket, bucketcount,
                s3_client, explained):
    groups_to_check = {
        'http://acs.amazonaws.com/groups/global/AllUsers': 'Everyone',
        'http://acs.amazonaws.com/groups/global/AuthenticatedUsers': 'Authenticated AWS users'
    }
    seperator = '-' * 40
    location = get_location(bucket.name, s3_client)

    acl = bucket.Acl()
    public, grants = check_acl(acl, groups_to_check)

    if public:
        print(seperator)
        bucket_line = termcolor.colored(
            bucket.name, 'blue', attrs=['bold'])
        public_ind = termcolor.colored(
            'PUBLIC!', 'red', attrs=['bold'])
        termcolor.cprint('Bucket {}: {}'.format(
            bucket_line, public_ind))
        print('Location: {}'.format(location))
        if grants:
            for grant in grants:
                grantchecker(grant, grants, explained, groups_to_check)
        urls = scan_bucket_urls(bucket.name)
        print('URLs:')
        if urls:
            print('\n'.join(urls))
        else:
            print('Nothing found')
    else:
        # bucket_line = termcolor.colored(
        #     bucket.name, 'blue', attrs=['bold'])
        # public_ind = termcolor.colored(
        #     'Not public', 'green', attrs=['bold'])
        # termcolor.cprint('Bucket {}: {}'.format(
        #     bucket_line, public_ind))
        # print('Location: {}'.format(location))
        pass
    bucketcount += 1
    return bucketcount


def bucketlist():
    s3 = boto3.resource('s3')
    return s3.buckets.all(), boto3.client('s3')

def check_acl(acl, groups_to_check):
    dangerous_grants = defaultdict(list)
    for grant in acl.grants:
        grantee = grant['Grantee']
        if grantee['Type'] == 'Group' and grantee['URI'] in groups_to_check:
            dangerous_grants[grantee['URI']].append(grant['Permission'])
    public_indicator = True if dangerous_grants else False
    return public_indicator, dangerous_grants


def get_location(bucket_name, s3_client):
    loc = s3_client.get_bucket_location(
        Bucket=bucket_name)['LocationConstraint']
    if loc is None:
        loc = 'None(probably North Virginia)'
    return loc

def scan_bucket_urls(bucket_name):
    domain = 's3.amazonaws.com'
    access_urls = []
    urls_to_scan = [
        'https://{}.{}'.format(bucket_name, domain),
        'http://{}.{}'.format(bucket_name, domain),
        'https://{}/{}'.format(domain, bucket_name),
        'http://{}/{}'.format(domain, bucket_name)
    ]
    for url in urls_to_scan:
        content = requests.get(url).text
        if not re.search('Access Denied', content):
            access_urls.append(url)
    return access_urls

def bucketloop():
    explained = {
        'READ': 'readable',
        'WRITE': 'writable',
        'READ_ACP': 'permissions readable',
        'WRITE_ACP': 'permissions writeable',
        'FULL_CONTROL': 'Full Control'
    }

    bucketcount = 0
    buckets, s3_client = bucketlist()
    for bucket in buckets:
        if bucket.name not in ignored_buckets:
            bucketcount = bucketcheck(bucket, bucketcount,
                                      s3_client, explained)
    if not bucketcount:
        print('No buckets found')
        termcolor.cprint(termcolor.colored('You are safe', 'green'))

if __name__ == '__main__':
    try:
        bucketloop()
    except botocore.exceptions.ClientError as error:
        print(str(error))
