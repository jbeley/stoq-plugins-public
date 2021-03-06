#   Copyright 2014-2015 PUNCH Cyber Analytics Group
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Overview
========

Sends and retrieves content from Amazon S3 buckets

"""

import boto3

from stoq.scan import get_sha1
from stoq.plugins import StoqConnectorPlugin


class S3Connector(StoqConnectorPlugin):

    def __init__(self):
        super().__init__()

    def activate(self, stoq):
        self.stoq = stoq

        super().activate()

        self.bucket = None

    def get_file(self, **kwargs):
        """
        Retrieve a file from an S3 bucket

        :param **kwargs s3bucket: Bucket name to be used
        :param **kwargs sha1: SHA1 hash to be used as a filename
        :param **kwargs filename: Filename of file to retrieve
        :param **kwargs index: Bucket to save content to

        :returns: Content of file retrieved
        :rtype: bytes or None

        """

        s3bucket = kwargs.get('index', self.bucket_name)
        self.connect(bucket_name=s3bucket)

        valid_keys = ['filename', 'sha1']
        for key in valid_keys:
            if key in kwargs:
                return self.bucket.get_key(kwargs[key])
        return None

    def save(self, payload, archive=False, **kwargs):
        """
        Save results to S3

        :param bytes payload: Content to be stored in Amazon S3 container
        :param **kwargs s3bucket: Bucket name to be used
        :param **kwargs sha1: SHA1 hash to be used as a filename

        :returns: Filename used to save the payload
        :rtype: bytes

        """

        s3bucket = kwargs.get('index', self.bucket_name)
        self.connect(bucket_name=s3bucket)

        filename = kwargs.get('sha1', get_sha1(payload))

        key = boto3.s3.key.Key(self.bucket, filename)

        try:
            key.set_contents_from_string(payload)
        except Exception as err:
            self.log.error("Unable to save file to S3: {}".format(str(err)))
            return None

        return filename

    def connect(self, bucket_name=None):
        # If we have a valid bucket, and the name matches the one
        # we want to use, let's just return
        if self.bucket and bucket_name == self.bucket.name:
            return

        # Looks like we need to connect to the bucket
        conn = boto3.connect_s3(self.access_key, self.secret_key)
        self.bucket = conn.create_bucket(bucket_name)
