<template>
  <div>
    <div class="logo">
      <div class="logo-img">
        <img src="@/assets/logos/logo.svg" alt=""/>
      </div>
      <div class="logo-title font-bold">
        <h4>SKKU</h4>
        <h4>Coding Platform</h4>
      </div>
    </div>
    <b-form @on-enter="handleLogin" ref="formLogin" :model="formLogin" class="font-bold">
      <b-container fluid="xl">
        <b-row class="mb-4">
          <b-form-input v-model="formLogin.username" placeholder="Student ID" @keydown.enter.native="handleLogin" />
        </b-row>
        <b-row class="mb-4">
          <b-form-input type="password" v-model="formLogin.password" placeholder="Password" @keydown.enter.native="handleLogin" />
        </b-row>
        <b-button data-loading-text="a" class="sign-btn" @click="handleLogin" variant="outline">
          <b-spinner v-if="btnLoginLoading" small></b-spinner> Sign In
        </b-button>
      </b-container>
    </b-form>
    <div class="google-login">
      <GoogleLogin
        class="google-login-button"
        :params="params"
        :onSuccess="googleLoginSuccess"
        :onFailure="googleLoginFail"
      >
        <span class="google-login-img">
          <img src="@/assets/g-logo.png" style="width:20px; height:auto;" alt=""/>
        </span>
        <span class="google-login-text">
          Google로 계속하기
        </span>
      </GoogleLogin>
    </div>
    <div class="modal-low mt-5 font-bold">
      <a v-if="website.allow_register" @click.stop="handleBtnClick('register')" style="float:left;">Register now</a>
      <a @click.stop="handleBtnClick('ApplyResetPassword')" style="float: right;">Forgot Password</a>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import api from '@oj/api'
import { FormMixin } from '@oj/components/mixins'
import { GoogleLogin } from 'vue-google-login'

export default {
  mixins: [FormMixin],
  data () {
    return {
      btnLoginLoading: false,
      formLogin: {
        username: '',
        password: ''
      },
      params: {
        client_id: '53826768076-36libfj7ft2vuh9mu2i78fj6d3t2d6mg.apps.googleusercontent.com'
      }
    }
  },
  components: {
    GoogleLogin
  },
  methods: {
    ...mapActions(['changeModalStatus', 'getProfile']),
    handleBtnClick (mode) {
      this.changeModalStatus({
        mode,
        visible: true
      })
    },
    async handleLogin () {
      this.btnLoginLoading = true
      const formData = Object.assign({}, this.formLogin)
      try {
        await api.login(formData)
        this.btnLoginLoading = false
        this.changeModalStatus({ visible: false })
        this.getProfile()
        this.$success('Welcome back!')
      } catch (err) {
        this.btnLoginLoading = false
      }
    },
    googleLoginSuccess (googleUser) {
      console.log(googleUser)
    },
    googleLoginFail () {
      console.log('fail')
    }
  },
  computed: {
    ...mapGetters(['website', 'modalStatus']),
    visible: {
      get () {
        return this.modalStatus.visible
      },
      set (value) {
        this.changeModalStatus({ visible: value })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  @font-face {
    font-family: Manrope_bold;
    src: url('../../../../fonts/Manrope-Bold.ttf');
  }
  .logo-img {
    display:block;
    width:116px;
    height:136px;
    margin-left:auto;
    margin-right:auto;
    filter:invert(68%) sepia(59%) saturate(458%) hue-rotate(42deg) brightness(94%) contrast(88%);
  }
  .logo-title {
    margin:8px 0 28px 0;
    color: #8DC63F;
    text-align:center;
  }
  .sign-btn {
    width:284px;
    margin-left:18px;
  }
  .modal-low {
    color:#808080;
    font-size:14px;
  }
  .font-bold {
    font-family: manrope_bold;
  }
  .logo-img {
    display:block;
    width:116px;
    height:136px;
    margin-left:auto;
    margin-right:auto;
    filter:invert(68%) sepia(59%) saturate(458%) hue-rotate(42deg) brightness(94%) contrast(88%);
  }
  .logo-title {
    margin:8px 0 28px 0;
    color: #8DC63F;
    text-align:center;
  }
  .sign-btn {
    width:284px;
    margin-left:18px;
  }
  .modal-low {
    color:#808080;
    font-size:14px;
  }
  .font-bold {
    font-family: manrope_bold;
  }
  .google-login {
    margin-left:10px;
  }
  .google-login-button {
    width:280px;
    height:40px;
    background:#FFFFFF;
    margin:10px 25px 0 25px;
    border-radius:4px;
    border:thin solid #808080;
  }
  .google-login-img {
    margin-right:10px;
  }
  .google-login-text {
    font-size:15px;
    font-weight:600;
  }
</style>
