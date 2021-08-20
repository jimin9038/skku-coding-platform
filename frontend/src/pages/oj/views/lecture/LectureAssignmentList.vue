<template>
  <div>
    <Sidemenu/>
    <article class="lecture-assignment-card">
      <div class="top-bar mb-4">
        <h2 class="title">Lecture Assignments</h2>
      </div>
      <div class="table">
        <b-table
          hover
          :items="assignments"
          :fields="assignmentListFields"
          head-variant="light"
          class="table"
          @row-clicked="goAssignment"
        >
          <template #cell(title)="data">
            {{ data.item.title }}
          </template>
          <template #cell(start_time))="data">
            {{ data.item.start_time }}
          </template>
          <template #cell(end_time)="data">
            {{ data.item.end_time }}
          </template>
          <template #cell(status)="data">
            <b-icon
              icon="circle-fill"
              scale="0.7"
              :style="'color:' + data.item.statuscolor"
            >
            </b-icon>
            <!-- getter이용해서 status 불러오기 -->
            {{ data.item.status }}
          </template>
          <template #cell(submission)="data">
            <b-icon
              icon="circle-fill"
              scale="0.7"
              :style="'color:' + data.item.submissioncolor"
            >
            </b-icon>
            {{ data.item.submission }}
          </template>
        </b-table>
      </div>
    </article>
  </div>
</template>

<script>
import Sidemenu from '@oj/components/Sidemenu.vue'

export default {
  name: 'LectureAssignmentList',
  components: {
    Sidemenu
  },
  data () {
    return {
      assignmentListFields: [
        {
          key: 'title',
          label: 'Assignment'
        },
        'start_time',
        {
          key: 'end_time',
          label: 'Due'
        },
        'status',
        'submission'
      ],
      assignments: [
        // 날짜 역순 정렬
        {
          id: '3',
          title: 'Assignment 3',
          start_time: '2021.08.05',
          end_time: '2021.08.06',
          status: 'Not Started',
          statuscolor: '#D75B66',
          submission: 'Not Submitted',
          submissioncolor: '#D75B66'
        },
        {
          id: '2',
          title: 'Assignment 2',
          start_time: '2021.08.08',
          end_time: '2021.08.09',
          status: 'Underway',
          statuscolor: '#8DC63F',
          submission: '4/5 Submitted',
          submissioncolor: '#FEB144'
        },
        {
          id: '1',
          title: 'Assignment 1',
          start_time: '2021.08.05',
          end_time: '2021.08.06',
          status: 'Ended',
          statuscolor: '#D75B66',
          submission: '5/5 Submitted',
          submissioncolor: '#8DC63F'
        }
      ],
      assignment: ''
    }
  },
  async mounted () {
  },
  methods: {
    async goAssignment (assignment) {
      this.assignment = assignment
      this.listVisible = false
      await this.$router.push({ name: 'lecture-assignment-detail', params: { assignmentID: assignment.id } })
    }
  },
  computed: {
  }
}
</script>

<style lang="scss" scoped>
  @font-face {
    font-family: Manrope_bold;
    src: url('../../../../fonts/Manrope-Bold.ttf');
  }
  .title{
    color: #7C7A7B;
  }
  .top-bar {
    margin-top: 40px;
    margin-left: 68px;
  }
  .lecture-assignment-card{
    margin: 0 auto;
    width: 70%;
    font-family: Manrope_bold;
    .table{
      width: 95% !important;
      margin: 0 auto;
    }
  }
  .course-info{
    display: flex;
    justify-content: space-between;
    width: 90%;
    margin-left: 40px;
    font-size: 12px;
  }
  .course-info-title{
    padding-left: 20px;
    color: #4f4f4f;
  }
  .course-info-menu{
    display: flex;
  }
</style>
