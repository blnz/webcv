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

SOLR_HOST = 'ec2-54-187-86-241.us-west-2.compute.amazonaws.com:8983'
SOLR_CORE = 'imgcat'
SQS_QUEUE = 'imgcat-solr'
AWS_REGION = 'us-west-2'

logging.Formatter.converter = time.gmtime
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger('imgcat')
logger.setLevel(logging.INFO)

def solrDoc(data):
    if data['metadata'] is None:
        metadata = {}
    else:
        try:
            metadata = json.loads(data['metadata'])
        except ValueError, e:
            metadata = {}
            
    doc = {
        'id': str(data['image_uuid']),
        'owner': data['owner_uuid'],
        'status': data['load_status'],
        'image_name': data['image_name'],
        'thumbnail': data['thumb_path'],
    }

    words = [ data['image_name'] ]
    taxonomy = []
    toparray = []

    if 'watson' in metadata and 'scores' in metadata['watson']:
        for topic in metadata['watson']['scores']:
            toparray.append(topic['classifier_id'])
            words.append(topic['classifier_id'])
        
    try:
        for keyword in metadata['alchemyKeywords']['imageKeywords']:
            toparray.append(keyword['text'])
            try:
                taxonstr = ''
                val =  keyword['knowledgeGraph']['typeHierarchy']
                taxons = str.split(str(val), '/')[1:]
                for token in taxons:
                    if len(taxonstr) == 0:
                        taxonstr = token
                    else:
                        taxonstr = taxonstr + '/' + token
                    taxonomy.append(taxonstr)
                    words.append(taxonstr)
                        
            except KeyError, k:
                pass
            
    except KeyError, k:
        pass
        
    persons = []

    try:
        for tag in metadata['facebook']['tags']['data']:
            persons.append(tag['name'])
            words.append(tag['name'])
    except KeyError, k:
        pass

    faces = []
    genders = []
    ages = []
    if 'alchemyFaces' in metadata and 'imageFaces' in metadata['alchemyFaces']:
        for person in metadata['alchemyFaces']['imageFaces']:
            try:
                genders.append(person['gender']['gender'])
            except KeyError, k:
                pass
            try:
                ages.append(person['age']['ageRange'])
            except KeyError, k:
                pass
            try:
                faces.append(person['gender']['gender'] + person['age']['ageRange'])
            except KeyError, k:
                pass
            
    doc['topic'] = toparray
    doc['taxon'] = taxonomy
    # doc['text'] = ' '.join(words)
    fingerprint = data['fingerprint']
    fingerprintTokens = [ fingerprint[i:i+6] for i in range(0, (len(fingerprint) - 6)) ]
    doc['fingerprint'] = ' '.join(fingerprintTokens)
    doc['person'] = persons
    doc['face'] = faces
    doc['gender'] = genders
    
    return doc

def postSolr(imageData, host, core):
    logger.info("posting to solr: " + str(imageData['image_uuid']))
    logger.info("from metadata: " + json.dumps(json.loads(imageData['metadata']), indent=4))
                
    url = 'http://' + host + '/solr/' + core + '/update/json?commit=true'

    message = {
        'add':
        { 'doc': solrDoc(imageData) },
        'commit': {}
    }
    try:            
        print "Solr update message: " + json.dumps(message, indent=4)
        requests.post(url, json=message)
    except:
        pass

    return None

                

def monitorFeed(feed=SQS_QUEUE, solr_host=SOLR_HOST,  solr_core=SOLR_CORE, aws_region=AWS_REGION):
    
    logger.info("solrIndexer starting")
    
    # boto AWS connection credentials are in env or ~/.boto
    conn = boto.sqs.connect_to_region(aws_region) 
    q = conn.create_queue(feed)
    logger.info(' connected to queue ' + feed)
    
    while True:
        print ''
        try:
            rs = q.get_messages(1)
        except:
            logger.warn('resetting connection:' + feed)
            sys.stdout.flush()

            conn = boto.sqs.connect_to_region(aws_region)
            q = conn.create_queue(feed)
            rs = []
            pass
        
        num = len(rs)
        if (num > 0):
            message = rs[0]
            print "message: " , message.get_body()
            
            msgDict = json.loads(message.get_body())
            print 'msgDict: ' , msgDict
            
            image_id = long(msgDict['id'])
            
            logger.info("processing image_id: " + msgDict['id'])
            try:
                postSolr(dataLayer.getImageRow(image_id), solr_host, solr_core)
            except:
                logger.warn("failed to post image_id: " + msgDict['id'])
                pass
            
            logger.info("index complete image_id: " + msgDict['id'])            
            sys.stdout.flush()
            q.delete_message(message)
        else:
            logger.info('waiting on message queue: ' + feed)
            sys.stdout.flush()
            time.sleep(5)
            
        sys.stdout.flush()
