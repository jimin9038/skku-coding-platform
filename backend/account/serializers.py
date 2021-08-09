from django import forms

from utils.api import serializers

from .models import AdminType, ProblemPermission, User, UserProfile


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()


class UsernameOrEmailCheckSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)


class GoogleAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32)
    email = serializers.EmailField(max_length=64)
    major = serializers.CharField(max_length=128)
    captcha = serializers.CharField()


class EmailAuthSerializer(serializers.Serializer):
    token = serializers.CharField()


class GenerateUserSerializer(serializers.Serializer):
    prefix = serializers.CharField(max_length=16, allow_blank=True)
    suffix = serializers.CharField(max_length=16, allow_blank=True)
    number_from = serializers.IntegerField()
    number_to = serializers.IntegerField()


class ImportUserSeralizer(serializers.Serializer):
    users = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField(max_length=64)))


class UserAdminSerializer(serializers.ModelSerializer):
    real_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "major", "admin_type", "problem_permission", "real_name",
                  "create_time", "last_login", "is_disabled"]

    def get_real_name(self, obj):
        return obj.userprofile.real_name


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "major", "admin_type", "problem_permission",
                  "create_time", "last_login", "is_disabled"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    real_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.show_real_name = kwargs.pop("show_real_name", False)
        super(UserProfileSerializer, self).__init__(*args, **kwargs)

    def get_real_name(self, obj):
        return obj.real_name if self.show_real_name else None


class EditUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=32)
    real_name = serializers.CharField(max_length=32, allow_blank=True, allow_null=True)
    email = serializers.EmailField(max_length=64)
    major = serializers.CharField(max_length=128)
    admin_type = serializers.ChoiceField(choices=(AdminType.REGULAR_USER, AdminType.ADMIN, AdminType.SUPER_ADMIN))
    problem_permission = serializers.ChoiceField(choices=(ProblemPermission.NONE, ProblemPermission.OWN,
                                                          ProblemPermission.ALL))
    is_disabled = serializers.BooleanField()


class EditUserSettingSerializer(serializers.Serializer):
    major = serializers.CharField(max_length=128)


class EditUserProfileSerializer(serializers.Serializer):
    real_name = serializers.CharField(max_length=32, allow_null=True, required=False)
    avatar = serializers.CharField(max_length=256, allow_blank=True, required=False)
    language = serializers.CharField(max_length=32, allow_blank=True, required=False)


class SSOSerializer(serializers.Serializer):
    token = serializers.CharField()


class ImageUploadForm(forms.Form):
    image = forms.FileField()


class FileUploadForm(forms.Form):
    file = forms.FileField()
