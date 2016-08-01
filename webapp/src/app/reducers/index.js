import * as ActionTypes from '../actions'
import merge from 'lodash/merge'

import { routerReducer as routing } from 'react-router-redux'   // does magic, I suppose
import { combineReducers } from 'redux'

// Updates an entity cache in response to any action with response.entities.
// We count on this guy to populate the initial state via the default argument
function entities(state = { detected: {}, photos: {}}, action) {
  if (action.response && action.response.entities) {
    return merge({}, state, action.response.entities)
  }

  return state
}

function photos(state = { query: {}, docs: [] } , action) {
  const { type } = action

  if (type === ActionTypes.COUNTS_SUCCESS) {

    const { counts } = action.response.entities.counts

    var classified = 0
    const { status } = counts.facetFields

    for ( var i = 0; i < status.length; i+=2 ) {
      if (status[i].startsWith('categorized') ) {
	classified += status[i + 1]
      }
    }

    var nums = { total: counts.numFound, classified: classified }

    var nextState = Object.assign({}, state, {counts: nums})
    return nextState
  } else if (type === ActionTypes.PHOTOS_SUCCESS) {

    const { photos } = action.response.entities
    const {  start } = photos.solr.params
    const {  docs, numFound } = photos.solr
    
    const ndocs = state.queryChanged ? docs :  state.docs.concat(docs)
    
    var nextState = Object.assign({}, state, photos, { queryChanged: false, start: start, docs: ndocs, numFound: numFound })
    return nextState
    
  } else if (type === "ADD_QUERY_TERM" ) {
    var nextState = Object.assign({}, state)
    var  { query } = nextState
    const { term }  = action.response

    for (const key in term) {

      if (query.hasOwnProperty(key)) {
	const val = term[key]
	var words = query[key]

	if (typeof words === 'string') {
	  if (!words.equals(val)) {
	    query[key] = [ words, val]
	  }
	} else if (typeof words === 'object' && Array.isArray(words) && words.indexOf(val) == -1) {
	  query[key] = [...words, val] 
	}

      } else {
	query[key] = [ term[key] ]
      }
    }
    
    const queryChanged = true;
    nextState = Object.assign(nextState, { query, queryChanged })
    
    return nextState
    
  } else if (type === "REFRESH_QUERY" ) {
    nextState = Object.assign({}, state, { queryChanged: true, docs: [], numFound: 0, start: 0 })
    return nextState
  }  else if (type === "DELETE_QUERY_TERM" ) {
    var nextState = Object.assign({}, state)
    var  { query } = nextState
    const termType = action.response[0]
    const termVal = action.response[1]
    if (query.hasOwnProperty(termType)) {
      var words = query[termType]
      if (typeof words === 'string') {
	if (words.equals(termVal)) {
	  query[termType] = []
	}
      } else if (typeof words === 'object' && Array.isArray(words) && words.indexOf(termVal) > -1) {
	var ix = words.indexOf(termVal)
	var newArr = words.slice(0, ix).concat(words.slice(ix+1))
	query[termType] =  newArr  // [...words, val] 
      }
    }
    const queryChanged = true;
    nextState = Object.assign(nextState, { query, queryChanged })
    return nextState
  }
  return state
}

function queryTerms(state = { "query": { } }, action) {

  const { type, response } = action

  if (type === "ADD_QUERY_TERM" ) {
    var nextState = Object.assign({}, state)
    if (nextState.hasOwnProperty('photos')) {
      console.log("have photos in state");
    } else {
      console.log("DO NOT have photos in nextState");
    }
    return nextState
  }
  
  return state
  
}

// puts the detected face into the state
function detected ( state = { detected: {} }, action) {
  const { type } = action

  if (type == 'STORE_DETECTED') {
    
    if (action.detected) {
      return merge({}, state, action.detected)
    }
  }
  return state
}

// Updates error message to notify about the failed fetches.
function errorMessage(state = null, action) {
  const { type, error } = action

  if (type === ActionTypes.RESET_ERROR_MESSAGE) {
    return null
  } else if (error) {
    return action.error
  }

  return state
}

// iterate through all the reducers
const rootReducer = combineReducers({
  entities,
  detected,
  photos,
  errorMessage,
  routing
})

export default rootReducer
