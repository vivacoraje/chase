import Vue from 'vue'

export const EventBus = new Vue()

export function isValidToken (tokens) {
  const timestamp = new Date(tokens.timestamp)
  const now = new Date()
  return (now - timestamp) < tokens.expiration
}
