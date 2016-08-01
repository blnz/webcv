Face recognition with webrtc, websockets and opencv
==========================================

Based on 
https://github.com/ragulin/face-recognition-server


How does it work?
-------------------
Frames are captured from the web camera via webrtc and sent to the server over websockets. On the server the frames are processed with opencv and a json response is sent back to the client.

Sample json response:

      {
        "face": {
          "distance": 428.53381034802453,
          "coords": {
            "y": "39",
            "x": "121",
            "height": "137",
            "width": "137"
          },
          "name": "mike"
        }
      }

Everything except `distance` is pretty self explanatory.

* `name` is the predicted name of the person in front of the camera.

* `coords` is where the face is found in the image.

* `distance` is a measurement on how accurate the prediction is, lower is better.

If we can't get a reliable prediction (10 consecutive frames that contains a face and with a distance lower than 1000) we switch over to training mode. In training mode we capture 10 images and send them together with a name back to the server for retraining. After the training has been completed we switch back to recognition mode and hopefully we'll get a more accurate result.

Running it
----------

docker-compose up

It re-installs the image and retrians the model, every time on startup.

browse to localhost:3000

