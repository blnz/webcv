import React, { PropTypes } from 'react';

import { connect } from 'react-redux'
import { storeDetected } from '../actions'

import merge from 'lodash/merge'

class MainWidget extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.ws = null
  }

  componentWillReceiveProps(nextProps) {
    console.log("got new props")
    // loadData(nextProps)
  }

  componentDidMount(){

    var { storeDetected } = this.props
    
    var ws = new WebSocket("ws://" + location.hostname + ":8888/predict");
    
    ws.onopen = function() {
      return console.log("Opened websocket");
    };

    ws.onmessage = function(e) {
      
      var mdata = JSON.parse(e.data)
      console.log(mdata)
      var openCvCoords = JSON.parse(e.data)[0];
      storeDetected(mdata);
      // return ctx.strokeRect(openCvCoords[0], openCvCoords[1], openCvCoords[2], openCvCoords[3]);
      
    };
    
    var updater = function(ws, video) {
      var canvas = document.querySelector('canvas');
      var ctx = canvas.getContext('2d');
      
      ctx.strokeStyle = '#dd4';
      ctx.lineWidth = 2;

      return ( () => {
        ctx.drawImage(video, 0, 0, 320, 240);
        return canvas.toBlob(function(blob) {
          return ws.send(blob);
        }, 'image/jpeg');
      })
    };
    
    var onError = function(e) {
      return console.log("Rejected", e);
    };

    // on successfully getting hold of users webrtc video cam,
    // we attach it to an element in the DOM
    var onSuccess = function(localMediaStream) {
      var  video = document.querySelector('video');
      video.src = URL.createObjectURL(localMediaStream);
      return setInterval(updater(ws, video), 500);
    };
    
    navigator.webkitGetUserMedia({
      'video': true,
      'audio': false
    }, onSuccess, onError);
    
  }
  
  render() {
    console.log("rendering")
    var { face } = this.props
    if (face) {
      console.log("painting face", face)
      var canvas = document.querySelector('canvas');
      var ctx = canvas.getContext('2d');
      
      ctx.strokeStyle = '#dd4';
      ctx.lineWidth = 2;
      ctx.strokeRect(face.coords.x, face.coords.y, face.coords.width, face.coords.height);

    }

    return (
	<div>
        <div style={{margin: "10px"}} >
        <video id="live" width="640" height="480" autoPlay></video>
        </div>

        <div style={{margin: "10px"}} >
        <canvas width="320" id="canvas" height="240" ></canvas>
        </div>
	</div>
      )
    }
}

MainWidget.propTypes = {
}

function mapStateToProps(state, ownProps) {
  var { face } = state.detected
  console.log("merging face:", face)
  // return ownProps
  var newProps = merge( {}, state, ownProps, {face: face} )
  console.log("newProps!!!", newProps)
  return merge( {}, state, ownProps, {face: face} )
}

export default connect(mapStateToProps, { storeDetected })(MainWidget)
