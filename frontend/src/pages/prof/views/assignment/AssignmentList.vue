<template>
  <div>
    <b-card title="Assignments">
      <div class="table">
        <b-table
          hover
          :items="assignmentlist"
          :fields="assignmentfield"
        >
          <b-icon icon="caret-right-fill" aria-hidden="true"></b-icon>
          <b-form-checkbox switch size="sm"></b-form-checkbox>
          <b-icon icon="pencil" aria-hidden="true"></b-icon>
          <b-icon icon="box-arrow-in-down" aria-hidden="true"></b-icon>
          <b-icon icon="trash" aria-hidden="true"></b-icon>
        </b-table>
      </div>
      <div v-if="!assignmentlist.length">
        No Assignment
      </div>
    </b-card>
  </div>
</template>

<script>

export default {
  name: 'AssignmentList',
  components: {
    // Split into many components
  },
  data () {
    return {
      assignmentfield: ['Title', 'Visible', 'Status', 'Operation'],
      assignmentlist: [
      ]
    }
  },
  async mounted () {
  },
  methods: {
  },
  computed: {
  }
}
</script>

<style lang="scss">

</style>
