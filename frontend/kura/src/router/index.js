import Vue from 'vue'
import Router from 'vue-router'
import Search from '@/components/Search'
import Home from '@/components/Home'
import Mine from '@/components/Mine'
import Video from '@/components/Video'
import Login from '@/components/Login'
import Register from '@/components/Register'

Vue.use(Router)

var routes = [
  {
    path: '/',
    name: 'search',
    component: Search
  },
  {
    path: '/home',
    name: 'home',
    component: Home
  },
  {
    path: '/subscription/mine',
    name: 'mine',
    component: Mine,
    meta: {
      required: true
    }
  },
  {
    path: '/subscription/videos/:subId',
    name: 'videos',
    component: Video
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/register',
    name: 'register',
    component: Register
  }
]

export default new Router({ routes })
