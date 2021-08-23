import copy
from datetime import datetime, timedelta

from django.utils import timezone

from utils.api.tests import APITestCase
from utils.constants import ContestStatus

from .models import ContestAnnouncement, ContestRuleType, Contest

DEFAULT_CONTEST_DATA = {"title": "test title", "description": "test description",
                        "start_time": timezone.localtime(timezone.now()),
                        "end_time": timezone.localtime(timezone.now()) + timedelta(days=1),
                        "rule_type": ContestRuleType.ACM,
                        "password": "123",
                        "allowed_ip_ranges": [],
                        "visible": True, "real_time_rank": False}


class ContestAdminAPITest(APITestCase):
    def setUp(self):
        self.create_admin()
        self.url = self.reverse("contest_admin_api")
        self.data = copy.deepcopy(DEFAULT_CONTEST_DATA)

    def test_create_contest(self):
        response = self.client.post(self.url, data=self.data)
        self.assertSuccess(response)
        return response

    def test_create_contest_time_error(self):
        self.data["end_time"] = self.data["start_time"] - timedelta(days=1)
        response = self.client.post(self.url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "Start time must occur earlier than end time"})

    def test_create_contest_without_password(self):
        self.data["password"] = ""
        response = self.client.post(self.url, data=self.data)
        self.assertSuccess(response)

    def test_create_contest_with_invalid_cidr(self):
        self.data["allowed_ip_ranges"] = ["127.0.0"]
        resp = self.client.post(self.url, data=self.data)
        self.assertTrue(resp.data["data"].endswith("is not a valid cidr network"))

    def test_update_contest(self):
        id = self.test_create_contest().data["data"]["id"]
        update_data = {"id": id, "title": "update title",
                       "description": "update description",
                       "password": "12345",
                       "visible": False, "real_time_rank": False}
        data = copy.deepcopy(self.data)
        data.update(update_data)
        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)
        response_data = response.data["data"]
        for k in data.keys():
            if isinstance(data[k], datetime):
                continue
            self.assertEqual(response_data[k], data[k])

    def test_update_contest_no_contest(self):
        self.data["id"] = "19980331"
        resp = self.client.put(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Contest does not exist"})

    def test_update_contest_time_error(self):
        id = self.test_create_contest().data["data"]["id"]
        self.data["id"] = id
        self.data["start_time"] = timezone.localtime(timezone.now())
        self.data["end_time"] = self.data["start_time"] - timedelta(days=3)
        response = self.client.put(self.url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "Start time must occur earlier than end time"})

    def test_update_contest_without_password(self):
        id = self.test_create_contest().data["data"]["id"]
        self.data["id"] = id
        self.data["password"] = ""
        response = self.client.put(self.url, data=self.data)
        self.assertSuccess(response)

    def test_update_contest_with_invalid_cidr(self):
        id = self.test_create_contest().data["data"]["id"]
        self.data["id"] = id
        self.data["allowed_ip_ranges"] = ["127.0.0"]
        resp = self.client.put(self.url, data=self.data)
        self.assertFailed(resp)

    def test_update_contest_real_time(self):
        id = self.test_create_contest().data["data"]["id"]
        update_data = {"id": id, "title": "update title",
                       "description": "update description",
                       "password": "12345",
                       "visible": False, "real_time_rank": False}
        data = copy.deepcopy(self.data)
        data.update(update_data)
        self.data["id"] = id
        self.data["real_time_rank"] = True
        response = self.client.put(self.url, data=self.data)
        self.assertSuccess(response)

    def test_get_contests(self):
        self.test_create_contest()
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def test_get_one_contest(self):
        id = self.test_create_contest().data["data"]["id"]
        response = self.client.get("{}?id={}".format(self.url, id))
        self.assertSuccess(response)

    def test_get_one_contest_no_contest(self):
        id = self.test_create_contest().data["data"]["id"]
        resp = self.client.get("{}?id={}".format(self.url, id+123))
        self.assertDictEqual(resp.data, {"error": "error", "data": "Contest does not exist"})

    def test_get_one_contest_admin(self):
        id = self.test_create_contest().data["data"]["id"]
        response = self.client.get("{}?id={}".format(self.url, id))
        self.assertSuccess(response)

    def test_get_one_contest_keyword(self):
        response = self.client.get(self.url + "?keyword=" + "key")
        self.assertSuccess(response)


class ContestAPITest(APITestCase):
    def setUp(self):
        user = self.create_super_admin()
        self.contest = Contest.objects.create(created_by=user, **DEFAULT_CONTEST_DATA)

    def test_get_contest_list(self):
        url = self.reverse("contest_list_api")
        response = self.client.get(url + "?limit=10")
        self.assertSuccess(response)
        self.assertEqual(len(response.data["data"]["results"]), 1)

    def test_get_contest_list_keyword(self):
        url = self.reverse("contest_list_api")
        response = self.client.get(url + "?keyword=" + "key")
        self.assertSuccess(response)
        self.assertEqual(len(response.data["data"]["results"]), 0)

    def test_get_contest_list_rule_type(self):
        url = self.reverse("contest_list_api")
        response = self.client.get(url + "?rule_type=" + "rule")
        self.assertSuccess(response)
        self.assertEqual(len(response.data["data"]["results"]), 0)

    def test_get_contest_list_status_not_start(self):
        url = self.reverse("contest_list_api")
        response = self.client.get(url + "?status=" + ContestStatus.CONTEST_NOT_START)
        self.assertSuccess(response)
        self.assertEqual(len(response.data["data"]["results"]), 0)

    def test_get_contest_list_status_ended(self):
        url = self.reverse("contest_list_api")
        response = self.client.get(url + "?status=" + ContestStatus.CONTEST_ENDED)
        self.assertSuccess(response)
        self.assertEqual(len(response.data["data"]["results"]), 0)

    def test_get_contest_list_status_else(self):
        url = self.reverse("contest_list_api")
        response = self.client.get(url + "?status=" + "else")
        self.assertSuccess(response)
        self.assertEqual(len(response.data["data"]["results"]), 1)

    def test_get_one_contest(self):
        self.url = self.reverse("contest_api") + "?id=" + str(self.contest.id)
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_get_one_contest_without_id(self):
        self.url = self.reverse("contest_api")
        resp = self.client.get(self.url)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Invalid parameter, id is required"})

    def test_get_one_contest_fail(self):
        self.url = self.reverse("contest_api") + "?id=" + "19980331"
        resp = self.client.get(self.url)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Contest does not exist"})

    def test_regular_user_validate_contest_password(self):
        self.create_user("test", "test123")
        url = self.reverse("contest_password_api")
        resp = self.client.post(url, {"contest_id": self.contest.id, "password": "error_password"})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Wrong password or password expired"})

        resp = self.client.post(url, {"contest_id": self.contest.id, "password": DEFAULT_CONTEST_DATA["password"]})
        self.assertSuccess(resp)

    def test_regular_user_validate_contest_password_fail(self):
        self.create_user("test", "test123")
        url = self.reverse("contest_password_api")
        resp = self.client.post(url, {"contest_id": "19980331", "password": "error_password"})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Contest does not exist"})

    def test_regular_user_access_contest(self):
        self.create_user("test", "test123")
        url = self.reverse("contest_access_api")
        resp = self.client.get(url + "?contest_id=" + str(self.contest.id))
        self.assertFalse(resp.data["data"]["access"])

        password_url = self.reverse("contest_password_api")
        resp = self.client.post(password_url,
                                {"contest_id": self.contest.id, "password": DEFAULT_CONTEST_DATA["password"]})
        self.assertSuccess(resp)
        self.url = self.reverse("contest_api") + "?id=" + str(self.contest.id)
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_regular_user_access_contest_without_contest_id(self):
        self.create_user("test", "test123")
        url = self.reverse("contest_access_api")
        resp = self.client.get(url)
        self.assertFailed(resp)

    def test_regular_user_access_contest_fail(self):
        self.create_user("test", "test123")
        url = self.reverse("contest_access_api")
        resp = self.client.get(url + "?contest_id=" + "19980331")
        self.assertDictEqual(resp.data, {"error": "error", "data": "Contest does not exist"})

    def test_delete_contest_success(self):
        url = self.reverse("contest_admin_api")
        response = self.client.delete("{}?id={}".format(url, self.contest.id))
        self.assertSuccess(response)

    def test_delete_contest_no_id(self):
        url = self.reverse("contest_admin_api")
        response = self.client.delete("{}?password={}".format(url, "19980331"))
        self.assertDictEqual(response.data, {"error": "error", "data": "Invalid parameter, id is required"})

    def test_delete_contest_no_contest(self):
        url = self.reverse("contest_admin_api")
        response = self.client.delete("{}?id={}".format(url, "19980331"))
        self.assertDictEqual(response.data, {"error": "error", "data": "Contest does not exists"})


class ContestAnnouncementAdminAPITest(APITestCase):
    def setUp(self):
        self.url = self.reverse("contest_announcement_admin_api")

    def create_contest(self):
        url = self.reverse("contest_admin_api")
        data = DEFAULT_CONTEST_DATA
        return self.client.post(url, data=data)

    def test_create_contest_announcement(self):
        self.create_admin()
        self.contest_id = self.create_contest().data["data"]["id"]
        self.data = {"title": "test title", "content": "test content", "contest_id": self.contest_id, "visible": True}
        response = self.client.post(self.url, data=self.data)
        self.assertSuccess(response)
        return response

    def test_create_contest_announcement_no_contest(self):
        self.create_admin()
        self.contest_id = self.create_contest().data["data"]["id"]
        self.data = {"title": "test title", "content": "test content", "contest_id": self.contest_id, "visible": True}
        self.data["contest_id"] = "19980331"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Contest does not exist"})

    def test_edit_contest_announcement_success(self):
        id = self.test_create_contest_announcement().data["data"]["id"]
        update_data = {"id": id, "title": "update title",
                       "content": "update content",
                       "contest_id": self.contest_id, "visible": True}
        data = copy.deepcopy(self.data)
        data.update(update_data)
        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)

    def test_edit_contest_announcement_no_announcement(self):
        self.create_admin()
        self.contest_id = self.create_contest().data["data"]["id"]
        self.data = {"title": "test title", "content": "test content", "contest_id": self.contest_id, "visible": True}
        id = "19980331"
        update_data = {"id": id, "title": "update title",
                       "content": "update content",
                       "contest_id": self.contest_id, "visible": True}
        data = copy.deepcopy(self.data)
        data.update(update_data)
        resp = self.client.put(self.url, data=data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Contest announcement does not exist"})

    def test_delete_contest_announcement(self):
        id = self.test_create_contest_announcement().data["data"]["id"]
        response = self.client.delete("{}?id={}".format(self.url, id))
        self.assertSuccess(response)
        self.assertFalse(ContestAnnouncement.objects.filter(id=id).exists())

    def test_delete_contest_announcement_not_admin(self):
        self.create_super_admin()
        self.contest_id = self.create_contest().data["data"]["id"]
        self.data = {"title": "test title", "content": "test content", "contest_id": self.contest_id, "visible": True}
        response = self.client.post(self.url, data=self.data)
        self.assertSuccess(response)
        id = response.data["data"]["id"]
        response = self.client.delete("{}?id={}".format(self.url, id))
        self.assertSuccess(response)

    def test_get_contest_announcements(self):
        self.test_create_contest_announcement()
        response = self.client.get(self.url + "?contest_id=" + str(self.data["contest_id"]))
        self.assertSuccess(response)

    def test_get_one_contest_announcement(self):
        id = self.test_create_contest_announcement().data["data"]["id"]
        resp = self.client.get("{}?id={}".format(self.url, id))
        self.assertSuccess(resp)


class ContestAnnouncementListAPITest(APITestCase):
    def setUp(self):
        self.create_admin()
        self.url = self.reverse("contest_announcement_api")

    def create_contest_announcements(self):
        contest_id = self.client.post(self.reverse("contest_admin_api"), data=DEFAULT_CONTEST_DATA).data["data"]["id"]
        url = self.reverse("contest_announcement_admin_api")
        self.client.post(url, data={"title": "test title1", "content": "test content1", "contest_id": contest_id})
        self.client.post(url, data={"title": "test title2", "content": "test content2", "contest_id": contest_id})
        return contest_id

    def test_get_contest_announcement_list(self):
        contest_id = self.create_contest_announcements()
        response = self.client.get(self.url, data={"contest_id": contest_id})
        self.assertSuccess(response)

    def test_get_contest_announcement_list_keyword(self):
        contest_id = self.create_contest_announcements()
        response = self.client.get(self.url + "?keyword=key", data={"contest_id": contest_id, "keyword": "key"})
        self.assertSuccess(response)

    def test_get_contest_announcement_list_fail(self):
        response = self.client.get(self.url, data={})
        self.assertDictEqual(response.data, {"error": "error", "data": "Parameter error, contest_id is required"})

    def test_get_contest_announcement_list_no_contest_announcement(self):
        contest_id = self.client.post(self.reverse("contest_admin_api"), data=DEFAULT_CONTEST_DATA).data["data"]["id"]
        response = self.client.get(self.url, data={"id": "8791916165298", "contest_id": contest_id})
        self.assertSuccess(response)

    def test_get_contest_announcement_list_max_id(self):
        contest_id = self.create_contest_announcements()
        response = self.client.get(self.url, data={"max_id": 1000, "contest_id": contest_id})
        self.assertSuccess(response)
