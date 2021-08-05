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
    <div class="google-login">
      <GoogleLogin
        class="google-login-button"
        :params="params"
        :onSuccess="googleLoginSuccess"
        :onFailure="googleLoginFail"
      >
        <span class="google-login-img">
          <img src="@/assets/g-logo.png"
            style="width:25px; height:auto; margin-bottom:3px;"
            alt="google login"
          />
        </span>
        <span class="google-login-text">
          Sign in with Google
        </span>
      </GoogleLogin>
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
    async googleLoginSuccess (googleUser) {
      const accessToken = googleUser.Zb.access_token
      try {
        await api.googleAuth(accessToken)
        // 구글 로그인 성공
        this.changeMadalStatus({ visible: false })
        this.$success('Welcome!')
      } catch (err) {
        // 구글 계정 에러 또는 회원가입 절차 진행
        if (err.data.data === 'User does not exist') {
          this.handleBtnClick('register')
        }
      }
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
  .google-login-button {
    width:300px;
    height:50px;
    background:#FFFFFF;
    margin:0 25px 15px 25px;
    border-radius:4px;
    border:thin solid #808080;
  }
  .google-login-img {
    margin-right:10px;
  }
  .google-login-text {
    font-size:18px;
    font-weight:600;
  }
</style>
