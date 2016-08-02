# module imgcatDB

import MySQLdb
import os
import logging

import boto
import boto.sqs
from boto.s3.key import Key

import time
import sys
import subprocess

import json
import requests
from requests.auth import HTTPBasicAuth

import dataLayer
import pypuzzle

puzzle = pypuzzle.Puzzle()

import shutil

logger = logging.getLogger('imgcat')

from wand.image import Image as WandImage

#
# unit test connection
#
def countUsers() :
    return dataLayer.countUsers()

class User:
    data = {}
    def __init__ (self, rowdict) :
        self.data = rowdict

    def persist(self):
        print self.data
        sys.stdout.flush()
#
# unit test User
#
def getFirstUser() :
    return dataLayer.getFirstUserRow()


class Image:

    def __init__ (self, rowdict) :
        #  print rowdict
        self.data = rowdict
        if self.data['metadata'] is None:
            self.metadata = {}
        else:
            try:
                self.metadata = json.loads(self.data['metadata'])
            except ValueError, e:
                self.metadata = {}
                
    def persist(self):
        self.data['metadata'] = json.dumps(self.metadata)
        dataLayer.persistImageData(self.data)

    def localTempFilename(self):
        suffix = '.jpg'
        if (self.data['mimetype'] == 'image/png') :
            suffix = '.png'
        return '/tmp/' + str(self.data['image_uuid']) + suffix


    def localThumbFilename(self):
        suffix = '.jpg'
        if (self.data['mimetype'] == 'image/png') :
            suffix = '.png'
        return '/tmp/' + str(self.data['image_uuid']) + '-thumb' + suffix

    def uploadTmpToS3(self):
        #setup the bucket
        # c = boto.connect_s3(your_s3_key, your_s3_key_secret)

        bucket = 'imgcat-dev'
        c = boto.connect_s3()
        b = c.get_bucket(bucket, validate=False)
        keyname = os.path.basename(os.path.normpath(self.localTempFilename()))
        logger.debug( 'gonna create key: ' + keyname)
        sys.stdout.flush()
        k = Key(bucket=b, name=keyname)
        k.content_type = self.data['mimetype']
        k.set_contents_from_filename(self.localTempFilename())
        logger.info( "uploaded: " + keyname + " to S3")
        sys.stdout.flush()
        self.data['load_status'] = 'uploaded'
        self.persist()

    def uploadThumbToS3(self):
        #setup the bucket
        # c = boto.connect_s3(your_s3_key, your_s3_key_secret)

        bucket = 'imgcat-dev'
        c = boto.connect_s3()
        # b = c.get_bucket(bucket, validate=False)
        b = c.lookup(bucket)
        if (b == None):
            logger.error("Bucket not found: " + bucket)


        sys.stdout.flush()
        keyname = os.path.basename(os.path.normpath(self.localThumbFilename()))
        print 'gonna create key: ' , keyname
        k = Key(bucket=b, name=keyname)

        k.content_type = self.data['mimetype']
        k.set_contents_from_filename(self.localThumbFilename())
        k.set_acl('public-read')
        self.data['thumb_path'] = k.generate_url(expires_in=0, query_auth=False)

        logger.info("uploaded thumbnail:" + keyname + " to S3")
        sys.stdout.flush()
        self.data['load_status'] = 'thumbnailed'
        self.persist()

    def downloadToTmp(self):
        logger.info("downloading from web: " + str(self.data['image_uuid']))
        if ((self.data['upload_source_id'] == 'web') or (self.data['upload_source_id'] == 'facebook')) :
            response = requests.session().get(self.data['source_locater'], stream=True)
            if (response.status_code == 200) :
                logger.debug("starting download from %s to %s", self.data['source_locater'], self.localTempFilename())
                with open(self.localTempFilename(), 'wb') as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)  
                logger.debug("completed download from %s to %s", self.data['source_locater'], self.localTempFilename())
                self.uploadTmpToS3()
                return self.localTempFilename()
            else:
                logger.warn("status code: %s from %s",  response.status_code, self.data['source_locater'] )

        return None

    def getFingerprint(self):
        #        command = "puzzle-print -l 5 " + self.localThumbFilename()
        #        output = subprocess.Popen(["puzzle-print", "-l", "5", self.localThumbFilename()], stdout=subprocess.PIPE).communicate()[0]
        vec_1 = puzzle.get_cvec_from_file("file_1.jpg")
        print "FINGERPRINT is [" + vec_1 + ']'
        self.data['fingerprint'] = vec_1
        self.persist()
        possibleMatch = dataLayer.findPossibleDuplicate(self.data)
        print "our best match is: "
        print possibleMatch
        dataLayer.recordFingerprintTokens(self.data)
        return None
        
    def getEXIF(self):
        logger.info("extracting exif: " + str(self.data['image_uuid']))
        imgpath = self.localTempFilename()
        with WandImage(filename=imgpath) as img:

            self.data['original_width'], self.data['original_height'] = img.size
            exif = {}
            exif.update((k, v) for k, v in img.metadata.items())

            scaleRate = max(img.width, img.height) / 512
            if (scaleRate > 1.0):
                img.resize(img.width / scaleRate, img.height / scaleRate)
            img.format = 'jpeg'
            img.save(filename=self.localThumbFilename())

            self.uploadThumbToS3()
            # print "exif: " , exif
            self.metadata['exif'] = exif
            self.persist()
            
        return None

    def cleanFiles(self):
        try:
            os.unlink(self.localThumbFilename())
            os.unlink(self.localFilename())
        except:
            pass
    
        
#
# unit test image
#
def getFirstImage() :
    return Image(dataLayer.getFirstImageRow(longID))

def getImage(longID) :
    return  Image(dataLayer.getImageRow(longID))



