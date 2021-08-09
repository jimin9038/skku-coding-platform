import os
import re
import requests
from datetime import timedelta

from django.conf import settings
from django.contrib import auth
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from json.decoder import JSONDecodeError
from django.http import JsonResponse
from rest_framework import status

from options.options import SysOptions
from utils.api import APIView, validate_serializer
from utils.captcha import Captcha
from utils.shortcuts import rand_str
from ..decorators import login_required
from ..models import User, UserProfile
from ..serializers import (UserLoginSerializer, GoogleAuthSerializer,
                           UserRegisterSerializer, EmailAuthSerializer, UsernameOrEmailCheckSerializer,
                           UserChangeEmailSerializer)
from ..serializers import (UserProfileSerializer,
                           EditUserProfileSerializer, ImageUploadForm, EditUserSettingSerializer, UserSerializer)
from ..tasks import send_email_async


class UserProfileAPI(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="username",
                in_=openapi.IN_QUERY,
                description="Specific user profile with `username`",
                type=openapi.TYPE_STRING,
            ),
        ],
        opearation_description="Get user information if logged in",
        responses={200: UserProfileSerializer},
    )
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, **kwargs):
        """
        Determine whether to log in, and return user information if logged in
        """
        user = request.user
        if not user.is_authenticated:
            return self.success()
        show_real_name = False
        username = request.GET.get("username")
        try:
            if username:
                user = User.objects.get(username=username, is_disabled=False)
            else:
                user = request.user
                # The api returns your own information, you can return real_name
                show_real_name = True
        except User.DoesNotExist:
            return self.error("User does not exist")
        return self.success(UserProfileSerializer(user.userprofile, show_real_name=show_real_name).data)

    @swagger_auto_schema(
        request_body=EditUserProfileSerializer,
        description="Update user profile",
        responses={200: UserProfileSerializer},
    )
    @validate_serializer(EditUserProfileSerializer)
    @login_required
    def put(self, request):
        data = request.data
        user_profile = request.user.userprofile
        for k, v in data.items():
            setattr(user_profile, k, v)
        user_profile.save()
        return self.success(UserProfileSerializer(user_profile, show_real_name=True).data)


class UserSettingAPI(APIView):
    @validate_serializer(EditUserSettingSerializer)
    @login_required
    def put(self, request):
        data = request.data
        user = request.user
        setattr(user, "major", data["major"])
        user.save()
        return self.success(UserSerializer(user).data)

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, **kwargs):
        """
        Determine whether to log in, and return user information if logged in
        """
        user = request.user
        if not user.is_authenticated:
            return self.success()
        username = request.GET.get("username")
        try:
            if username:
                user = User.objects.get(username=username, is_disabled=False)
            else:
                user = request.user
                # The api returns your own information, you can return real_name
        except User.DoesNotExist:
            return self.error("User does not exist")
        return self.success(UserSerializer(user).data)


class AvatarUploadAPI(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                required=True,
                type=openapi.TYPE_FILE,
            ),
        ],
    )
    @login_required
    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            avatar = form.cleaned_data["image"]
        else:
            return self.error("Invalid file content")
        if avatar.size > 2 * 1024 * 1024:
            return self.error("Picture is too large")
        suffix = os.path.splitext(avatar.name)[-1].lower()
        if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
            return self.error("Unsupported file format")

        name = rand_str(10) + suffix
        with open(os.path.join(settings.AVATAR_UPLOAD_DIR, name), "wb") as img:
            for chunk in avatar:
                img.write(chunk)
        user_profile = request.user.userprofile

        user_profile.avatar = f"{settings.AVATAR_URI_PREFIX}/{name}"
        user_profile.save()
        return self.success("Succeeded")


class UserLoginAPI(APIView):
    @swagger_auto_schema(request_body=UserLoginSerializer)
    @validate_serializer(UserLoginSerializer)
    def post(self, request):
        """
        User login api
        """
        data = request.data
        user = auth.authenticate(username=data["username"])
        # None is returned if username or password is wrong
        if not user:
            return self.error("Invalid username or password")
        if user.is_disabled:
            return self.error("Your account has been disabled")
        if not user.has_email_auth:
            return self.error("Your need to authenticate your email")
        auth.login(request, user)
        return self.success("Succeeded")


class UserLogoutAPI(APIView):
    def get(self, request):
        auth.logout(request)
        return self.success()


class UsernameOrEmailCheck(APIView):
    @swagger_auto_schema(
        request_body=UsernameOrEmailCheckSerializer,
        description="Check if username or email is valid and not duplicate.\n0 means valid, 1 means duplicate, 2 means invlalid student ID or university email.",
    )
    @validate_serializer(UsernameOrEmailCheckSerializer)
    def post(self, request):
        data = request.data
        # 1 means already exist.
        # 2 means not student ID / university email
        result = {
            "username": 0,
            "email": 0
        }
        if data.get("username"):
            if User.objects.filter(username=data["username"].lower()).exists():
                result["username"] = 1
            elif not re.match(r"^20[0-9]{8}$", data["username"]):
                result["username"] = 2
        if data.get("email"):
            if User.objects.filter(email=data["email"].lower()).exists():
                result["email"] = 1
            elif data["email"].split("@")[1] not in ("g.skku.edu", "skku.edu"):
                result["email"] = 2
        return self.success(result)


class GoogleAuthAPI(APIView):
    @swagger_auto_schema(request_body=GoogleAuthSerializer)
    @validate_serializer(GoogleAuthSerializer)
    def post(self, request):
        data = request.data
        access_token = data["access_token"]
        email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
        email_req_status = email_req.status_code

        if email_req_status != 200:
            return self.error("Failed to get email(400 BAD REQUEST)")
        email_req_json = email_req.json()
        email = email_req_json.get('email')

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return self.error("User does not exist")
        if user.has_email_auth == True:
            return self.success(email) 
        else:
            return self.error("User needs email authorization")


class UserRegisterAPI(APIView):
    @swagger_auto_schema(request_body=UserRegisterSerializer)
    @validate_serializer(UserRegisterSerializer)
    def post(self, request):
        """
        User register api
        """
        if not SysOptions.allow_register:
            return self.error("Register function has been disabled by admin")         

        data = request.data
        data["username"] = data["username"].lower()
        data["email"] = data["email"].lower()

        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error("Invalid captcha")
        if User.objects.filter(username=data["username"]).exists():
            return self.error("Username already exists")
        if data["email"].split("@")[1] in ["g.skku.edu", "skku.edu"]:
            if not re.match(r"^20[0-9]{8}$", data["username"]):
                return self.error("Not student ID")
        if User.objects.filter(email=data["email"]).exists():
            return self.error("Email already exists")
        
        user = User.objects.create(username=data["username"], email=data["email"], major=data["major"])
        user.school = data["email"].split("@")[1].split(".")[0].upper();
        user.has_email_auth = False
        user.email_auth_token = rand_str()
        user.save()
        UserProfile.objects.create(user=user)

        render_data = {
            "username": user.username,
            "website_name": SysOptions.website_name,
            "link": f"{SysOptions.website_base_url}/email-auth/{user.email_auth_token}"
        }
        email_html = render_to_string("email_auth.html", render_data)
        send_email_async.send(from_name=SysOptions.website_name_shortcut,
                              to_email=user.email,
                              to_name=user.username,
                              subject="Email Authentication",
                              content=email_html)

        return self.success("Succeeded")


class EmailAuthAPI(APIView):
    @swagger_auto_schema(
        request_body=EmailAuthSerializer,
        operation_description="Authorize user with url sent to email",
    )
    @validate_serializer(EmailAuthSerializer)
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(email_auth_token=data["token"])
        except User.DoesNotExist:
            return self.error("Token does not exist")
        user.email_auth_token = None
        user.has_email_auth = True
        user.save()
        return self.success("Succeeded")
