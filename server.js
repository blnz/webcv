var webpack = require('webpack')
var webpackDevMiddleware = require('webpack-dev-middleware')
var webpackHotMiddleware = require('webpack-hot-middleware')
var wpConfig = require('./webpack-dev-server.config')
var express = require('express')
var session = require('express-session')
var fbConfig = require('./config')()
var cookieParser = require('cookie-parser')
var bodyParser = require('body-parser')
var path = require('path')
var request = require('request')

var app = express()
var port = fbConfig.port

// give the app the simplest controller
router = express.Router()
router.get('/',  function(req, res) {
  res.sendFile(__dirname + '/src/www/index.html')
})

app.use(router);

app.use(cookieParser());
app.use(bodyParser());
app.use(session({ secret: 'keyboard cat' }));

console.log("fbConfig:", fbConfig);

if (fbConfig.mode === 'local') {
  var compiler = webpack(wpConfig)
  app.use(webpackDevMiddleware(compiler, { noInfo: false, publicPath: wpConfig.output.publicPath }))
  app.use(webpackHotMiddleware(compiler))
} else {
  //
  app.use(express.static(path.resolve(__dirname, 'build')));
}


console.info("running at " , __dirname);

// app.get('/', function(req, res) {
//   res.sendFile(__dirname + '/src/www/index.html')
// })

app.listen(port, function(error) {
  if (error) {
    console.error(error)
  } else {
    console.info("==> 🌎  Listening on port %s. Open up http://localhost:%s/ in your browser.", port, port)
  }
})
