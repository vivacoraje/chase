<template>
  <a-list
    itemLayout="vertical"
    size="small"
    :pagination="pagination"
    :dataSource="listData"
  >
    <a-list-item slot="renderItem" slot-scope="item" key="item.title">
      <template slot="actions" v-for="{type, text, theme, style, link, spin} in item.actions">
        <span :key="type">
          <a-icon :spin="spin" :theme="theme" :type="type" :style="style" />
          <a :href="link" target="_blank">{{text}}</a>

        </span>
      </template>
      <img slot="extra" width="55%" alt="logo" :src="item.imgSrc" />
      <a-list-item-meta
        :description="item.description"
      >
        <router-link slot="title" :to="item.href">{{item.title}}</router-link>
      </a-list-item-meta>
      {{item.content}}
    </a-list-item>
  </a-list>
</template>
<script>

export default {
  data () {
    return {
      listData: [],
      subscriptions: [],
      pagination: {
        onChange: (page) => {
          console.log(page)
        },
        pageSize: 3
      }
    }
  },
  beforeMount () {
    if (this.isAuthenticated) {
      this.$store.dispatch('loadSubscriptions', { username: this.$store.state.userData.username })
    }
  },
  mounted () {
    this.loadSubscriptions()
  },
  computed: {
    isAuthenticated () {
      return this.$store.getters.isAuthenticated
    },
    userData () {
      return this.$store.state.userData
    }
  },
  methods: {
    makeActions (aSubs) {
      var actions = [
        { type: 'star', text: `${aSubs.user_count}`, theme: 'filled', style: 'margin-right: 8px; color: orange' }
      ]
      var syncAct
      if (aSubs.ended) {
        syncAct = { type: 'sync', spin: false, style: 'margin-right: 8px; color: blue' }
      } else {
        syncAct = { type: 'sync', spin: true, style: 'margin-right: 8px; color: green' }
      }
      actions.push(syncAct)
      actions.push(
        { type: 'link', text: 'douban', link: `${aSubs.refes.douban}`, style: 'margin-right: 8px; color: green' },
        { type: 'link', text: 'imdb', link: `${aSubs.refes.imdb}`, style: 'margin-right: 8px; color: green' }
      )
      return actions
    },
    loadSubscriptions () {
      var subs = this.$store.state.subscriptions
      for (var i in subs) {
        var s = subs[`${i}`]
        var description = `首播: ${s.episode_aired} 集数: ${s.episode_count}`
        this.listData.push({
          title: s.title,
          href: `/subscription/videos/${s.id}`,
          description: description,
          content: s.synopsis,
          imgSrc: s.poster,
          actions: this.makeActions(s)
        })
      }
    }
  }
}
</script>
<style>

</style>
