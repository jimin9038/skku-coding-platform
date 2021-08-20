<template>
  <div>
    <Sidemenu/>
    <article class="lecture-assignment-card">
      <section class="top-bar mb-4">
        <div class="assignment-title">{{ assignment.title }}</div>
        <div class="assignment-info">
          {{ assignment.start_time + '~' + assignment.end_time }}
          <b-badge class="due">- 3:00:00</b-badge>
        </div>
      </section>
      <section class="assignment-container">
        <p class="assignment__content">
          {{ assignment.content }}
        </p>
        <div class="table">
          <b-table
            hover
            :items="assignmentProblemList"
            :fields="assignmentProblemListFields"
            head-variant="light"
            class="table"
          >
            <template #cell(title)="data">
              {{ data.item.title }}
            </template>
          </b-table>
        </div>
      </section>
    </article>
  </div>
</template>

<script>
import Sidemenu from '@oj/components/Sidemenu.vue'

export default {
  name: 'LectureAssignmentDetail',
  components: {
    Sidemenu
  },
  data () {
    return {
      assignment: {
        title: 'Assignment1',
        content: 'If true, KaTeX will throw a ParseError when it encounters an unsupported command or invalid LaTeX. If false, KaTeX will render unsupported commands as text, and render invalid LaTeX as its source code with hover text giving the error, in the color given by errorColor. If true, KaTeX will throw a ParseError when it encounters an unsupported command or invalid LaTeX. If false, KaTeX will render unsupported commands as text, and render invalid LaTeX as its source code with hover text giving the error, in the color given by errorColor.',
        start_time: '2021.08.05 09:00',
        end_time: '2021.08.06 23:59',
        status: 'Not Start',
        statuscolor: '#D75B66',
        submission: 'Not Submitted',
        submissioncolor: '#D75B66'
      },
      assignmentProblemListFields: [
        {
          key: 'displayID',
          label: '#'
        },
        'type',
        'title',
        'score'
      ],
      assignmentProblemList: [
        // 날짜 역순 정렬
        {
          displayID: '1',
          type: 'Problem',
          title: '가파른 경사',
          score: '60/100'
        },
        {
          displayID: '2',
          type: 'Problem',
          title: '습격자 호루라기',
          score: '100/100'
        },
        {
          displayID: '3',
          type: 'Problem',
          title: '두번째 JMT',
          score: '60/100'
        }
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

<style lang="scss" scoped>
  @font-face {
    font-family: Manrope_bold;
    src: url('../../../../fonts/Manrope-Bold.ttf');
  }
  .lecture-assignment-card{
    margin: 0 auto;
    width: 70%;
    font-family: Manrope_bold;
    .assignment__content{
      width: 90%;
      margin: 0 auto 20px;
      height: 150px;
      border-radius: 10px;
      background-color: #EDECEC;
      padding: 25px;
      overflow: auto;
    }
    .table{
      width: 95% !important;
      margin: 0 auto;
    }
  }
  .top-bar {
    margin-top: 40px;
    margin-left: 68px;
    & .assignment-title {
      margin-bottom: 10px;
      font-size: 36px;
      color: #7C7A7B;
    }
    & .assignment-info {
      width: 90%;
      display:flex;
      justify-content: space-between;
      font-size: 12px;
      color: #7C7A7B;
      margin: auto 0;
      .due {
        font-weight: 400;
        padding: 5px 10px;
        font-size: 14px;
        background-color: #E9A05A !important;
      }
    }
  }
</style>
