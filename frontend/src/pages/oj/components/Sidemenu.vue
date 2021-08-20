<template>
  <div class="Sidemenu">
    <b-card>
      <b-list-group class="menu-container">
        <b-list-group-item class="menu-item" to="/lecture/1">
          <b-icon class="icon" icon="calendar2-check"/>
          <p>Dashboard</p>
        </b-list-group-item>
        <b-list-group-item class="menu-item" to="/lecture/1/assignment">
          <b-icon class="icon" icon="journal-text"/>
          <p>Assignment</p>
        </b-list-group-item>
        <b-list-group-item class="menu-item" to="/lecture/1/question">
          <b-icon class="icon" icon="patch-question"/>
          <p>QnA</p>
        </b-list-group-item>
      </b-list-group>
    </b-card>
  </div>
</template>

<script>
export default {
  data () {
    return {
    }
  },
  methods: {
  }
}
</script>

<style lang="scss" scoped>
  .Sidemenu {
    position: fixed;
    top: 30%;
    right: 70px;
    & .card {
      box-shadow: none !important;
      height: 230px;
    }
    & .menu-item {
      padding: 5px;
    }
    & .icon {
      display: flex;
      justify-content: center;
      width: 30px;
      height: 30px;
      margin: 0 auto 5px auto;
    }
    & p {
      text-align: center;
      margin: 0;
    }
  }
</style>
