import logging
import tornado.escape
import tornado.ioloop
from tornado.ioloop import IOLoop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
from PIL import Image
import time
import aiohttp
from tornado.platform.asyncio import AsyncIOMainLoop
import asyncio


from io import StringIO
from io import BytesIO

import uuid
import numpy
import json
from tornado.options import define, options
import opencv

define("port", default=8888, help="run on the given poort", type=int)

class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
        #(r"/", MainHandler),
        #(r"/facedetector", FaceDetectHandler),
        (r"/", SetupHarvestHandler),
        (r"/harvesting", HarvestHandler),
        (r"/predict", PredictHandler),
        (r"/train", TrainHandler)
        ]

    settings = dict(
#        cookie_secret="asdsafl.rleknknfkjqweonrkbknoijsdfckjnk 234jn",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=False,
        autoescape=None,
        debug=True
        )
    tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("facedetect.html")

class SocketHandler(tornado.websocket.WebSocketHandler):

  def open(self):
    logging.info('new connection')

  def check_xsrf_cookie():
    pass
  
  def check_origin(self, origin):
    return True
  
  def on_message(self, message):
    print("got message")
    #    print (message)
    image = Image.open(BytesIO(message))
    cv_image = numpy.array(image)
    self.process(cv_image)

  def on_close(self):
    logging.info('connection closed')

  def process(self, cv_image):
    pass

class FaceDetectHandler(SocketHandler):

  def process(self, cv_image):
    faces = opencv.detect_faces(cv_image)
    if len(faces) > 0:
      result = json.dumps(faces.tolist())
      self.write_message(result)

class SetupHarvestHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("harvest.html")

  def post(self):
    name = self.get_argument("label", None)
    if not name:
      logging.error("No label, bailing out")
      return
    logging.info("Got label %s" %  name)
    (newName, success) = opencv.Label.get_or_create(name=name)
    newName.persist()
    logging.info("Setting secure cookie %s" % name)
    self.set_secure_cookie('label', name)
    self.redirect("/")

class HarvestHandler(SocketHandler):
  def process(self, cv_image):
    label = opencv.Label.get(opencv.Label.name == self.get_secure_cookie('label'))
    logging.info("Got label: %s" % label.name)
    if not label:
      logging.info("No cookie, bailing out")
      return
    logging.info("About to save image")
    result = opencv.Image(label=label).persist(cv_image)
    if result == 'Done':
      self.write_message(json.dumps(result))

class TrainHandler(tornado.web.RequestHandler):
  def post(self):
    opencv.train()

class PredictHandler(SocketHandler):
  def process(self, cv_image):
    logging.info("PredictHandler process()")
    result = opencv.predict(cv_image)
    if result: 
      self.write_message(json.dumps(result))

def main():
  tornado.options.parse_command_line()

  # reset the training data and train a new model
  opencv.Image().delete()
  logging.info("Images deleted")
  opencv.Label().delete()
  logging.info("Labels deleted")
  opencv.load_images_to_db("data/images")
  logging.info("Labels and images loaded")
  opencv.train()
  logging.info("Model trained")

  app = Application()
  app.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()
