<template>
  <b-list-group class="prof_vertical_menu" v-show="sideMenuShow">
    <div class="logo">
      <img
        src="@/assets/logos/logo.png"
        style="height=35px; width=auto;"
        alt="oj admin"
      >
    </div>
    <div class="put-in">
      My Lecture
      <b-button :v-model="asdf" class="put-in-button" variant="white" @click="lectureGroup()">
        <b-icon icon="chevron-double-left"/>
      </b-button>
      {{asdf}}
    </div>
    <b-list-group-item to="/">
      <b-button :pressed.sync="press" class="put-in-button" variant="white">
        <b-icon :icon="press ? 'chevron-down' : 'chevron-right'"/>
      </b-button>
      Dashboard {{press}}
      {{lecture_term}}  {{lectures}}
    </b-list-group-item>

    <div v-for="(term,index) in lecture_term" :key="index" >
      {{term.semester}}
      <div v-for="(lecture,index) in lectures" :key="index">
        {{term.year}} {{lecture.title}} {{lecture.registered_year}} {{term.semester}} {{lecture.semester}}
        <!-- <div v-if="term.year === lecture.registered_year && term.semester === lecture.semester"> -->
          {{lecture.course_code}} {{semester_name[lecture.semester]}}
          <b-collapse id="lecture" role="tab">
            <b-list-group-item
              class="list-group-subitem"
              v-b-toggle.lecture_group
            >
              <b-icon :icon="detailsShowing ? 'chevron-down' : 'chevron-right'"/>
              {{term.year}} {{semester_name[term.semester]}}
            </b-list-group-item>
          </b-collapse>

          <b-collapse id="lecture_group" role="tab">
            <b-list-group-item
              class="list-group-subitem"
              v-b-toggle.inner
            >
              <b-icon icon="caret-down-fill" />
              {{lecture2.title}}_{{lecture2.course_code}}_{{lecture2.class_number}}
            </b-list-group-item>
          </b-collapse>

          <b-collapse id="inner" role="tabpanel">
            <b-list-group-item
              to="/lecture/1/dashboard"
              class="list-group-subitem"
            >
              Lecture Dashboard
            </b-list-group-item>
            <b-list-group-item
              to="/lecture/1/assignment"
              class="list-group-subitem"
            >
              Assignments
            </b-list-group-item>
            <b-list-group-item
              to="/lecture/1/qna"
              class="list-group-subitem"
            >
              QnA
            </b-list-group-item>
          </b-collapse>
        <!-- </div> -->
      </div>
<!--
      <b-collapse id="lecture_title">
        <b-list-group-item>
        </b-list-group-item`
        {{lecture.title}}
      </b-collapse>

      <div v-for="(lecture,id) of lecture_list" :key="id">
        <b-list-group-item
          class="list-group-subitem"
        >
          {{lecture}}
          <b-collapse>
            <b-list-group-item>
            </b-list-group-item>
          </b-collapse>
        </b-list-group-item>
      </div>
-->
    </div>
    <b-list-group-item href="#" role="tab" v-b-toggle.lecture_group>
      <b-icon
        icon="grid-fill"
        font-scale="1.25"
        style="margin-right: 8px"
      />
      Lecture
    </b-list-group-item>
  </b-list-group>
</template>

<script>
import { mapGetters } from 'vuex'
// import api from '../api.js'
export default {
  name: 'SideMenu',
  data () {
    return {
      currentPath: '',
      lecture_term: [],
      press: false,
      asdf: 'asdf',
      semester_name: ['Spring', 'Summer', 'Fall', 'Winter'],
      lectures: [{ 
        id: 1,
        title: '',
        course_code: '',
        class_number: 1,
        created_by: {
          id: 1,
          username: '',
          real_name: ''
        },
        registered_year: '',
        semester: 0
      }],
      lectureNumber: 1
    }
  },
  mounted () {
    this.currentPath = this.$route.path
    this.lectureGroup()
    // const res = api.getCourseList()
    // this.lectureNumber = res.data.data.lectureNumber
  },
  computed: {
    ...mapGetters(['user', 'isSuperAdmin', 'hasProblemPermission'])
  },
  methods: {
    putMenuInside () {
      this.sideMenuShow = false
    },
    lectureGroup () {
      // const apilectures = res.data.data.results
      const apilectures = [{ // 여기서 api 불러옴
        id: 1,
        title: 'Python Programming',
        course_code: 'GDBEASDF',
        class_number: 41,
        created_by: {
          id: 1,
          username: 'minchae',
          real_name: '고민채'
        },
        registered_year: '2021',
        semester: 0
      },
      {
        id: 2,
        title: '프로그래밍 기초와 실습',
        course_code: 'GDBEAPOI',
        class_number: 40,
        created_by: {
          id: 1,
          username: 'minchae',
          real_name: '고민채'
        },
        registered_year: '2020',
        semester: 1
      }]
      const registerTerm = []
      this.asdf = 'Change'
      apilectures.sort((a, b) => { return a.registered_year < b.registered_year })
      apilectures.sort((a, b) => {
        if (a.registered_year === b.registered_year) {
          return a.semester < b.semester
        } else { return 0 }
      })
      apilectures.sort((a, b) => { return a.title < b.title })
      apilectures.sort((a, b) => {
        if (a.title === b.title) {
          return a.class_number < b.class_number
        } else { return 0 }
      })

      apilectures.forEach(lecture => {
        if (!({ year: lecture.registered_year, semester: lecture.semester } in registerTerm)) {
          registerTerm.push({ year: lecture.registered_year, semester: lecture.semester })
        }
      })

      this.lectures = apilectures
      this.lecture_term = registerTerm
    }
  }
}
</script>

<style scoped lang="scss">
  #prof_vertical_menu {
    flex-grow: 1;
    flex-shrink: 1;
    width: 200px;
    min-width: 200px;
    resize: horizontal;
    height: 100%;
    z-index: 1;
    background-color: white;
    .logo {
      margin: 20px 0;
      text-align: center;
    }
    .put-in {
      display: flex;
      flex-direction: row;
      .put-in-text {
        flex: auto;
      }
      .put-in-button {
        width: 8px;
      }
    }
  }
  .list-group-subitem {
    padding: 16px 0px 16px 50px;
  }
</style>
