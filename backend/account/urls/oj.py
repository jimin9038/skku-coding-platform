from django.urls import path

from ..views.oj import (ApplyResetPasswordAPI, ResetPasswordAPI,
                        UserChangePasswordAPI, UserRegisterAPI, EmailAuthAPI, UserChangeEmailAPI,
                        UserLoginAPI, UserLogoutAPI, UsernameOrEmailCheck,
                        AvatarUploadAPI, UserProfileAPI, UserSettingAPI)

from utils.captcha.views import CaptchaAPIView

urlpatterns = [
    path("login/", UserLoginAPI.as_view(), name="user_login_api"),
    path("logout/", UserLogoutAPI.as_view(), name="user_logout_api"),
    path("register/", UserRegisterAPI.as_view(), name="user_register_api"),
    path("email_auth/", EmailAuthAPI.as_view(), name="email_auth_api"),
    path("change_password/", UserChangePasswordAPI.as_view(), name="user_change_password_api"),
    path("change_email/", UserChangeEmailAPI.as_view(), name="user_change_email_api"),
    path("apply_reset_password/", ApplyResetPasswordAPI.as_view(), name="apply_reset_password_api"),
    path("reset_password/", ResetPasswordAPI.as_view(), name="reset_password_api"),
    path("captcha/", CaptchaAPIView.as_view(), name="show_captcha"),
    path("check_username_or_email/", UsernameOrEmailCheck.as_view(), name="check_username_or_email"),
    path("profile/", UserProfileAPI.as_view(), name="user_profile_api"),
    path("user/", UserSettingAPI.as_view(), name="user_setting_api"),
    path("upload_avatar/", AvatarUploadAPI.as_view(), name="avatar_upload_api"),
]
