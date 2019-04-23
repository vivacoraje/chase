<template>
  <div align="center">
    <a-input-search style="width:400px;" placeholder="" @search="onSearch" enterButton size="large" />
    <br/>
    <br/>
    <a-list
      size="small"
      bordered
      :dataSource="subs"
      v-if="subs.length"
    >
      <a-list-item slot="renderItem" slot-scope="title" align="center">
        <p>{{title}}</p>
      </a-list-item>
      <div slot="header">已订阅</div>
    </a-list>
    <a-list
      size="small"
      bordered
      :dataSource="non"
      v-if="non.length"
    >
    <a-list-item slot="renderItem" slot-scope="site" align="center">
      <a :href="site.url">{{site.title}}</a>
      <a-button v-if="isAuthenticated" class="subscribe" type="primary" size="small" @click="subscribeS(site.url, site.title)">订阅</a-button>
    </a-list-item>
    <div slot="header">未订阅/在线播放</div>
  </a-list>
  </div>
</template>

<script>
import { search, subscribe } from '../api'

export default {
  data () {
    return {
      subs: [],
      non: []
    }
  },
  computed: {
    isAuthenticated () {
      return this.$store.getters.isAuthenticated
    },
    userData () {
      return this.$store.state.userData
    },
    tokens () {
      return this.$store.state.tokens
    }
  },
  methods: {
    onSearch (value) {
      search({
        title: value, email: this.$store.state.userData.email
      })
        .then(response => {
          this.subs = response.data.subs
          this.non = response.data.non
        })
    },
    subscribeS (url, title) {
      if (this.$store.getters.isAuthenticated) {
        subscribe(url, this.$store.state.tokens.token, this.$store.state.userData.username)
          .then(() => {
            var idx
            this.non.forEach((item, index) => {
              if (item.title === title) {
                idx = index
              }
            })
            this.non.pop(this.non.valueOf(idx))
            this.subs.push(title)
          })
      }
    }
  }
}
</script>
