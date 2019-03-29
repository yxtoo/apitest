
import re
import json
import requests
from ruamel import yaml
from HandleProperties import Properties


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


def read_file(path):
    """ Read an input into a file, doing necessary conversions around relative path handling """
    with open(path, "r", encoding='utf-8') as f:
        string = f.read()
        f.close()
    return string


def read_yml_file(path):
    """ Read test file at 'path' in YAML """
    return yaml.safe_load(read_file(path))


def parse_vars():
    return read_yml_file('./vars.yaml')


def parse_parameter(parameter, url, method, base_url, name, results_list):
    if base_url == '/':
        base_url = ""
    test = []
    option_str = None
    body = None
    query_str = None
    headers_str = None
    # 获取option参数
    if parameter and "<option>" in parameter and "</option>" in parameter:
        parameter.strip()
        option_handle = parameter[parameter.index("<option>") + 8:parameter.rindex("</option>")]
        if "{" in option_handle and "}" in option_handle:
            option_handle.strip()
            option_str_left_index = option_handle.index("{")
            option_str_right_index = option_handle.rindex("}")
            option_str = option_handle[option_str_left_index:option_str_right_index + 1]

        if option_str and url.count("{") == 1 and url.count("}") == 1:
            one_char = url[url.index("{"):url.index("}") + 1]
            one_option_dict = json.loads(option_str)
            url = url.replace(one_char, one_option_dict[one_char[1:len(one_char) - 1]])
        elif option_str and url.count("{") == 2 and url.count("}") == 2:
            two_char = re.match(r"/.*({.*}).*({.*}).*", url)
            two_option_dict = json.loads(option_str)
            for key, value in two_option_dict.items():
                if "{" + key + "}" == two_char.group(1):
                    url = url.replace(two_char.group(1), value)
                if "{" + key + "}" == two_char.group(2):
                    url = url.replace(two_char.group(2), value)
        elif option_str and url.count("{") == 3 and url.count("}") == 3:
            three_char = re.match(r"/.*({.*}).*({.*}).*({.*}).*", url)
            three_option_dict = json.loads(option_str)
            for key, value in three_option_dict.items():
                if "{" + key + "}" == three_char.group(1):
                    url = url.replace(three_char.group(1), value)
                if "{" + key + "}" == three_char.group(2):
                    url = url.replace(three_char.group(2), value)
                if "{" + key + "}" == three_char.group(3):
                    url = url.replace(three_char.group(3), value)

    # 获取headers参数
    if parameter and "<headers>" in parameter and "</headers>" in parameter:
        parameter.strip()
        headers_handle = parameter[parameter.index("<headers>") + 9:parameter.rindex("</headers>")]
        if "{" in headers_handle and "}" in headers_handle:
            headers_handle.strip()
            headers_str_left_index = headers_handle.index("{")
            headers_str_right_index = headers_handle.rindex("}")
            headers_str = headers_handle[headers_str_left_index:headers_str_right_index + 1]

    # 获取query参数
    if parameter and "<query>" in parameter and "</query>" in parameter:
        parameter.strip()
        query_handle = parameter[parameter.index("<query>") + 7:parameter.rindex("</query>")]
        if "{" in query_handle and "}" in query_handle:
            query_handle.strip()
            query_str_left_index = query_handle.index("{")
            query_str_right_index = query_handle.rindex("}")
            query_str = query_handle[query_str_left_index:query_str_right_index + 1]
        if query_str and method == "GET":
            url_param_dict = json.loads(query_str)
            if parse_vars():
                for vars_name, vars_value in parse_vars().items():
                    for get_name, get_value in url_param_dict.items():
                        if "{{" + vars_name + "}}" == get_value:
                            url_param_dict[get_name] = vars_value
            # make url
            url_param = ""
            for url_key, url_value in url_param_dict.items():
                if not url_value:
                    url_value = ""
                url_param += "%s=%s&" % (url_key, url_value)
            url = url + "?" + url_param

    # 获取body参数
    elif parameter and "<body>" in parameter and "</body>" in parameter:
        parameter.strip()
        body_handle = parameter[parameter.index("<body>"):parameter.rindex("</body>")]
        if "{" in body_handle and "}" in body_handle:
            body_handle.strip()
            body_str_left_index = body_handle.index("{")
            body_str_right_index = body_handle.rindex("}")
            body_str = body_handle[body_str_left_index:body_str_right_index + 1]
            if body_str:
                body = (json.loads(body_str))
                if parse_vars():
                    for vars_name, vars_param in parse_vars().items():
                        for body_name, body_value in body.items():
                            if "{{" + vars_name + "}}" == body_value:
                                body[body_name] = vars_param

    validators = []
    if parameter and "<validators>" in parameter and "</validators>" in parameter:
        parameter.strip()
        validators_handle = parameter[parameter.index("<validators>"):parameter.rindex("</validators>")]
        if "{" in validators_handle and "}" in validators_handle:
            validators_handle.strip()
            validators_str_left_index = validators_handle.index("-")
            validators_str_right_index = validators_handle.rindex("}")
            validators_str = validators_handle[validators_str_left_index:validators_str_right_index + 1]
            compare_list = re.findall(r"-.*}", validators_str)
            for compare in compare_list:
                compare_str = re.match(r"- (\w{7,12}): ({.*})", compare)
                validators.append({compare_str.group(1): json.loads(compare_str.group(2))})

    if name and method and url and validators:
        name_dict = {'name': name}
        method_dict = {'method': method}
        default_headers = {"Content-Type": "application/json"}
        if headers_str:
            default_headers.update(json.loads(headers_str))
        headers_dict = {'headers': default_headers}
        url_dict = {"url": base_url + url}
        body_dict = {"body": json.dumps(body)}
        validators_dict = {"validators": validators}
        test.append(name_dict)
        test.append(headers_dict)
        test.append(url_dict)
        test.append(method_dict)
        if method == "POST" or method == "PUT":
            test.append(body_dict)
        test.append(validators_dict)
        results_list.append({'test': test})


def make_name(name):
    if name:
        return name[2:]
    return name


def case_testing(datas, yaml_file_path):
    testset = datas["info"]["description"]
    results_list = []
    start = {"config": [{'testset': testset}]}
    results_list.append(start)

    for url, value in datas['paths'].items():
        for method, info in value.items():
            if isinstance(info, dict):
                summary = info.get("summary", None)
                parameter = info.get("description", None)
                if summary and "1:" in summary and parameter and "2:" in parameter:
                    one_case = re.match(r"([\s\S]*)2:", parameter)
                    try:
                        one_case_str = one_case.group(1)
                    except:
                        one_case_str = None
                    if one_case_str:
                        one_case_str = summary + one_case_str
                        parse_parameter(
                            parameter=one_case_str,
                            url=url,
                            method=method.upper(),
                            base_url=datas["basePath"],
                            name=make_name(summary),
                            results_list=results_list
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
                        parse_parameter(
                            parameter=two_case_str,
                            url=url,
                            method=method.upper(),
                            base_url=datas["basePath"],
                            name=make_name(summary),
                            results_list=results_list
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
                        parse_parameter(
                            parameter=three_case_str,
                            url=url,
                            method=method.upper(),
                            base_url=datas["basePath"],
                            name=make_name(summary),
                            results_list=results_list
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
                        parse_parameter(
                            parameter=four_case_str,
                            url=url,
                            method=method.upper(),
                            base_url=datas["basePath"],
                            name=make_name(summary),
                            results_list=results_list
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
                        parse_parameter(
                            parameter=five_case_str,
                            url=url,
                            method=method.upper(),
                            base_url=datas["basePath"],
                            name=make_name(summary),
                            results_list=results_list
                        )
                else:
                    parse_parameter(
                        parameter=parameter,
                        url=url,
                        method=method.upper(),
                        base_url=datas["basePath"],
                        name=summary,
                        results_list=results_list
                    )

    with open(yaml_file_path, "w", encoding='utf-8') as yml_file:
        yml_file.write("---\n")
        yaml.dump(results_list, yml_file, Dumper=yaml.RoundTripDumper, allow_unicode=True)


def api_auto_test_main():
    api_doc_url, yaml_file_path = read_properties_config()
    datas = get_swagger_response(api_doc_url)
    case_testing(datas, yaml_file_path)


if __name__ == '__main__':
    api_auto_test_main()
