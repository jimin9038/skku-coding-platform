import time

from unittest import mock
from datetime import timedelta
from copy import deepcopy

from django.contrib import auth
from django.utils.timezone import now

from utils.api.tests import APIClient, APITestCase
from utils.shortcuts import rand_str
from options.options import SysOptions

from .models import AdminType, ProblemPermission, User


class PermissionDecoratorTest(APITestCase):
    def setUp(self):
        self.regular_user = User.objects.create(username="regular_user")
        self.admin = User.objects.create(username="admin")
        self.super_admin = User.objects.create(username="super_admin")
        self.request = mock.MagicMock()
        self.request.user.is_authenticated = mock.MagicMock()
        self.request.user.is_disabled = mock.MagicMock()
        self.request.user.has_email_auth = mock.MagicMock()

    def test_login_required(self):
        self.request.user.is_authenticated.return_value = False

    def test_disabled_account(self):
        self.request.user.is_authenticated.return_value = True
        self.request.user.is_disabled.return_value = True

    def test_admin_required(self):
        pass

    def test_super_admin_required(self):
        pass


class DuplicateUserCheckAPITest(APITestCase):
    def setUp(self):
        user = self.create_user("2020123456", "test123", login=False)
        user.email = "test@skku.edu"
        user.save()
        self.url = self.reverse("check_username_or_email")

    def test_duplicate_username(self):
        resp = self.client.post(self.url, data={"username": "2020123456"})
        self.assertEqual(resp.data["data"]["username"], 1)

    def test_ok_username(self):
        resp = self.client.post(self.url, data={"username": "2020987654"})
        data = resp.data["data"]
        self.assertFalse(data["username"])

    def test_duplicate_email(self):
        resp = self.client.post(self.url, data={"email": "test@skku.edu"})
        self.assertEqual(resp.data["data"]["email"], 1)
        resp = self.client.post(self.url, data={"email": "Test@Skku.edu"})
        self.assertEqual(resp.data["data"]["email"], 1)

    def test_ok_email(self):
        resp = self.client.post(self.url, data={"email": "aa@skku.edu"})
        self.assertFalse(resp.data["data"]["email"])


class WrongFormatUserCheckAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("check_username_or_email")

    def test_wrong_format_username(self):
        resp = self.client.post(self.url, data={"username": "202012345"})
        data = resp.data["data"]
        self.assertEqual(data["username"], 2)
        resp = self.client.post(self.url, data={"username": "20201234567"})
        data = resp.data["data"]
        self.assertEqual(data["username"], 2)
        resp = self.client.post(self.url, data={"username": "2020hahaha"})
        data = resp.data["data"]
        self.assertEqual(data["username"], 2)
        resp = self.client.post(self.url, data={"username": "1234567890"})
        data = resp.data["data"]
        self.assertEqual(data["username"], 2)

    def test_not_university_email(self):
        resp = self.client.post(self.url, data={"email": "hello@gmail.com"})
        self.assertEqual(resp.data["data"]["email"], 2)


class UserLoginAPITest(APITestCase):
    def setUp(self):
        self.username = self.password = "2020222000"
        self.user = self.create_user(username=self.username, password=self.password, login=False)
        self.login_url = self.reverse("user_login_api")

    def test_login_with_correct_info(self):
        response = self.client.post(self.login_url,
                                    data={"username": self.username, "password": self.password})
        self.assertDictEqual(response.data, {"error": None, "data": "Succeeded"})

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_login_and_add_number(self):
        response = self.client.post(self.login_url,
                                    data={"username": self.username, "password": self.password})
        self.assertDictEqual(response.data, {"error": None, "data": "Succeeded"})

        user = auth.get_user(self.client)
        user.userprofile.add_score(100, 200)
        user.userprofile.add_submission_number()
        user.userprofile.add_accepted_problem_number()
        self.assertTrue(user.is_authenticated)

    def test_login_with_correct_info_upper_username(self):
        resp = self.client.post(self.login_url, data={"username": self.username.upper(), "password": self.password})
        self.assertDictEqual(resp.data, {"error": None, "data": "Succeeded"})
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_login_with_wrong_info(self):
        response = self.client.post(self.login_url,
                                    data={"username": self.username, "password": "invalid_password"})
        self.assertDictEqual(response.data, {"error": "error", "data": "Invalid username or password"})

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_user_disabled(self):
        self.user.is_disabled = True
        self.user.save()
        resp = self.client.post(self.login_url, data={"username": self.username,
                                                      "password": self.password})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Your account has been disabled"})

    def test_user_without_email_auth(self):
        self.user.has_email_auth = False
        self.user.save()
        resp = self.client.post(self.login_url, data={"username": self.username,
                                                      "password": self.password})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Your need to authenticate your email"})


class CaptchaTest(APITestCase):
    def _set_captcha(self, session):
        captcha = rand_str(4)
        session["_django_captcha_key"] = captcha
        session["_django_captcha_expires_time"] = int(time.time()) + 30
        session.save()
        return captcha


class UserRegisterAPITest(CaptchaTest):
    def setUp(self):
        self.client = APIClient()
        self.register_url = self.reverse("user_register_api")
        self.captcha = rand_str(4)

        self.data = {"username": "2020111111", "password": "testuserpassword",
                     "real_name": "real_name", "email": "test@skku.edu",
                     "major": "Computer Science (컴퓨터공학과)",
                     "captcha": self._set_captcha(self.client.session)}

    def test_website_config_limit(self):
        SysOptions.allow_register = False
        resp = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Register function has been disabled by admin"})

    def test_invalid_captcha(self):
        self.data["captcha"] = "****"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "Invalid captcha"})

        self.data.pop("captcha")
        response = self.client.post(self.register_url, data=self.data)
        self.assertTrue(response.data["error"] is not None)

    @mock.patch("account.views.oj.send_email_async.send")
    def test_register_with_correct_info(self, mock):
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": None, "data": "Succeeded"})
        mock.assert_called()

    def test_username_already_exists(self):
        self.test_register_with_correct_info()
        self.data["captcha"] = self._set_captcha(self.client.session)
        self.data["email"] = "test1@skku.edu"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "Username already exists"})

    def test_email_already_exists(self):
        self.test_register_with_correct_info()
        self.data["captcha"] = self._set_captcha(self.client.session)
        self.data["username"] = "2020111222"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "Email already exists"})

    def test_not_student_id(self):
        self.test_register_with_correct_info()
        self.data["captcha"] = self._set_captcha(self.client.session)
        self.data["username"] = "19980331"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "Not student ID"})

    def test_invalid_domain(self):
        self.test_register_with_correct_info()
        self.data["captcha"] = self._set_captcha(self.client.session)
        self.data["username"] = "2020111223"
        self.data["email"] = "19980331@gmail.com"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "Invalid domain (Use skku.edu or g.skku.edu)"})


class UserProfileAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("user_profile_api")

    def test_get_profile_without_login(self):
        resp = self.client.get(self.url)
        self.assertDictEqual(resp.data, {"error": None, "data": None})

    def test_get_profile_without_user(self):
        self.create_user("2020222000", "test123")
        data = {"username": "19980331"}
        resp = self.client.get(self.url, data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "User does not exist"})

    def test_get_profile(self):
        self.create_user("2020222000", "test123")
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_get_profile_with_username(self):
        self.create_user("2020222000", "test123")
        data = {"username": "2020222000"}
        resp = self.client.get(self.url, data)
        self.assertSuccess(resp)

    def test_update_profile(self):
        self.create_user("2020222000", "test123")
        update_data = {"real_name": "zemal", "submission_number": 233, "language": "en-US"}
        resp = self.client.put(self.url, data=update_data)
        self.assertSuccess(resp)
        data = resp.data["data"]
        self.assertEqual(data["real_name"], "zemal")
        self.assertEqual(data["submission_number"], 0)
        self.assertEqual(data["language"], "en-US")


@mock.patch("account.views.oj.send_email_async.send")
class ApplyResetPasswordAPITest(CaptchaTest):
    def setUp(self):
        self.username = self.password = "2020222000"
        self.user = self.create_user(username=self.username, password=self.password, login=False)
        self.user.email = "test@g.skku.edu"
        self.user.save()
        self.url = self.reverse("apply_reset_password_api")
        self.login_url = self.reverse("user_login_api")
        self.data = {"email": "test@g.skku.edu", "captcha": self._set_captcha(self.client.session)}

    def _refresh_captcha(self):
        self.data["captcha"] = self._set_captcha(self.client.session)

    def test_apply_reset_password(self, send_email_send):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        send_email_send.assert_called()

    def test_apply_reset_password_with_authentication(self, send_email_send):
        response = self.client.post(self.login_url,
                                    data={"username": self.username, "password": self.password})
        self.assertDictEqual(response.data, {"error": None, "data": "Succeeded"})
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "You have already logged in, are you kidding me? "})

    def test_apply_reset_password_twice_in_20_mins(self, send_email_send):
        self.test_apply_reset_password()
        send_email_send.reset_mock()
        self._refresh_captcha()
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "You can only reset password once per 20 minutes"})
        send_email_send.assert_not_called()

    def test_apply_reset_password_again_after_20_mins(self, send_email_send):
        self.test_apply_reset_password()
        self.user.reset_password_token_expire_time = now() - timedelta(minutes=21)
        self.user.save()
        self._refresh_captcha()
        self.test_apply_reset_password()

    def test_invalid_captcha(self, send_email_send):
        self.data["captcha"] = "invalid"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Invalid captcha"})

    def test_user_does_not_exist(self, send_email_send):
        self.data["email"] = "19980331@gmail.com"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "User does not exist"})


class ResetPasswordAPITest(CaptchaTest):
    def setUp(self):
        self.create_user("2020222000", "test123", login=False)
        self.url = self.reverse("reset_password_api")
        user = User.objects.first()
        user.reset_password_token = "online_judge?"
        user.reset_password_token_expire_time = now() + timedelta(minutes=20)
        user.save()
        self.data = {"token": user.reset_password_token,
                     "captcha": self._set_captcha(self.client.session),
                     "password": "test456"}

    def test_reset_password_with_correct_token(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        self.assertTrue(self.client.login(username="2020222000", password="test456"))

    def test_reset_password_with_invalid_token(self):
        self.data["token"] = "aaaaaaaaaaa"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Token does not exist"})

    def test_reset_password_with_expired_token(self):
        user = User.objects.first()
        user.reset_password_token_expire_time = now() - timedelta(seconds=30)
        user.save()
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Token has expired"})

    def test_invalid_captcha(self):
        self.data["captcha"] = "invalid"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Invalid captcha"})


class UserChangeEmailAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("user_change_email_api")
        self.user = self.create_user("2020222000", "test123")
        self.new_mail = "test@skku.edu"
        self.data = {"password": "test123", "new_email": self.new_mail}

    def test_change_email_success(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)

    def test_wrong_password(self):
        self.data["password"] = "aaaa"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Wrong password"})

    def test_duplicate_email(self):
        u = self.create_user("aa", "bb", login=False)
        u.email = self.new_mail
        u.save()
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "The email is owned by other account"})

    def test_invalid_domain(self):
        self.data["new_email"] = "19980331@gmail.com"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Invalid domain (Use skku.edu or g.skku.edu)"})


class UserChangePasswordAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("user_change_password_api")

        # Create user at first
        self.username = "2020222000"
        self.old_password = "testuserpassword"
        self.new_password = "new_password"
        self.login_url = self.reverse("user_login_api")
        self.user = self.create_user(username=self.username, password=self.old_password, login=False)

        self.data = {"old_password": self.old_password, "new_password": self.new_password}

    def test_login_required(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.data, {"error": "permission-denied", "data": "Please login first"})

    def test_disabled_account(self):
        self.user.is_disabled = True
        self.user.save()
        self.assertTrue(self.client.login(username=self.username, password=self.old_password))
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.data, {"error": "permission-denied", "data": "Your account is disabled"})

    def test_valid_old_password(self):
        self.assertTrue(self.client.login(username=self.username, password=self.old_password))
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.data, {"error": None, "data": "Succeeded"})
        self.assertTrue(self.client.login(username=self.username, password=self.new_password))

    def test_invalid_old_password(self):
        self.assertTrue(self.client.login(username=self.username, password=self.old_password))
        self.data["old_password"] = "invalid"
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.data, {"error": "error", "data": "Invalid old password"})


class ProfileProblemDisplayIDRefreshAPITest(APITestCase):
    def setUp(self):
        pass


class AdminUserTest(APITestCase):
    def setUp(self):
        self.user = self.create_super_admin(login=True)
        self.username = self.password = "2015135790"
        self.new_username = "2016135790"
        self.regular_user = self.create_user(username=self.username, password=self.password, login=False)
        self.url = self.reverse("user_admin_api")
        self.data = {"id": self.regular_user.id, "username": self.new_username, "real_name": "test_name",
                     "email": "example@skku.edu", "major": "Computer Science (컴퓨터공학과)",
                     "admin_type": AdminType.REGULAR_USER, "problem_permission": ProblemPermission.OWN,
                     "is_disabled": False}

    def test_user_list(self):
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def test_user_list_with_id(self):
        self.data = {"id": self.regular_user.id}
        response = self.client.get(self.url, data=self.data)
        self.assertSuccess(response)

    def test_get_user_fail(self):
        self.data = {"id": "19980331"}
        resp = self.client.get(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "User does not exist"})

    def test_get_user(self):
        self.data = {"keyword": self.regular_user.username}
        response = self.client.get(self.url, data=self.data)
        self.assertSuccess(response)

    def test_edit_user_successfully(self):
        response = self.client.put(self.url, data=self.data)
        self.assertSuccess(response)
        resp_data = response.data["data"]
        self.assertEqual(resp_data["username"], self.new_username)
        self.assertEqual(resp_data["email"], "example@skku.edu")
        self.assertEqual(resp_data["major"], "Computer Science (컴퓨터공학과)")
        self.assertEqual(resp_data["is_disabled"], False)
        self.assertEqual(resp_data["problem_permission"], ProblemPermission.NONE)

    def test_edit_user_does_not_exist(self):
        self.data["id"] = "19980331"
        resp = self.client.put(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "User does not exist"})

    def test_edit_user_duplicated_username(self):
        self.create_user(username=self.new_username, password=self.password, login=False)
        resp = self.client.put(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Username already exists"})

    def test_edit_user_duplicated_email(self):
        self.duplicated_user = self.create_user(username="2015135791", password=self.password, login=False)
        self.duplicated_user.email = "example@skku.edu"
        self.duplicated_user.save()
        self.user.login = True
        self.user.save()
        resp = self.client.put(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Email already exists"})

    def test_edit_user_admin_successfully(self):
        self.data["admin_type"] = AdminType.ADMIN
        response = self.client.put(self.url, data=self.data)
        self.assertSuccess(response)
        resp_data = response.data["data"]
        self.assertEqual(resp_data["username"], self.new_username)
        self.assertEqual(resp_data["email"], "example@skku.edu")
        self.assertEqual(resp_data["major"], "Computer Science (컴퓨터공학과)")
        self.assertEqual(resp_data["is_disabled"], False)
        self.assertEqual(resp_data["problem_permission"], ProblemPermission.OWN)

    def test_edit_user_super_admin_successfully(self):
        self.data["admin_type"] = AdminType.SUPER_ADMIN
        response = self.client.put(self.url, data=self.data)
        self.assertSuccess(response)
        resp_data = response.data["data"]
        self.assertEqual(resp_data["username"], self.new_username)
        self.assertEqual(resp_data["email"], "example@skku.edu")
        self.assertEqual(resp_data["major"], "Computer Science (컴퓨터공학과)")
        self.assertEqual(resp_data["is_disabled"], False)
        self.assertEqual(resp_data["problem_permission"], ProblemPermission.ALL)

    def test_admin_role_required_middleware(self):
        self.duplicated_user = self.create_user(username="2015135791", password=self.password, login=True)
        resp = self.client.put(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "login-required", "data": "Please login in first"})

    def test_edit_user_password(self):
        data = self.data
        new_password = "testpassword"
        data["password"] = new_password
        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)
        user = User.objects.get(id=self.regular_user.id)
        self.assertFalse(user.check_password(self.password))
        self.assertTrue(user.check_password(new_password))

    def test_import_users(self):
        data = {"users": [["user1", "pass1", "eami1@skku.edu"],
                          ["user2", "pass3", "eamil3@skku.edu"]]
                }
        resp = self.client.post(self.url, data)
        self.assertSuccess(resp)
        # successfully created 2 users
        self.assertEqual(User.objects.all().count(), 4)

    def test_import_users_failed(self):
        data = {"users": [["user1", "pass1", "eami1@skku.edu"],
                          ["user2", "eamil3@skku.edu"]]
                }
        resp = self.client.post(self.url, data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Error occurred while processing data '['user2', 'eamil3@skku.edu']'"})

    def test_import_duplicate_user(self):
        data = {"users": [["user1", "pass1", "eami1@skku.edu"],
                          ["user1", "pass1", "eami1@skku.edu"]]
                }
        resp = self.client.post(self.url, data)
        self.assertFailed(resp, "DETAIL:  Key (username)=(user1) already exists.")
        # no user is created
        self.assertEqual(User.objects.all().count(), 2)

    def test_delete_users(self):
        self.test_import_users()
        user_ids = User.objects.filter(username__in=["user1", "user2"]).values_list("id", flat=True)
        user_ids = ",".join([str(id) for id in user_ids])
        resp = self.client.delete(self.url + "?id=" + user_ids)
        self.assertSuccess(resp)
        self.assertEqual(User.objects.all().count(), 2)

    def test_delete_users_without_id(self):
        self.test_import_users()
        resp = self.client.delete(self.url)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Invalid Parameter, id is required"})

    def test_delete_users_fail(self):
        self.test_import_users()
        resp = self.client.delete(self.url + "?id=" + str(self.user.id))
        self.assertDictEqual(resp.data, {"error": "error", "data": "Current user can not be deleted"})


class GenerateUserAPITest(APITestCase):
    def setUp(self):
        self.create_super_admin()
        self.url = self.reverse("generate_user_api")
        self.data = {
            "number_from": 100, "number_to": 105,
            "prefix": "pre", "suffix": "suf",
            "default_email": "test@test.com",
            "password_length": 8
        }
        self.password = "teset123"

    @mock.patch("account.views.admin.xlsxwriter.Workbook")
    def test_download_users_success(self, mock_workbook):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        mock_workbook.assert_called()
        # resp = self.client.get(self.url, data={mock_workbook.get_id()})
        # self.assertEqual(resp.data["data"], f"U  {mock_workbook.get_id()}")

    def test_error_case(self):
        data = deepcopy(self.data)
        data["prefix"] = "t" * 16
        data["suffix"] = "s" * 14
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.data["data"], "Username should not more than 32 characters")

        data2 = deepcopy(self.data)
        data2["number_from"] = 106
        resp = self.client.post(self.url, data=data2)
        self.assertEqual(resp.data["data"], "Start number must be lower than end number")

    @mock.patch("account.views.admin.xlsxwriter.Workbook")
    def test_generate_user_success(self, mock_workbook):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        mock_workbook.assert_called()

    def test_generate_user_fail(self):
        self.duplicated_user = self.create_user(username="pre101suf", password=self.password, login=False)
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "DETAIL:  Key (username)=(pre101suf) already exists."})


class UserSettingAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("user_setting_api")
        self.login_url = self.reverse("user_login_api")
        self.username = "2020222000"
        self.password = "test123"

    def test_change_major_success(self):
        self.create_user(self.username, self.password)
        data = {"major": "software"}
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)
        data = resp.data["data"]
        self.assertEqual(data["major"], "software")

    def test_get_user_information_without_user(self):
        self.create_user(self.username, self.password)
        data = {"username": "19980331"}
        resp = self.client.get(self.url, data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "User does not exist"})

    def test_get_user_information(self):
        self.create_user(self.username, self.password)
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_get_user_information_with_username(self):
        self.create_user(self.username, self.password)
        data = {"username": "2020222000"}
        resp = self.client.get(self.url, data)
        self.assertSuccess(resp)

    def test_user_setting_without_authentication(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)


class UserLogoutAPITest(APITestCase):
    def setUp(self):
        self.username = self.password = "2020222000"
        self.user = self.create_user(username=self.username, password=self.password, login=True)
        self.url = self.reverse("user_logout_api")

    def test_logout(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)


class EmailAuthAPITest(APITestCase):
    def setUp(self):
        self.username = self.password = "2020222000"
        self.user = self.create_user(username=self.username, password=self.password, login=True)
        self.url = self.reverse("email_auth_api")
        self.user.email_auth_token = "testtoken"
        self.user.save()

    def test_email_auth_success(self):
        resp = self.client.post(self.url, data={"token": "testtoken"})
        self.assertSuccess(resp)

    def test_email_auth_fail(self):
        resp = self.client.post(self.url, data={"token": "failtoken"})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Token does not exist"})
