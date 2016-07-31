#!/usr/bin/python

import solrIndexer
import imageLoader
import alchemyClassifier
import fb_client
import imgcatDB

import boto
import boto.sqs
import time
import sys
import os
import json
from boto.s3.key import Key
import requests

import logging
import argparse

logging.Formatter.converter = time.gmtime
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger('imgcat')
logger.setLevel(logging.DEBUG)

logger.info("feedProcessor starting")

SOLR_HOST = 'ec2-54-187-86-241.us-west-2.compute.amazonaws.com:8983'
SOLR_CORE = 'imgcat'

SOLR_SQS_QUEUE = 'imgcat-solr'
ALCHEMY_SQS_QUEUE = 'imgcat-alchemy'
USER_SQS_QUEUE = 'imgcat-user'
LOADER_SQS_QUEUE = 'imgcat-loader'

AWS_REGION = 'us-west-2'

ALCHEMY_APIHOST = 'gateway-a.watsonplatform.net'
ALCHEMY_APIKEY = 'fc1b44987b12c84d802aa935098189c32abecda4'

WATSON_APIHOST = 'gateway.watsonplatform.net'
WATSON_USERNAME = "e9418f1e-c7e9-480b-b973-96620bc26281"
WATSON_APIKEY = "nqnIoyO50MwV"


def unitTests():
    bucket = 'imgcat-dev'
    
    #setup the bucket
    # AWS_ACCESS_KEY_ID and  AWS_SECRET_ACCESS_KEY should be in the environment or ~/.boto

    c = boto.connect_s3()
    b = c.get_bucket(bucket, validate=False)
    print 'got the bucket'


feed = os.getenv('IMGCAT_FEED', 'all')

if feed == 'solr':
    solrIndexer.monitorFeed(feed=SOLR_SQS_QUEUE, solr_host=SOLR_HOST,  solr_core=SOLR_CORE, aws_region=AWS_REGION)

elif feed == 'alchemy':
    alchemyClassifier.monitorFeed(feed=ALCHEMY_SQS_QUEUE,
                                  aws_region=AWS_REGION,
                                  apihost=ALCHEMY_APIHOST,
                                  apikey=ALCHEMY_APIKEY,
                                  solr_queue=SOLR_SQS_QUEUE)

elif feed == 'loader':
    imageLoader.monitorFeed(feed=LOADER_SQS_QUEUE,
                            aws_region=AWS_REGION,
                            apihost=WATSON_APIHOST,
                            apiuser=WATSON_USERNAME,
                            apikey=WATSON_APIKEY,
                            alchemy_queue=ALCHEMY_SQS_QUEUE,
                            solr_queue=SOLR_SQS_QUEUE)


elif feed == 'user':
    fb_client.monitorFeed(feed=USER_SQS_QUEUE, aws_region=AWS_REGION)
    
elif feed == 'all':

    conn = boto.sqs.connect_to_region("us-west-2")
    q = conn.create_queue('imgcat-q1')
    print ' connected to queue '
    
    while True:
        print ''
        try:
            rs = q.get_messages(1)
        except:
            print 'resetting connection'
            conn = boto.sqs.connect_to_region("us-west-2")
            q = conn.create_queue('imgcat-q1')
            rs = []
            pass
        
        num = len(rs)
        if (num > 0):
            message = rs[0]
            print "message: " , message.get_body()
            
            msgDict = json.loads(message.get_body())
            print 'msgDict: ' , msgDict
            
            image_id = long(msgDict['id'])
            
            print "image_id: ", image_id
            image = imgcatDB.getImage(image_id)
            print image.data
            path = image.downloadToTmp()
            logger.debug("got the image at: %s", path)
            image.getEXIF()
            image.getFingerprint()
            image.postWatson()
            image.getAlchemyKeywords()
            image.getAlchemyFaceTags()
            image.postSolr()
            
            q.delete_message(message)
        else:
            logger.info('waiting on message queue')
            sys.stdout.flush()
            time.sleep(5)
            
            sys.stdout.flush()
