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

SQS_QUEUE = 'imgcat-alchemy'
AWS_REGION = 'us-west-2'
APIHOST = ''
APIKEY = ''

logging.Formatter.converter = time.gmtime
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger('imgcat')
logger.setLevel(logging.INFO)


    
def getAlchemyFaceTags(image, apihost, apikey):
    logger.info("posting to Alchemy: " + image.data['thumb_path'])
    sys.stdout.flush()
    urlParams = {
        'apikey': apikey,
        'outputMode': 'json',
        'url': image.data['thumb_path']
    }
    url= 'https://' + apihost + '/calls/url/URLGetRankedImageFaceTags'
    
    r = requests.get(url, params=urlParams)
    
    logger.info("response status:" + str(r.status_code))
    
    if (r.status_code == 200) :
        update_image = imgcatDB.getImage(image.data['image_uuid'])
        update_image.data['load_status'] = 'categorized_faces'
        update_image.metadata['alchemyFaces'] = r.json()
        update_image.persist()
        
    sys.stdout.flush()
    return None
    

def getAlchemyKeywords(image, apihost, apikey):
    logger.info("posting to Alchemy: " + image.data['thumb_path'])
    urlParams = {
        'apikey': apikey,
        'outputMode': 'json',
        'knowledgeGraph': 1,
        'url': image.data['thumb_path']
    }
    url= 'https://'+ apihost + '/calls/url/URLGetRankedImageKeywords'
    r = requests.get(url, params=urlParams)
    
    logger.info("response status:" + str(r.status_code))
    
    if (r.status_code == 200) :
        update_image = imgcatDB.getImage(image.data['image_uuid'])
        update_image.data['load_status'] = 'categorized_faces'
        update_image.metadata['alchemyKeywords'] = r.json()
        update_image.persist()
        
    sys.stdout.flush()
    return None

def monitorFeed(feed=SQS_QUEUE, aws_region=AWS_REGION, apihost=APIHOST,  apikey=APIKEY, solr_queue='imgcat-solr'):
    logger.info("alchemy classifier starting")
    
    # boto AWS connection credentials are in env or ~/.boto
    conn = boto.sqs.connect_to_region(aws_region) 
    q = conn.create_queue(feed)
    solrQ = conn.create_queue(solr_queue)
    logger.info(' connected to queue ' + feed)
    
    while True:
        print ''
        try:
            rs = q.get_messages(1)
        except:
            logger.warn('resetting connection:' + sqs_queue)
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
            logger.info("processing image_id: " + msgDict['id'])
            image = imgcatDB.getImage(image_id)
            getAlchemyKeywords(image, apihost, apikey)
            getAlchemyFaceTags(image, apihost, apikey)
            conn.send_message(solrQ, message.get_body());
            logger.info("alchemy classification complete. image_id: " + msgDict['id'])            
            sys.stdout.flush()
            q.delete_message(message)
        else:
            logger.info('waiting on message queue')
            sys.stdout.flush()
            time.sleep(5)
            
        sys.stdout.flush()
