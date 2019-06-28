import requests
import json
import re
from ruamel import yaml
from HandleProperties import Properties
from webhook import process_msg_to_dingding
from api_class.get_api import GetApiInfo
from api_class.post_api import PostApiInfo
from api_class.base_api import BaseApiInfo
from config.constant import *


def read_properties_config():
    # 获取swagger url和yml文件名
    pro = Properties('config.properties')
    api_key = "API_DOC_URL"
    yml_key = "YAML_FILE_PATH"
    try:
        API_DOC_URL = pro.get(api_key)
        YAML_FILE_PATH = pro.get(yml_key)
    except:
        print("yml文件为空!")
        return

    return API_DOC_URL, YAML_FILE_PATH


def get_swagger_response(api_doc_url):
    """get swagger.json content"""
    # 对url访问并检查返回的response
    response = requests.get(url=api_doc_url)

    # coding test
    response.encoding = "utf-8"

    if response.status_code != 200:
        print("访问swagger url 失败！")
        return
    datas = json.loads(response.text)
    if not isinstance(datas, dict):
        print(u"获取的数据类型不是json！")
        return
    return datas


def make_name(name):
    if name:
        return name[2:]
    return name


def get_app_name(base_url):
    return "_".join(base_url.split("/")[1:])


def create_api(method, url, description, summary, base_url, result_list, is_timing=False):
    # 根据baseUrl判断哪个app
    app_yml_file_name = None
    for _app_yml_file_name in app_yml_file_name_list:
        if _app_yml_file_name == "_".join(base_url.split("/")[1:]) + ".yml":
             app_yml_file_name = _app_yml_file_name

    if method.upper() == "GET":
        GetApiInfo(
            url=url,
            method=method,
            description=description,
            name=summary,
            base_url=base_url,
            app_yml_file_name=app_yml_file_name,
            is_timing=is_timing,
            app_name=get_app_name(base_url),
            result_list=result_list
        ).run()
    elif method.upper() == "POST":
        PostApiInfo(
            url=url,
            method=method,
            description=description,
            name=summary,
            base_url=base_url,
            app_yml_file_name=app_yml_file_name,
            is_timing=is_timing,
            app_name=get_app_name(base_url),
            result_list=result_list,
        ).run()
    else:  # XXX: maybe support other request type.
        pass


def case_testing(datas, result_list, is_timing=False):
    """process swagger.json to generate the expected data format"""
    testset = datas.get("info", None)
    if testset:
        testset = testset.get("description", None)
    results = []
    start = {"config": [{'testset': testset}]}
    results.append(start)
    for url, value in datas['paths'].items():
        for method, info in value.items():
            if method.upper() not in all_methods:
                continue
            summary = info.get("summary", None)
            parameter = info.get("description", None)
            if summary and parameter and "1:" in summary and "2:" in parameter:
                one_case = re.match(r"([\s\S]*)2:", parameter)
                try:
                    one_case_str = one_case.group(1)
                except:
                    one_case_str = None
                if one_case_str:
                    one_case_str = summary + one_case_str
                    create_api(
                        method=method,
                        url=url,
                        description=one_case_str,
                        summary=make_name(summary),
                        base_url=datas["basePath"],
                        is_timing=is_timing,
                        result_list=result_list,
                    )

                if parameter and "2:" in parameter and "3:" in parameter:
                    two_case = re.search(r"2:([\s\S]*)3:", parameter)
                elif parameter and "2:" in parameter and "3:" not in parameter:
                    two_case = re.search(r"2:([\s\S]*)", parameter)
                else:
                    two_case = None
                try:
                    two_case_str = two_case.group(1)
                except:
                    two_case_str = None
                if two_case_str:
                    create_api(
                        method=method,
                        url=url,
                        description=two_case_str,
                        summary=make_name(summary),
                        base_url=datas["basePath"],
                        is_timing=is_timing,
                        result_list=result_list,
                    )

                if parameter and "3:" in parameter and "4:" in parameter:
                    three_case = re.search(r"3:([\s\S]*)4:", parameter)
                elif parameter and "3:" in parameter and "4:" not in parameter:
                    three_case = re.search(r"3:([\s\S]*)", parameter)
                else:
                    three_case = None
                try:
                    three_case_str = three_case.group(1)
                except:
                    three_case_str = None
                if three_case_str:
                    create_api(
                        method=method,
                        url=url,
                        description=three_case_str,
                        summary=make_name(summary),
                        base_url=datas["basePath"],
                        is_timing=is_timing,
                        result_list=result_list,
                    )

                if parameter and "4:" in parameter and "5:" in parameter:
                    four_case = re.search(r"4:([\s\S]*)5:", parameter)
                elif parameter and "4:" in parameter and "5:" not in parameter:
                    four_case = re.search(r"4:([\s\S]*)", parameter)
                else:
                    four_case = None
                try:
                    four_case_str = four_case.group(1)
                except:
                    four_case_str = None
                if four_case_str:
                    create_api(
                        method=method,
                        url=url,
                        description=four_case_str,
                        summary=make_name(summary),
                        base_url=datas["basePath"],
                        is_timing=is_timing,
                        result_list=result_list,
                    )

                if parameter and "5:" in parameter and "6:" in parameter:
                    print(
                        "\033[1;32;43m Sorry, A single url only supports 5 cases at the same time, or contact "
                        "owner to resolve this issue !! \033[0m"
                    )
                elif parameter and "5:" in parameter and "6:" not in parameter:
                    five_case = re.search(r"5:([\s\S]*)", parameter)
                else:
                    five_case = None
                try:
                    five_case_str = five_case.group(1)
                except:
                    five_case_str = None
                if five_case_str:
                    create_api(
                        method=method,
                        url=url,
                        description=five_case_str,
                        summary=make_name(summary),
                        base_url=datas["basePath"],
                        is_timing=is_timing,
                        result_list=result_list,
                    )
            else:
                create_api(
                    method=method,
                    url=url,
                    description=parameter,
                    summary=make_name(summary),
                    base_url=datas["basePath"],
                    is_timing=is_timing,
                    result_list=result_list,
                )

    for res in result_list:
        results.append({"test": res.test})
    return results


def write_yaml(yaml_file_path, results):
    """write data to yaml file"""
    with open(yaml_file_path, "w", encoding='utf-8') as yml_file:
        yml_file.truncate()
        yml_file.write("---\n")
        yaml.dump(results, yml_file, Dumper=yaml.RoundTripDumper, allow_unicode=True)


def timing_test():
    app_hosts = dict()

    for app_url in app_url_list:
        test_file_path = None
        datas = get_swagger_response(app_url)
        result_list = []
        results = case_testing(datas, result_list, is_timing=True)
        # screen the file name
        app_name_file = "_".join(app_url.split("/")[3:5]) + ".yml"
        app_host = "".join([app_url.split("/")[0] + "//", app_url.split("/")[2]])
        app_hosts.setdefault(app_name_file, app_host)
        for app_yml_file_name in app_yml_file_name_list:
            if app_name_file == app_yml_file_name:
                test_file_path = "config/test_files/%s" % app_name_file
                write_yaml(test_file_path, results)
                break

    # starting test
    from pyresttest.resttest import main
    args_dict = {}
    all_test_results = []
    for test_file, base_url in app_hosts.items():
        args_dict[u"url"] = base_url
        args_dict[u"test"] = "config/test_files/%s" % test_file
        try:
            test_results = main(args_dict)
            all_test_results.append(test_results)
        except Exception as e:
            raise e
    process_msg_to_dingding(all_test_results)


def api_auto_test_main():
    api_doc_url, yaml_file_path = read_properties_config()
    datas = get_swagger_response(api_doc_url)
    results = case_testing(datas)
    write_yaml(yaml_file_path, results)


if __name__ == '__main__':
    api_auto_test_main()


