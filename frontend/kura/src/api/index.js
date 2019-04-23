import axios from 'axios'

const API_URL = 'http://localhost:5000'

export function subscribe (url, token, username) {
  let a = axios.create({
    headers: { Authorization: `Bearer ${token}` }
  })
  return a.post(
    `${API_URL}/api/subscriptions/${username}`,
    { tv_url: url }
  )
}

export function subscriptions (username) {
  return axios.get(
    `${API_URL}/api/subscriptions/${username}`
  )
}

export function videos (username, subId) {
  return axios.get(
    `${API_URL}/api/videos/${username}/subs/${subId}`
  )
}

export function register (userData) {
  return axios.post(
    `${API_URL}/api/users`, userData
  )
}

export function authenticate (userData) {
  return axios.post(
    `${API_URL}/login`, userData
  )
}

export function search (keywords) {
  return axios.post(
    `${API_URL}/api/search`,
    keywords
  )
}

export function switchFinishState (videoId, username, token) {
  let a = axios.create({
    headers: { Authorization: `Bearer ${token}` }
  })
  return a.put(
    `${API_URL}/api/videos/${username}/${videoId}`
  )
}
