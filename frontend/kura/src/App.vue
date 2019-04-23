<template>
  <div id="app">
    <basiclayout></basiclayout>
  </div>
</template>

<script>
import BasicLayout from '@/components/BasicLayout'

export default {
  name: 'App',
  components: {
    basiclayout: BasicLayout
  },
  created () {
    if (localStorage.getItem('userData')) {
      this.$store.state.userData = JSON.parse(localStorage.getItem('userData'))
    }
    if (localStorage.getItem('tokens')) {
      this.$store.state.tokens = JSON.parse(localStorage.getItem('tokens'))
    }
    window.addEventListener('beforeunload', () => {
      localStorage.setItem('userData', JSON.stringify(this.$store.state.userData))
      localStorage.setItem('tokens', JSON.stringify(this.$store.state.tokens))
    })
  }
}
</script>

<style>
  .header {
    background-color: #0E7DE9;
    color: #fff;
    line-height: 60px;
  }
</style>
