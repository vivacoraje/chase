<template>
  <a-layout id="components-layout-demo-side" style="min-height: 100vh;">
    <a-layout-sider
      collapsible
      v-model="collapsed"
      theme="dark"
    >
      <div class="logo">
        <!-- <a-avatar style="left: 8px" src="http://clipartjapan.com/wp-content/uploads/sakura2.svg" /> -->
      </div>
      <a-menu theme="dark" :defaultSelectedKeys="['1']" mode="inline">
        <a-menu-item key="2">
          <a-icon type="search"></a-icon>
          <span>Search</span>
          <router-link to="/"></router-link>
        </a-menu-item>
        <a-sub-menu
          key="sub1"
        >
          <span slot="title"><a-icon type="star" /><span>Subscription</span></span>
          <a-menu-item key="3">
            <router-link to="/subscription/mine"><a-icon type="smile" />Mine</router-link>
          </a-menu-item>
          <!-- <a-menu-item key="4">
            <router-link to="/subscription/popluar"><a-icon type="fire"/>Popular</router-link>
          </a-menu-item> -->
        </a-sub-menu>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="header" style="background: #fff; padding: 0">
        <router-link v-if="!isAuthenticated" to="/login">Login</router-link>
        <!-- <router-link v-else to="">Logout</router-link> -->
        <a-avatar v-if="isAuthenticated" style="left: 92%;" :src="userData.avatar" />
      </a-layout-header>
      <a-layout-content style="margin: 16px">
        <div :style="{ padding: '24px', background: '#fff', minHeight: '582px' }">
          <router-view></router-view>
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>
<script>
export default {
  data () {
    return {
      collapsed: false
    }
  },
  computed: {
    isAuthenticated () {
      return this.$store.getters.isAuthenticated
    },
    userData () {
      return this.$store.state.userData
    }
  }
}
</script>

<style>

#components-layout-demo-side .logo {
  height: 32px;
  background: #FBEAEB;
  margin: 16px;
}
  /* .header {
    background-color: #0E7DE9;
    color: #fff;
    line-height: 60px;
  }
  a:hover {
    color: #0E7DE9;
  }
  a:active {
    color: #ffffff;
  }
  a:link {
    color: red;
  } */
</style>
