"""This module functions like a webhook， process messages for assembly and send to dingding", the file main function
is process_msg_to_dingding"""

import gc
import re
from dingtalkchatbot.chatbot import DingtalkChatbot
from jinja2 import PackageLoader, Environment
from api_class.test_case import CorrectTestApi, FailureTestApi
from config.constant import app_names, get_webhook_url
from logs import logger


def get_url_root(url):
    return "/".join(url.split("/")[:5])


def get_url(url):
    return "/" + "/".join(url.split("/")[5:])


def check_app_name(api_url):
    if api_url is None:
        return False
    for key, value in app_names.items():
        if key in api_url:
            return value


def check_app_and_count(test_apis, failure_flag=False):
    test_case_result = dict()
    orgskyeyeapi_v4_correct_case = list()
    navigatorapi_v1_correct_case = list()
    datavdashboardapi_v2_correct_case = list()
    datavorgdashboardapi_v2_correct_case = list()
    skyeyeapi_v3_correct_case = list()
    skyeyeapi_v2_correct_case = list()
    srvskyeyeapi_v1_correct_case = list()
    orgskyeyeapi_v1_correct_case = list()
    datavgraphapi_v2_correct_case = list()

    for test_api in test_apis:
        if test_api.app_name == "orgskyeyeapi_v4":
            orgskyeyeapi_v4_correct_case.append(test_api)
        elif test_api.app_name == "navigatorapi_v1":
            navigatorapi_v1_correct_case.append(test_api)
        elif test_api.app_name == "datavdashboardapi_v2":
            datavdashboardapi_v2_correct_case.append(test_api)
        elif test_api.app_name == "datavorgdashboardapi_v2":
            datavorgdashboardapi_v2_correct_case.append(test_api)
        elif test_api.app_name == "skyeyeapi_v3":
            skyeyeapi_v3_correct_case.append(test_api)
        elif test_api.app_name == "skyeyeapi_v2":
            skyeyeapi_v2_correct_case.append(test_api)
        elif test_api.app_name == "srvskyeyeapi_v1":
            srvskyeyeapi_v1_correct_case.append(test_api)
        elif test_api.app_name == "orgskyeyeapi_v1":
            orgskyeyeapi_v1_correct_case.append(test_api)
        elif test_api.app_name == "datavgraphapi_v2":
            datavgraphapi_v2_correct_case.append(test_api)
        else:  # XXX: maybe support other app
            pass

    del test_apis
    gc.collect()

    test_case_result.setdefault("orgskyeyeapi_v4", orgskyeyeapi_v4_correct_case)
    test_case_result.setdefault("navigatorapi_v1", navigatorapi_v1_correct_case)
    test_case_result.setdefault("datavdashboardapi_v2", datavdashboardapi_v2_correct_case)
    test_case_result.setdefault("datavorgdashboardapi_v2", datavorgdashboardapi_v2_correct_case)
    test_case_result.setdefault("skyeyeapi_v3", skyeyeapi_v3_correct_case)
    test_case_result.setdefault("skyeyeapi_v2", skyeyeapi_v2_correct_case)
    test_case_result.setdefault("srvskyeyeapi_v1", srvskyeyeapi_v1_correct_case)
    test_case_result.setdefault("orgskyeyeapi_v1", orgskyeyeapi_v1_correct_case)
    test_case_result.setdefault("datavgraphapi_v2", datavgraphapi_v2_correct_case)

    case_duration_top10 = dict()
    # Here is the code for Top Low 10
    # for app_name, app_case_list in test_case_result.items():
    #     if not failure_flag:
    #         # 求出每个app请求耗时的top10api
    #         case_duration_top10.setdefault(app_name, sorted(app_case_list, key=lambda case: case.time, reverse=True)[:10])
    # if failure_flag:
    #     return test_case_result
    # return test_case_result, case_duration_top10
    return test_case_result


def send_msg_to_dingding(url, msg, at_mobiles=None):
    if url and msg:
        try:
            dingding = DingtalkChatbot(url)
            response = dingding.send_text(msg=msg, at_mobiles=at_mobiles)
            if response.get("errcode") == 0 and response.get("errmsg") == "ok":
                logger.info("***** The message was sent successfully *****")
            else:
                logger.error("Error: %s" % response.get("errmsg"))
        except Exception as e:
            logger.error("Error: %s" % e)
    else:
        logger.error("webhook url and msg and at_mobiles can't be empty...")


def loader_jinja2():
    env = Environment(loader=PackageLoader("__main__", "templates"))
    return env.get_template("notice.txt")


def process_msg_to_dingding(all_test_results):
    all_correct_test_results = list()
    all_failure_test_results = list()
    for test_results in all_test_results:
        correct_api_list = test_results.get("correct", None)
        failure_api_list = test_results.get("failure", None)
        # Put all the correct test api data into the list for easy follow-up
        if correct_api_list:
            all_correct_test_results.extend(correct_api_list)
        if failure_api_list:
            all_failure_test_results.extend(failure_api_list)

    all_correct_test_apis = list()
    all_failure_test_apis = list()
    for correct_api in all_correct_test_results:
        all_correct_test_apis.append(CorrectTestApi(
            url_root=get_url_root(correct_api["url"]),
            url=get_url(correct_api["url"]),
            time=int(correct_api["duration"] * 1000),
            app_name=check_app_name(correct_api["url"])
        ))
    for failure_api in all_failure_test_results:
        all_failure_test_apis.append(FailureTestApi(
            url=get_url(failure_api["url"]),
            method=failure_api["method"],
            param=failure_api["param"],
            status_code=failure_api["status_code"],
            msg=failure_api.get("msg", None),
            validator_msg=failure_api.get("validator_msg", None),
            app_name=check_app_name(failure_api["url"])
        ))

    correct_case = check_app_and_count(all_correct_test_apis)
    failure_case = check_app_and_count(all_failure_test_apis, failure_flag=True)

    # Delete to free memory
    del all_correct_test_results, all_failure_test_results, all_correct_test_apis, all_failure_test_apis
    gc.collect()

    # 加载jinja2模板
    template = loader_jinja2()
    msg = ""
    app_index = 1
    _failure_case_list = None
    for app_name, correct_case_list in correct_case.items():
        if not correct_case_list:
            continue
        url_root = correct_case_list[0].url_root
        correct_case_num = len(correct_case_list)
        failure_case_num = 0
        app_case_total = correct_case_num + failure_case_num
        _failure_case_list = []

        for _app_name, failure_case_list in failure_case.items():
            if not failure_case_list:
                continue
            if app_name == _app_name:
                url_root = correct_case_list[0].url_root
                correct_case_num = len(correct_case_list)
                failure_case_num = len(failure_case_list)
                app_case_total = correct_case_num + failure_case_num
                _failure_case_list = failure_case_list

        template_msg = template.render(
                               num=app_index,
                               url_root=url_root,
                               total=app_case_total,
                               success=correct_case_num,
                               failed=failure_case_num,
                               failed_list=_failure_case_list,
                               case_duration_top10=correct_case_list,
                               wrap="\n")

        match = re.search(r"[\s]{6}Top", template_msg).group()
        msg += re.sub(match, "\nTop", template_msg, 1)
        app_index += 1

    msg = "Auto RESTful API Test Report: \n" + msg
    if isinstance(get_webhook_url(), list):
        for url in get_webhook_url():
            send_msg_to_dingding(url, msg)
    elif isinstance(get_webhook_url(), str):
        url = get_webhook_url()
        send_msg_to_dingding(url, msg)
    else:
        logger.error("webhook_url in yml configuration file only supports string and list.")

