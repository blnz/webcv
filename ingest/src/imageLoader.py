#!/usr/bin/python

import boto
import boto.sqs
import time
import sys
import imgcatDB
import json
from boto.s3.key import Key
import requests
import dataLayer
import logging
from requests.auth import HTTPBasicAuth

SOLR_SQS_QUEUE = 'imgcat-solr'
ALCHEMY_SQS_QUEUE = 'imgcat-alchemy'
LOADER_SQS_QUEUE = 'imgcat-loader'

AWS_REGION = 'us-west-2'
APIHOST = 'gateway.watsonplatform.net'
APIUSER = "e9418f1e-c7e9-480b-b973-96620bc26281"
APIKEY = "nqnIoyO50MwV"

logging.Formatter.converter = time.gmtime
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger('imgcat')
logger.setLevel(logging.INFO)



def postWatson(image, apihost, wUsername, wPassword):
    logger.info("posting to watson: " + str(image.data['image_uuid']))
    url= 'https://' + apihost + '/visual-recognition-beta/api/v2/classify?version=2015-12-02'
    files = { 'images_file': open(image.localTempFilename(), 'rb')}
    r = requests.post(url, files=files, auth=HTTPBasicAuth(wUsername, wPassword))
    logger.info("response status:" + str(r.status_code))

    if (r.status_code == 200) :
        watson = r.json()['images'][0]
        update_image = imgcatDB.getImage(image.data['image_uuid'])
        update_image.metadata['watson'] = watson
        update_image.data['load_status'] = 'categorized-watson'
        update_image.persist()
        
    sys.stdout.flush()
    return None


def monitorFeed(feed=LOADER_SQS_QUEUE, aws_region=AWS_REGION, apihost=APIHOST,  apiuser=APIUSER, apikey=APIKEY, solr_queue=SOLR_SQS_QUEUE, alchemy_queue=ALCHEMY_SQS_QUEUE):
    logger.info("image loader starting")
    
    # boto AWS connection credentials are in env or ~/.boto
    conn = boto.sqs.connect_to_region(aws_region) 
    q = conn.create_queue(feed)
    solrQ = conn.create_queue(solr_queue)
    alchemyQ = conn.create_queue(alchemy_queue)
    logger.info(' connected to queue ' + feed)
    
    while True:
        print ''
        try:
            rs = q.get_messages(1)
        except:
            logger.warn('resetting connection:' + feed)
            conn = boto.sqs.connect_to_region(aws_region)
            q = conn.create_queue(feed)
            rs = []
            pass
        
        num = len(rs)
        if (num > 0):
            message = rs[0]
            # print "message: " , message.get_body()
            
            msgDict = json.loads(message.get_body())
            # print 'msgDict: ' , msgDict
            
            image_id = long(msgDict['id'])
            logger.info("loading image_id: " + msgDict['id'])
            try:
                image = imgcatDB.getImage(image_id)
                path = image.downloadToTmp()
                logger.debug("got the image at: %s", path)
                image.getEXIF()
                
                conn.send_message(alchemyQ, message.get_body());
                conn.send_message(solrQ, message.get_body());
                
                image.getFingerprint()
                
                postWatson(image, apihost, apiuser, apikey)
                conn.send_message(solrQ, message.get_body());

                image.cleanFiles()
            
                logger.info("loading complete image_id: " + msgDict['id'])
            except:
                logger.warn("unable to load ")
                
            sys.stdout.flush()
            q.delete_message(message)
        else:
            logger.info('waiting on message queue')
            sys.stdout.flush()
            time.sleep(5)
            
        sys.stdout.flush()
