import json
import copy
from .base_api import BaseApiInfo, Result


class PostApiInfo(BaseApiInfo):
    def run(self):
        if not self.url:
            raise Exception("Failed to get the api url path!!!")
        if self.info:
            self.post_api_info()

    def replace_param(self, body, vars_body):
        if isinstance(vars_body, dict):
            for body_key in body.keys():
                vars_value = vars_body.get(body_key, KeyError)
                if isinstance(vars_value, list):
                    if body_key == "thirdids":
                        body[body_key] = vars_value
                        continue
                    for var_value in vars_value:
                        body[body_key] = var_value
                        c_body = copy.deepcopy(body)
                        self.result_list.append(Result(
                            name=self.name,
                            method=self.method,
                            url=self.url,
                            body=body,
                            validators=self.validators,
                            headers=self.headers
                        ))
                        body = c_body
                    return None
                else:  # XXX: maybe support other types
                    body[body_key] = vars_value
            return body
        elif isinstance(vars_body, list):
            for var_param in vars_body:
                for body_key in body.keys():
                    body[body_key] = var_param.get(body_key, KeyError)
                    self.result_list.append(Result(
                        name=self.name,
                        method=self.method,
                        url=self.url,
                        body=body,
                        validators=self.validators,
                        headers=self.headers
                    ))
            return None
        else:  # XXX: maybe also support other types
            return None

    def post_api_info(self):
        self.get_basic_info()
        # get body parameter
        if "<body>" in self.info and "</body>" in self.info:
            self.info.strip()
            body_handle = self.info[self.info.index("<body>"):self.info.rindex("</body>")]
            body_str = self.slice(body_handle)
            if body_str:
                if "{{" in body_str and "}}" in body_str:
                    body_str = body_str.replace('{{', '"{{', 100)
                    body_str = body_str.replace('}}', '}}"', 100)
                    # 去除字符串中的 \n和空格
                    body_str = "".join(body_str.split())
                    if body_str.endswith(",}"):
                        body_str = body_str.replace(",}", "}", 100)
                    body = json.loads(body_str)
                    vars_param = self.parse_vars()[self.url]
                    body = self.replace_param(body, vars_param)
                    if body:
                        self.result_list.append(Result(
                            name=self.name,
                            method=self.method,
                            url=self.url,
                            body=body,
                            validators=self.validators,
                            headers=self.headers
                        ))
                else:
                    self.result_list.append(Result(
                        name=self.name,
                        method=self.method,
                        url=self.url,
                        body=json.loads(body_str),
                        validators=self.validators,
                        headers=self.headers
                    ))
