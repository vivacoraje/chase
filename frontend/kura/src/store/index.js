import Vue from 'vue'
import Vuex from 'vuex'
import { videos, search, switchFinishState, authenticate, subscriptions } from '@/api'
import { isValidToken, EventBus } from '../utils'
Vue.use(Vuex)

const state = {
  subscriptions: [],
  searchResult: [],
  userData: {},
  tokens: {},
  videos: {}
}

const actions = {
  loadSubscriptions (context, { username }) {
    return subscriptions(username)
      .then((response) => {
        context.commit('setSubscriptions', { subscriptions: response.data })
      })
  },
  // addSubscription (context, { user, token }) {
  //   return subscribe(user, token)
  // },
  loadVideos (context, { username, subId }) {
    if (state.videos[subId]) {
      return
    }
    return videos(username, subId)
      .then((response) => {
        context.commit('setVideos', { subId: subId, video: response.data })
      })
  },
  loadSearchResult (context, { keywords, token }) {
    return search(keywords, token)
      .then((response) => {
        context.commit('setSearchSesult', { searchResult: response.data })
      })
  },
  login (context, userData) {
    context.commit('setUserData', { userData })
    return authenticate(userData)
      .then(response => {
        context.commit('setTokens', { tokens: response.data['tokens'] })
        var userData = {...context.state.userData, ...response.data['user']}
        context.commit('setUserData', { userData })
      })
      .catch(error => {
        console.log('Error Authenticating: ', error)
        EventBus.emit('failedAuthentication', error)
      })
  },
  switchFinishState (context, videoId, token) {
    return switchFinishState(videoId, token)
      .then((response) => {
        context.commit('setVideoFinishState', { video: response.data })
      })
  },
  logout (context) {
    context.commit('logout')
  }
}

const mutations = {
  setSubscriptions (state, payload) {
    state.subscriptions = payload.subscriptions
  },
  // addSubscription (state, payload) {
  //   state.subscriptions.push()
  // },
  setVideos (state, payload) {
    state.videos[payload.subId] = payload.video
  },
  setSearchSesult (state, payload) {
    state.searchResult = payload.searchResult
  },
  setTokens (state, payload) {
    state.tokens = payload.tokens
    window.localStorage.setItem('tokens', JSON.stringify(state.tokens))
  },
  setUserData (state, payload) {
    state.userData = payload.userData
    window.localStorage.setItem('userData', JSON.stringify(state.userData))
  },
  setVideoFinishState (state, payload) {
    state.videos.forEach(element => {
      if (payload.id === element.id) {
        element.finished = payload.video.finished
        return true
      }
    })
  },
  logout () {
    state.user = {}
    state.tokens = {}
  }
}

const getters = {
  isAuthenticated (state) {
    return isValidToken(state.tokens)
  }
}

const store = new Vuex.Store({
  state,
  actions,
  mutations,
  getters
})

export default store
