import { Schema, arrayOf, normalize } from 'normalizr'
import { camelizeKeys } from 'humps'
import 'isomorphic-fetch'

function getNextPageUrl(response) {
  return null
}

const API_ROOT = `${window.location.protocol}//${window.location.host}/`    // FIXME

// Fetches an API response and normalizes the result JSON according to schema.
// This makes every API response have the same shape, regardless of how nested it was.
function callApi(endpoint, schema) {
  
  const fullUrl = ((endpoint.indexOf("http://" ) != 0) && (endpoint.indexOf("https://" ) != 0) ) ? API_ROOT + endpoint : endpoint

/***
we fetch a url, when we recieve a response, we have a function
then1: which takes a response, grabs the json and passes the json to a unction
then2: which accepts the json as a param passes the json and respinse to a function
then3: which check for a bad HTTP status code 

**/
  
  return fetch(fullUrl)
    .then(response =>        // then1
	  response.json().then(json => ({ json, response })) // then2
	 ).then( ({ json, response }) => {                    // then3
	   if (!response.ok) {
	     console.log("*** response not ok", response)
	     return Promise.reject(json)
	   }

	   console.log("callApi() got json: ", json)
	   const camelizedJson = camelizeKeys(json)
	   const nextPageUrl = getNextPageUrl(response)

	   console.log ("callApi has constructed and will return this object:",
			Object.assign({},
				normalize(camelizedJson, schema),
				{ nextPageUrl }
			       )
		       )
	   
	   return Object.assign({},
				normalize(camelizedJson, schema),
				{ nextPageUrl }
			       )
	 })
}

// We use this Normalizr schemas to transform API responses from a nested form
// to a flatter form where repos and users are placed in `entities`, and nested
// JSON objects are replaced with their IDs. This is very convenient for
// consumption by reducers, because we can easily build a normalized tree
// and keep it updated as we fetch more data.

// Read more about Normalizr: https://github.com/gaearon/normalizr


const userSchema = new Schema('users', {
  idAttribute: user => user.login.toLowerCase()
})

const repoSchema = new Schema('repos', {
  idAttribute: repo => repo.fullName.toLowerCase()
})
const photoSchema = new Schema('photos', {
  idAttribute: solr => 'solr'
})
const countsSchema = new Schema('counts', {
  idAttribute: counts => 'counts'
})
const photoDetailsSchema = new Schema('photo_details', {
  idAttribute: 'imageUuid'
})
const photoSimilarsSchema = new Schema('photo_similars', {
  idAttribute: 'imageUuid'
})

repoSchema.define({
  owner: userSchema
})

// Schemas for API responses.

export const Schemas = {
  USER: userSchema,
  USER_ARRAY: arrayOf(userSchema),
  REPO: repoSchema,
  REPO_ARRAY: arrayOf(repoSchema),
  PHOTO: photoSchema,
  PHOTO_ARRAY: arrayOf(photoSchema),
  COUNTS: countsSchema,
  COUNTS_ARRAY: arrayOf(countsSchema),
  PHOTO_DETAILS: photoDetailsSchema,
  PHOTO_DETAILS_ARRAY: arrayOf(photoDetailsSchema),
  PHOTO_SIMILARS: photoSimilarsSchema,
  PHOTO_SIMILARS_ARRAY: arrayOf(photoSimilarsSchema)
}

// Action key that carries API call info interpreted by this Redux middleware.

export const CALL_API = Symbol('Call API')

// A Redux middleware that interprets actions with CALL_API info specified.
// Performs the call and promises when such actions are dispatched.

export default store => next => action => {
  const callAPI = action[CALL_API]
  if (typeof callAPI === 'undefined') {
    return next(action)
  }

  let { endpoint } = callAPI

  // endpoint is a function or string
  console.log("CALL_API for : ", endpoint)
  
  const { schema, types } = callAPI

  if (typeof endpoint === 'function') {
    endpoint = endpoint(store.getState())
  }

  if (typeof endpoint !== 'string') {
    throw new Error('Specify a string endpoint URL.')
  }
  if (!schema) {
    throw new Error('Specify one of the exported Schemas.')
  }
  if (!Array.isArray(types) || types.length !== 3) {
    throw new Error('Expected an array of three action types.')
  }
  if (!types.every(type => typeof type === 'string')) {
    throw new Error('Expected action types to be strings.')
  }

  function actionWith(data) {
    const finalAction = Object.assign({}, action, data)
    delete finalAction[CALL_API]
    return finalAction
  }

  const [ requestType, successType, failureType ] = types
  next(actionWith({ type: requestType }))

  return callApi(endpoint, schema).then(
    response => next(actionWith({
      response,
      type: successType
    })),
    error => next(actionWith({
      type: failureType,
      error: error.message || 'Something bad happened'
    }))
  )
}
