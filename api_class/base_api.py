import json
import re
from ruamel import yaml
from config.constant import read_config_yaml_file

base_url = None


class BaseApiInfo(object):
    # result_list = []

    def __init__(self, **kwargs):
        global base_url
        base_url = kwargs.pop("base_url", None)
        self.info = kwargs.pop("description", None)
        self.url = kwargs.pop("url", None)
        self.method = kwargs.pop("method", None)
        self.name = kwargs.pop("name", None)
        self.app_yml_file_name = kwargs.pop("app_yml_file_name", None)
        self.is_timing = kwargs.pop("is_timing", False)
        self.app_name = kwargs.pop("app_name", None)
        self.result_list = kwargs.pop("result_list", [])
        self.headers = None
        self.validators = []

    def slice(self, content):
        """slice for '{' 、 '}' and right index + 1"""
        if "{" in content and "}" in content:
            content.strip()
            body_str_left_index = content.index("{")
            body_str_right_index = content.rindex("}")
            return content[body_str_left_index:body_str_right_index + 1]
        else:
            return

    def get_basic_info(self):
        # 获取option参数
        if self.url == "/datavgraphapi/v2/{option}/usagestat/featureusage/list/":
            import pdb
            pdb.set_trace()
        if "<option>" in self.info and "</option>" in self.info:
            self.info.strip()
            option_handle = self.info[self.info.index("<option>") + 8:self.info.rindex("</option>")]
            option_str = self.slice(option_handle)
            if option_str and self.url.count("{") == 1 and self.url.count("}") == 1:
                one_char = self.url[self.url.index("{"):self.url.index("}") + 1]
                one_option_dict = json.loads(option_str)
                self.url = self.url.replace(one_char, one_option_dict[one_char[1:len(one_char) - 1]])
            elif option_str and self.url.count("{") == 2 and self.url.count("}") == 2:
                two_char = re.match(r"/.*({.*}).*({.*}).*", self.url)
                two_option_dict = json.loads(option_str)
                for key, value in two_option_dict.items():
                    if "{" + key + "}" == two_char.group(1):
                        self.url = self.url.replace(two_char.group(1), value)
                    if "{" + key + "}" == two_char.group(2):
                        self.url = self.url.replace(two_char.group(2), value)
            elif option_str and self.url.count("{") == 3 and self.url.count("}") == 3:
                three_char = re.match(r"/.*({.*}).*({.*}).*({.*}).*", self.url)
                three_option_dict = json.loads(option_str)
                for key, value in three_option_dict.items():
                    if "{" + key + "}" == three_char.group(1):
                        self.url = self.url.replace(three_char.group(1), value)
                    if "{" + key + "}" == three_char.group(2):
                        self.url = self.url.replace(three_char.group(2), value)
                    if "{" + key + "}" == three_char.group(3):
                        self.url = self.url.replace(three_char.group(3), value)

        # 获取headers参数
        if "<headers>" in self.info and "</headers>" in self.info:
            self.info.strip()
            headers_handle = self.info[
                             self.info.index("<headers>") + 9:self.info.rindex("</headers>")]
            self.headers = self.slice(headers_handle)

        # 提取validators数据
        if "<validators>" in self.info and "</validators>" in self.info:
            self.info.strip()
            validators_handle = self.info[
                                self.info.index("<validators>"):self.info.rindex("</validators>")]
            if "{" in validators_handle and "}" in validators_handle:
                validators_handle.strip()
                validators_str_left_index = validators_handle.index("-")
                validators_str_right_index = validators_handle.rindex("}")
                validators_str = validators_handle[validators_str_left_index:validators_str_right_index + 1]
                compare_list = re.findall(r"-.*}", validators_str)
                for compare in compare_list:
                    compare_str = re.match(r"- (\w{7,12}): ({.*})", compare)
                    self.validators.append({compare_str.group(1): json.loads(compare_str.group(2))})

    def read_file(self, path):
        """ Read an input into a file, doing necessary conversions around relative path handling """
        with open(path, "r", encoding='utf-8') as f:
            string = f.read()
            f.close()
        return string

    def read_yml_file(self, path):
        """ Read test file at 'path' in YAML """
        return yaml.safe_load(self.read_file(path))

    def parse_vars(self):
        if self.is_timing:
            return read_config_yaml_file(self.app_yml_file_name)
        vars_path = "".join([self.read_yml_file("restful_test.yml").get("appPath", KeyError), "/swagger/vars.yaml"])
        return self.read_yml_file(vars_path)


class Result(object):
    def __init__(self, name, method, url, validators, headers=None, body=None):
        name_dict = {'name': name}
        method_dict = {'method': method}
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(json.loads(headers))
        headers_dict = {'headers': default_headers}
        url_dict = {"url": base_url + url}
        body_dict = {"body": json.dumps(body)}
        validators_dict = {"validators": validators}
        self.test = list()
        self.test.append(name_dict)
        self.test.append(headers_dict)
        self.test.append(url_dict)
        self.test.append(method_dict)
        if method.upper() == "POST" or method.upper() == "PUT":
            self.test.append(body_dict)
        self.test.append(validators_dict)
