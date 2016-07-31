#!/usr/bin/python

import boto
import boto.sqs
import time
import sys
import dataLayer
import json
from boto.s3.key import Key
import requests
import facebook
import logging


logging.Formatter.converter = time.gmtime
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger('imgcat')
logger.setLevel(logging.DEBUG)


def bestimage(seq):
    ''' Return highest resolution version of image'''
    max_index = 0
    if seq:
        max_val = seq[0]['width']
        for i,val in ((i, val) for i, val in enumerate(seq) if val['width']  > max_val):
            max_val = val['width']
            max_index = [i]
            
    return max_index
        

def pullFacebook(token, solr_queue='imgcat-solr', loader_queue='imgcat-loader', aws_region='us-west-2'):
    
    conn = boto.sqs.connect_to_region(aws_region)
    loaderQ = conn.create_queue(loader_queue)
    solrQ = conn.create_queue(solr_queue)
    
    logger.info("obtaining graph")
    graph = facebook.GraphAPI(access_token=token, version='2.2')

    wasgqs = ['me/photos/uploaded?fields=album,picture,updated_time,event,images,created_time,caption,tags{id,name,tagging_user,created_time},name_tags,name',
           'me?fields=name,email,id,about'
    ]
    gqs = []
    for query in gqs:
        logger.info('query: ' + query)
        result = graph.get_object(query)
        logger.info(json.dumps(result, indent=4))
        logger.info("did get graph")

    user_query = 'me?fields=name,email,id,about'
    result = graph.get_object(user_query)
    fb_id = result['id']

    image_owner_id = 0
    
    if (fb_id):
        fbUser = dataLayer.getFacebookUser(fb_id)
        image_owner_id = fbUser.data['user_uuid']


    print 'facebook_id: ' + fb_id +  ' is user: ' +  str(image_owner_id)
    
    photos_query ='me/photos/uploaded?fields=album,picture,updated_time,event,images,created_time,tags{id,name,tagging_user,created_time},name_tags,name'

    result = graph.get_object(photos_query)
    # print result
    logger.info("pagination: " + json.dumps(result['paging'], indent=4))
    
    while True:
        try:
            for photo in result['data'] :
        
                # logger.info('photo: ' + json.dumps(photo, indent=4))
                best_image = photo['images'][bestimage(photo['images'])]
                # logger.info('best image: ' + json.dumps(best_image))
                
                imageDict = { 'owner_uuid' : image_owner_id ,
                              'image_name' : photo.get('name', 'untitled'),
                              'mimetype' : 'image/jpeg',
                              'upload_source_id' : 'facebook',
                              'source_locator': best_image['source'],
                              'load_status': 'identified',
                              'width': best_image['width'],
                              'height': best_image['height'],
                              'metadata': json.dumps({ 'facebook' : { 'tags' : photo.get('tags', {}) } })
                }
                logger.info("insert_data: " + json.dumps(imageDict))
                image_id = dataLayer.createImage(imageDict)
                if (image_id > 0):
                    logger.info("created: " + str(image_id))
                    message = json.dumps( { 'id' : str(image_id) } )
                    #                    print message
                    
                    conn.send_message(loaderQ, message);
                    conn.send_message(solrQ, message);
                    
                else:
                    logger.info("could not create")

            result = requests.get(result['paging']['next']).json()
            logger.info('got another page')
            print result

        except KeyError:
            # done pagination
            break
        

def monitorFeed(feed='imgcat-user', aws_region="us-west-2"):
    conn = boto.sqs.connect_to_region("us-west-2")
    loaderQ = conn.create_queue('imgcat-loader')
    solrQ = conn.create_queue('imgcat-solr')
    userQ = conn.create_queue(feed)
    
    while True:
        print ''
        try:
            rs = userQ.get_messages(1)
        except:
            print 'resetting connection'
            conn = boto.sqs.connect_to_region("us-west-2")
            userQ = conn.create_queue(feed)
            rs = []
            pass

        num = len(rs)
        if (num > 0):
            message = rs[0]
            print "message: " , message.get_body()
            
            msgDict = json.loads(message.get_body())
            print 'msgDict: ' , msgDict
            
            accessToken = msgDict['token']
            try:
                pullFacebook(accessToken)
            except:
                logger.warn("unable to load from the token")
                
            userQ.delete_message(message)
        else:
            logger.info('waiting on message queue: ' + feed)
            sys.stdout.flush()
            time.sleep(5)
            
        sys.stdout.flush()
