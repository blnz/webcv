
import MySQLdb
import os
import logging

import sys

logger = logging.getLogger('imgcat')

#
# ToDo: Cache this? how long does a connection last?
#
def db() :
    return  MySQLdb.connect(host='ic-dev-cluster.cluster-c5nkdi9sl4i0.us-west-2.rds.amazonaws.com', user='imgcat', passwd='img302cat', db='imgcat')


#
# unit test connection
#
def countUsers() :
    cursor = db().cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor.execute("select count(*) as count from user")
    r = cursor.fetchone()
    print r
    print cursor.description
    sys.stdout.flush()
    return r

class UserData:
    data = {}
    def __init__ (self, rowdict) :
        self.data = rowdict

    def persist(self):
        print self.data
        sys.stdout.flush()


def getFacebookUser(fb_id):
    cursor = db().cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor.execute("select *  from user where facebook_id = %s", [ fb_id ])
    return UserData(cursor.fetchone())

    
#
# unit test User
#
def getFirstUserRow() :
    cursor = db().cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor.execute("select * from user")
    r = cursor.fetchone()
    return r


class ImageData:
    data = {}
    update_SQL = "update image set owner_uuid = %s, image_name = %s, mimetype = %s, upload_source_id = %s, source_locater = %s, load_status = %s, failure_reason = %s, original_path = %s, original_width= %s, original_height= %s, thumb_path= %s, thumb_width = %s, thumb_height= %s, fingerprint= %s, metadata= %s, updated_at = now() where image_uuid = %s"

    insert_fingerprint_SQL = "insert into fingerprint_word values (%s, %s, %s)"

    find_similar_SQL = "select image_uuid, count(*) as count from fingerprint_word where owner_uuid = %s and fp_word in ( %s ) GROUP BY image_uuid order by count desc limit 5"
    
    def __init__ (self, rowdict) :
        self.data = rowdict

    def recordFingerprint(self) :
        fingerprint = self.data['fingerprint']
        fingerprintTokens = [ [ self.data['owner_uuid'], self.data['image_uuid'], str(i).zfill(3) + "_" + fingerprint[i:i+6] ] for i in range(0, (len(fingerprint) - 6)) ]
        conn = db()
        cursor = conn.cursor()
        cursor.executemany(self.insert_fingerprint_SQL, fingerprintTokens)
        conn.commit()        

    def bestFingerprintMatch(self) :
        fingerprint = self.data['fingerprint']
        fingerprintTokens = [  str(i).zfill(3) + "_" + fingerprint[i:i+6] for i in range(0, (len(fingerprint) - 6)) ]
        
        format_strings = ','.join(['%s'] * len(fingerprintTokens))
        
        conn = db()
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        cursor.execute(self.find_similar_SQL % ( self.data['owner_uuid'], format_strings ), tuple(fingerprintTokens))
        r = cursor.fetchone()
        return r
        
    def persist(self):
        conn = db()
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        print self.data
        cursor.execute(self.update_SQL, [ self.data['owner_uuid'], self.data['image_name'], self.data['mimetype'], self.data['upload_source_id'], self.data['source_locater'], self.data['load_status'], self.data['failure_reason'], self.data['original_path'], self.data['original_width'], self.data['original_height'], self.data['thumb_path'], self.data['thumb_width'], self.data['thumb_height'], self.data['fingerprint'], self.data['metadata'], self.data['image_uuid'] ])
        logger.info("persisted") #  with fingerprint" + self.data['fingerprint'])
        sys.stdout.flush()
        conn.commit()
        

new_image_sql = "insert into image (image_uuid, owner_uuid, image_name, mimetype, upload_source_id, source_locater, original_width, original_height, metadata, updated_at) values (uuid_short() MOD 100000000000, %s, %s, %s, %s, %s, %s, %s, %s, now())"        

def createImage(rowdict):
        conn = db()
        cursor = conn.cursor()

        rowid = -1
        try:
            cursor.execute(new_image_sql, [ rowdict['owner_uuid'],
                                            rowdict['image_name'],
                                            rowdict['mimetype'],
                                            rowdict['upload_source_id'],
                                            rowdict['source_locator'],
                                            rowdict['width'],
                                            rowdict['height'],
                                            rowdict['metadata'] ] )

            cursor.execute('select image_uuid from image where source_locater = %s', [rowdict['source_locator']])
            rowid = cursor.fetchone()[0]
            conn.commit()

        except: #  (_mysql_exceptions.IntegrityError):
            logger.info("dup source, probably")
            

        return rowid
        
#
# unit test image DB
#
def getFirstImageRow() :
    cursor = db().cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor.execute("select * from image")
    r = cursor.fetchone()
    if (r['image_uuid']):
        return r
    return None

def getImageRow(longID) :
    conn = db()
    cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor.execute("select * from image where image_uuid = %s", [longID])
    r = cursor.fetchone()
    try:
        if (r['image_uuid']):
            return r
    except:
        pass
    return None

def persistImageData(data) :
    ImageData(data).persist()

def persistImageData(data) :
    ImageData(data).persist()

def recordFingerprintTokens(data) :
    ImageData(data).recordFingerprint()

def findPossibleDuplicate(data) :
    return ImageData(data).bestFingerprintMatch()
