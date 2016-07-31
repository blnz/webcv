import 'babel-polyfill'
import React from 'react'
import { render } from 'react-dom'
import { browserHistory } from 'react-router'
import { syncHistoryWithStore } from 'react-router-redux'

import configureStore from './store/configureStore'

import injectTapEventPlugin from 'react-tap-event-plugin';
import Root from './containers/Root'; // Our custom react component

//Needed for onTouchTap  (responsive tap events on iOS)
//Can go away when react 1.0 release
//Check this repo:
//https://github.com/zilverline/react-tap-event-plugin
injectTapEventPlugin();

// redux singleton representation of all app state 
const store = configureStore()

const history = syncHistoryWithStore(browserHistory, store)

// Render the main app react component into the app div.
// For more details see: https://facebook.github.io/react/docs/top-level-api.html#react.render

render(
  <Root store={store} history={history} />,
  document.getElementById('app')
)
