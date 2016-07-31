import { CALL_API, Schemas } from '../middleware/api'

// Relies on Redux Thunk middleware.

export const USER_REQUEST = 'USER_REQUEST'
export const USER_SUCCESS = 'USER_SUCCESS'
export const USER_FAILURE = 'USER_FAILURE'

function fetchUser(login) {

  return {
    [CALL_API]: {
      types: [ USER_REQUEST, USER_SUCCESS, USER_FAILURE ],
      endpoint: `users/${login}`,
      schema: Schemas.USER
    }
  }
}


export function storeDetected(detected) {
  console.log("dispatch store detected", detected)
  
  return (dispatch, getState) => {
    var act = {
      type: 'STORE_DETECTED',
      detected: detected
    }
    console.log (act)
    return dispatch(act)
  }
}

export function loadUser(login, requiredFields = []) {

  return (dispatch, getState) => {
    const user = getState().entities.users[login]
    if (user && requiredFields.every(key => user.hasOwnProperty(key))) {
      return null
    }
    
    return dispatch(fetchUser(login))
  }
}
export const LOGIN_USER_REQUEST = 'LOGIN_USER_REQUEST'
export const LOGIN_USER_SUCCESS = 'LOGIN_USER_SUCCESS'
export const LOGIN_USER_FAILURE = 'LOGIN_USER_FAILURE'


function fetchLoginUser() {

  return {
    [CALL_API]: {
      types: [ LOGIN_USER_REQUEST, LOGIN_USER_SUCCESS, LOGIN_USER_FAILURE ],
      endpoint: `ckuser`,
      schema: Schemas.USER
    }
  }
}


export function loadLoginUser(login, requiredFields = []) {

  return (dispatch, getState) => {
    const user = getState().entities.users[login]
    if (user && requiredFields.every(key => user.hasOwnProperty(key))) {
      return null
    }
    
    return dispatch(fetchLoginUser(login))
  }
}

export const IMAGE_DETAILS_REQUEST = 'IMAGE_DETAILS_REQUEST'
export const IMAGE_DETAILS_SUCCESS = 'IMAGE_DETAILS_SUCCESS'
export const IMAGE_DETAILS_FAILURE = 'IMAGE_DETAILS_FAILURE'

function fetchImageDetails(imageID, authToken) {

  return {
    [CALL_API]: {
      types: [ IMAGE_DETAILS_REQUEST, IMAGE_DETAILS_SUCCESS, IMAGE_DETAILS_FAILURE ],
      endpoint: `api/image/${imageID}?auth_token=${authToken}`,
      schema: Schemas.PHOTO_DETAILS
    }
  }
}

export function loadImageDetails(imageID, authToken, requiredFields = []) {
  // returns a function that takes a couple functions as arguments.
  return (dispatch, getState) => {
    return dispatch(fetchImageDetails(imageID, authToken))
  }
}


export const IMAGE_SIMILARS_REQUEST = 'IMAGE_SIMILARS_REQUEST'
export const IMAGE_SIMILARS_SUCCESS = 'IMAGE_SIMILARS_SUCCESS'
export const IMAGE_SIMILARS_FAILURE = 'IMAGE_SIMILARS_FAILURE'

function fetchSimilarImages(imageID, authToken) {

  return {
    [CALL_API]: {
      types: [ IMAGE_SIMILARS_REQUEST, IMAGE_SIMILARS_SUCCESS, IMAGE_SIMILARS_FAILURE ],
      endpoint: `api/image/${imageID}/similar?auth_token=${authToken}`,
      schema: Schemas.PHOTO_SIMILARS
    }
  }
}

export function loadSimilarImages(imageID, authToken, requiredFields = []) {
  // returns a function that takes a couple functions as arguments.
  return (dispatch, getState) => {
    return dispatch(fetchSimilarImages(imageID, authToken))
  }
}


export function updateUser(user, requiredFields = []) {
  return (dispatch, getState) => {

    return dispatch({ type: 'UPDATE_USER' ,
		      response: {"user": user}});
  }
}

export function postUser(user, requiredFields = []) {
  
  return (dispatch, getState) => {
    return dispatch({ type: 'POST_USER' ,
		      response: {"user": user}});
  }
}

//
//
//

export const PHOTOS_REQUEST = 'PHOTOS_REQUEST'
export const PHOTOS_SUCCESS = 'PHOTOS_SUCCESS'
export const PHOTOS_FAILURE = 'PHOTOS_FAILURE'

// Fetches a page of photos for a particular user's query.
// Relies on the custom API middleware defined in ../middleware/api.js.

// not clear why Schemas are defined in 'middleware/api'
function fetchPhotos(query, nextPageUrl) {
  // console.log("fetchPhotos building a CALL_API action for url: ", nextPageUrl)
  return {
    query,
    [CALL_API]: {
      types: [ PHOTOS_REQUEST, PHOTOS_SUCCESS, PHOTOS_FAILURE ],
      endpoint: nextPageUrl,
      schema: Schemas.PHOTO_ARRAY
    }
  }
}

export const COUNTS_REQUEST = 'COUNTS_REQUEST'
export const COUNTS_SUCCESS = 'COUNTS_SUCCESS'
export const COUNTS_FAILURE = 'COUNTS_FAILURE'

// Fetches a page of photos for a particular user's query.
// Relies on the custom API middleware defined in ../middleware/api.js.

// not clear why Schemas are defined in 'middleware/api'
function fetchCounts(query, nextPageUrl) {
  // console.log("fetchCounts building a CALL_API action for url: ", nextPageUrl)
  return {
    query,
    [CALL_API]: {
      types: [ COUNTS_REQUEST, COUNTS_SUCCESS, COUNTS_FAILURE ],
      endpoint: nextPageUrl,
      schema: Schemas.COUNTS_ARRAY
    }
  }
}

function queryUrlParams(query) {
  var url = "";
  // console.log ("QUERY IS:", query)
  if (typeof query === 'undefined' || "*" === query || query.length == 0) {
    // console.log("wildcard query");
    url = `q=owner:${loggedInUser.user_uuid}`;
  } else {
    var qterms = []
    for (var key in query) {
      // FIXME: deal with strings vs array as value
      if (query.hasOwnProperty(key)) {
	
	var val = query[key]
	if (typeof val === 'string') {
	  qterms.push(key.concat(":").concat(query[key]))
	} else {
	  val.map(function(x) { qterms.push(key.concat(":").concat(x)) } )
	}
      }
    }
    if (qterms.length > 0) {
      
      url = "q=".concat(qterms.join(" AND ")).concat(" AND owner:").concat(loggedInUser.user_uuid)
    } else {
      url = `q=owner:${loggedInUser.user_uuid}`;
    }
  }
  console.log("built query: [", url, "]");
  return url;
}

// a query term is an object that maps a solr facet name against a string value, e.g. { person: "MALE>65" }
export function addQueryTerm(term) {
  // console.log("addQueryTerm")
  return (dispatch, getState) => {
    return dispatch(
      { type: "ADD_QUERY_TERM",
 	response: { term }});
  }
}


export function deleteQueryTerm(term) {
  // console.log("deleteQueryTerm")
  return (dispatch, getState) => {
    return dispatch(
      { type: "DELETE_QUERY_TERM",
	response:  term.split(':') } );
  }
}


export function refreshQuery() {
  // console.log("deleteQueryTerm")
  return (dispatch, getState) => {
    return dispatch(
      { type: "REFRESH_QUERY",
	response:  {  }  } );
  }
}

// Fetches a page of photos for a  particular user.
// Bails out if page is cached and user didn’t specifically request next page.
// Relies on Redux Thunk middleware.
export function loadPhotos(query, authToken, start=0) {
  // console.log("####### Load Photos entry for query: [", query, "] authToken", authToken)
  var qurl = queryUrlParams(query);
  return (dispatch, getState) => {
    const {
      nextPageUrl = `api/search?facet.field=topic&facet.field=taxon&facet.field=person&facet.field=face&facet=on&indent=on&${qurl}&rows=10&start=${start}&wt=json&sort=_docid_ desc&auth_token=${authToken}`,
      pageCount = 0
    } = {}
    
    if (pageCount > 0 && !nextPage) {
      return null
    }
    // construct and dispatch the action that will fetch a URL, postprocess the results via a schema, then somebody
    // in reducers will place the data in the store and notify some containers
    return dispatch(fetchPhotos(query, nextPageUrl))
  }
}

export function loadCounts(authToken, nextPage) {
  // console.log("# counts of image processing entry for authToken:", authToken)

  return (dispatch, getState) => {
    const {
      nextPageUrl = `api/search?facet.field=status&facet=on&indent=on&q=owner:${loggedInUser.user_uuid}&rows=0&start=0&wt=json&auth_token=${authToken}`,
      pageCount = 0
    } = {}
    
    //if (pageCount > 0 && !nextPage) {
    //  console.log("Bailing out on loadCounts")
    //  return null
    // }
    // construct and dispatch the action that will fetch a URL, postprocess the results via a schema, then somebody
    // in reducers will place the data in the store and notify some containers
    // console.log("dispatching fetch Counts")    
    return dispatch(fetchCounts({}, nextPageUrl))
  }
}

//
//
//

export const STARRED_REQUEST = 'STARRED_REQUEST'
export const STARRED_SUCCESS = 'STARRED_SUCCESS'
export const STARRED_FAILURE = 'STARRED_FAILURE'

// Fetches a page of starred repos by a particular user.
// Relies on the custom API middleware defined in ../middleware/api.js.
function fetchStarred(login, nextPageUrl) {
  return {
    login,
    [CALL_API]: {
      types: [ STARRED_REQUEST, STARRED_SUCCESS, STARRED_FAILURE ],
      endpoint: nextPageUrl,
      schema: Schemas.REPO_ARRAY
    }
  }
}

// Fetches a page of starred repos by a particular user.
// Bails out if page is cached and user didn’t specifically request next page.
// Relies on Redux Thunk middleware.
export function loadStarred(login, nextPage) {
  return (dispatch, getState) => {
    const {
      nextPageUrl = `users/${login}/starred`,
      pageCount = 0
    } = getState().pagination.starredByUser[login] || {}

    if (pageCount > 0 && !nextPage) {
      return null
    }

    return dispatch(fetchStarred(login, nextPageUrl))
  }
}


//
//
//

export const STARGAZERS_REQUEST = 'STARGAZERS_REQUEST'
export const STARGAZERS_SUCCESS = 'STARGAZERS_SUCCESS'
export const STARGAZERS_FAILURE = 'STARGAZERS_FAILURE'

// Fetches a page of stargazers for a particular repo.
// Relies on the custom API middleware defined in ../middleware/api.js.
function fetchStargazers(fullName, nextPageUrl) {
  return {
    fullName,
    [CALL_API]: {
      types: [ STARGAZERS_REQUEST, STARGAZERS_SUCCESS, STARGAZERS_FAILURE ],
      endpoint: nextPageUrl,
      schema: Schemas.USER_ARRAY
    }
  }
}

// Fetches a page of stargazers for a particular repo.
// Bails out if page is cached and user didn’t specifically request next page.
// Relies on Redux Thunk middleware.
export function loadStargazers(fullName, nextPage) {
  return (dispatch, getState) => {
    const {
      nextPageUrl = `repos/${fullName}/stargazers`,
      pageCount = 0
    } = getState().pagination.stargazersByRepo[fullName] || {}

    if (pageCount > 0 && !nextPage) {
      return null
    }

    return dispatch(fetchStargazers(fullName, nextPageUrl))
  }
}

export const RESET_ERROR_MESSAGE = 'RESET_ERROR_MESSAGE'

// Resets the currently visible error message.
export function resetErrorMessage() {
  return {
    type: RESET_ERROR_MESSAGE
  }
}
