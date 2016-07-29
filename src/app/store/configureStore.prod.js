import { createStore, applyMiddleware } from 'redux'
import thunk from 'redux-thunk'
import api from '../middleware/api'
import rootReducer from '../reducers'

export default function configureStore(initialState) {
  console.log("PRODUCTION STORE")
  return createStore(
    rootReducer,
    initialState,
    applyMiddleware(thunk, api)
  )
}
