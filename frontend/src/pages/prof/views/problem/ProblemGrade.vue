<template>
  <div class="grade">
    <p>{{lecture.title}}_{{lecture.class_number}}_{{lecture.course_code}}-Assignment{{lecture.assignment_id}}</p>
    <Panel :title="ProblemTitle">
      <b-table
        ref="table"
        :items="scoreList"
        :fields="field"
        :per-page="pageSize"
        :current-page="updateCurrentPage"
        style="width: 100%"
      >
        <template #cell(studentId)="row">
          {{row.item.student_id}}
        </template>

        <template #cell(name)="row">
          {{row.item.name}}
        </template>

        <template #head(file)="row">
          <span>
            {{row.label}}
            <icon-btn icon="download" varient="outline-light" @click.native="downloadAll()"/>
          </span>
        </template>

        <template #cell(file)="row">
          <div v-if="row.item.file">
            <b-button @click="download()">
              {{row.item.file}}
            </b-button>
          </div>
          <div v-if="!row.item.file">- </div>
        </template>

        <template #head(code)="row">
          <span>
            {{row.label}}
            <icon-btn icon="download" varient="outline-white" @click.native="download()"/>
          </span>
        </template>

        <template #cell(code)="row">
          <icon-btn :icon="row.item.code ? 'code' : 'dash'" @click.native="goCode(row.item.student_id)"/>
        </template>

        <template #cell(score)="row">
          <div v-if="newScore">
            {{newScore}} / {{row.item.total_score}}
          </div>
          <div v-if="!newScore">
            {{row.item.user_score ? row.item.user_score : '- '}} / {{row.item.total_score}}
          </div>
        </template>

        <b-button :pressed="press">
          <b-icon icon="pencil" />
          <div v-if="press">
            <b-form-input
              v-model="newScore"
            >
            {{newScore}} / {{row.item.total_score}}
            </b-form-input>
          </div>
        </b-button>
<!--
        <template #cell(visible)="row">
          <b-form-checkbox
            switch
            v-model="row.item.visible"
            @change="handleVisibleSwitch(row.item)"
          >
          </b-form-checkbox>
        </template>

        <template #cell(operation)="row">
          <div>
            <icon-btn
              name="Edit"
              icon="clipboard-plus"
              @click.native="goEdit(row.item.id)"
            />
          </div>
        </template>
      </b-table>
-->
      <div class="panel-options">
        <b-pagination
          v-model="currentPage"
          :per-page="pageSize"
          :total-rows="total"
          style="position: absolute; right: 20px; top: 15px;"
        />
      </div>
    </Panel>
  </div>
</template>

<script>
import IconBtn from '../../components/btn/IconBtn.vue'
// import api from '../api.js'
// import utils from '@/utils/utils'
export default {
  name: 'ProblemGrade',
  components: {
    IconBtn

  },
  data () {
    return {
      ProblemTitle: 'Assignmnet1 - A 가파른 경사',
      pageSize: 10,
      total: 1,
      currentPage: 0,
      press: false,
      newScore: false,
      field: [
        { key: 'studentId', label: 'Student ID' },
        { key: 'name', label: 'Name' },
        { key: 'file', label: 'File' },
        { key: 'code', label: 'Code' },
        { key: 'score', label: 'Score' }
      ],
      scoreList: [{
        student_id: 1,
        name: 'qwerqwer',
        file: '1234',
        user_score: 90,
        total_score: 100,
        code: true
      }],
      lecture: {
        title: 'Python Programming',
        course_code: 'GDBEASDF',
        class_number: 41,
        assignment_id: 1
      }
    }
  },
  mounted () {

  },
  methods: {
    downloads () {
    },
    downloadAll () {
      this.currentPage = 5
    },
    download () {
      // const url = `/prof/download_submissions?contest_id=${this.currentId}&exclude_admin=${excludeAdmin}`
      // utils.downloadFile(url)
      this.currentPage = 10
    },
    async goCode (id) {
      await this.$router.push({ name: 'announcement', params: { id } })
    }
  },
  computed: {
  }
}
</script>

<style lang="scss">

</style>
