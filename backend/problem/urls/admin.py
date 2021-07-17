from django.urls import path

from ..views.admin import (ContestProblemAPI, ProblemAPI, TestCaseAPI, MakeContestProblemPublicAPIView,
                           CompileSPJAPI, AddContestProblemAPI, TestCaseTextAPI)

urlpatterns = [
    path("test_case/", TestCaseAPI.as_view(), name="test_case_api"),
    path("compile_spj/", CompileSPJAPI.as_view(), name="compile_spj"),
    path("problem/", ProblemAPI.as_view(), name="problem_admin_api"),
    path("contest/problem/", ContestProblemAPI.as_view(), name="contest_problem_admin_api"),
    path("contest_problem/make_public/", MakeContestProblemPublicAPIView.as_view(), name="make_public_api"),
    path("contest/add_problem_from_public/", AddContestProblemAPI.as_view(), name="add_contest_problem_from_public_api"),
    path("testcase_text/", TestCaseTextAPI.as_view(), name="testcase_text_api")
]
