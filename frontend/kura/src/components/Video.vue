<template>
  <div>
    <a-divider orientation="left">{{video.title}}</a-divider>
    <a-table v-if="video.videos.download.length !== 0" size="small" :columns="columns" :dataSource="video.videos.download">
      <a-tag slot="address" slot-scope="address">
        <a class="address" target="_blank" :href="address">{{address}}</a>
      </a-tag>
      <span slot="tag" slot-scope="tag">
        <a-tag v-if="tag" color="blue">Yes</a-tag>
        <a-tag v-else color="orange">No</a-tag>
      </span>
      <span slot="action" slot-scope="record">
        <a-button @click="switchFinished(record)" icon="swap" type="primary"></a-button>
      </span>
      <template slot="title" slot-scope="">
        下载地址
      </template>
    </a-table>
    <a-table v-if="video.videos.play.length !== 0" size="small" :columns="columns" :dataSource="video.videos.play">
      <a-tag slot="address" slot-scope="address">
        <a class="address" :href="address" target="_blank">{{address}}</a>
      </a-tag>
      <span slot="tag" slot-scope="tag">
        <a-tag v-if="tag" color="blue">Yes</a-tag>
        <a-tag v-else color="orange">No</a-tag>
      </span>
      <span slot="action" slot-scope="record">
        <a-button @click="switchFinished(record)" icon="swap" type="primary"></a-button>
      </span>
      <template slot="title" slot-scope="">
        在线播放
      </template>
    </a-table>
  </div>
</template>
<script>
import { switchFinishState } from '../api'
const columns = [{
  dataIndex: 'title',
  key: 'title',
  title: '集序'
}, {
  title: '地址',
  dataIndex: 'address',
  key: 'address',
  scopedSlots: { customRender: 'address' }
}, {
  title: '已观看',
  key: 'tags',
  dataIndex: 'finished',
  scopedSlots: { customRender: 'tag' }
}, {
  title: 'Action',
  key: 'action',
  scopedSlots: { customRender: 'action' }
}]

export default {
  data () {
    return {
      columns,
      video: {}
    }
  },
  computed: {
    isAuthenticated () {
      return this.$store.getters.isAuthenticated
    },
    userData () {
      return this.$store.state.userData
    }
  },
  // beforeMount () {
  //   if (this.isAuthenticated) {
  //     this.$store.dispatch('loadVideos', { username: this.$store.state.userData.username, subId: this.$route.params.subId })
  //   }
  // },
  created () {
    if (this.isAuthenticated) {
      this.$store.dispatch('loadVideos', { username: this.$store.state.userData.username, subId: this.$route.params.subId })
    }
    this.video = this.$store.state.videos[this.$route.params.subId]
  },
  methods: {
    switchFinished (video) {
      if (this.isAuthenticated) {
        switchFinishState(
          video.id,
          this.$store.state.userData.username,
          this.$store.state.tokens.token)
          .then(response => {
            video.finished = response.data.finished
          })
      }
    }
  }
}
</script>
<style>
  a.address {
    width: 300px;
    overflow: hidden;
    display: block;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
