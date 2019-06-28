import json
from .base_api import BaseApiInfo, Result
from urllib import parse


class GetApiInfo(BaseApiInfo):
    def run(self, is_timing=False):
        if not self.url:
            raise Exception("Failed to get the api url path!!!")
        if self.info:
            self.get_api_info(is_timing)

    def get_api_info(self, is_timing=False):
        self.get_basic_info()
        # 获取query参数
        if "<query>" in self.info and "</query>" in self.info:
            self.info.strip()
            query_handle = self.info[
                           self.info.index("<query>") + 7:self.info.rindex("</query>")]
            query_str = self.slice(query_handle)
            # query = None
            if query_str:
                if "{{" in query_str and "}}" in query_str:
                    query_str = query_str.replace('{{', '"{{', 100)
                    query_str = query_str.replace('}}', '}}"', 100)
                query_str = "".join(query_str.split())
                if query_str.endswith(",}"):
                    query_str = query_str.replace(",}", "}", 100)
                try:
                    query = json.loads(query_str)
                except Exception as e:
                    print("json loads Error: ", e)
                    return
                if self.parse_vars():
                    for vars_key in self.parse_vars().keys():
                        if vars_key == self.url:
                            for url_vars_name, url_vars_param in self.parse_vars().get(vars_key, KeyError).items():
                                for name, value in query.items():
                                    if isinstance(value, str):
                                        if "{{" in value and "}}" in value:
                                            if url_vars_name == value.replace('{{', "").replace('}}', "").strip():
                                                if url_vars_param is None:
                                                    url_vars_param = ""
                                                query[name] = url_vars_param
                            break
                        # for g_vars_name, g_vars_param in self.parse_vars().get(vars_key, KeyError).items():
                        #     for name, value in query.items():
                        #         if isinstance(value, str):
                        #             if "{{" in value and "}}" in value:
                        #                 if g_vars_name == value.replace('{{', "").replace('}}', "").strip():
                        #                     query[name] = g_vars_param
                # make url
                url_param = ""
                # if self.url == "/service/search":
                #     import pdb
                #     pdb.set_trace()
                for url_key, url_value in query.items():
                    if not url_value and url_value != 0:
                        url_value = ""
                    if isinstance(url_value, str):
                        # if u'\u4e00' <= url_value <= u'\u9fa5':
                        url_param += "%s=%s&" % (url_key, parse.quote(url_value))
                    else:
                        url_param += "%s=%s&" % (url_key, url_value)

                self.url = self.url + "?" + url_param
                self.result_list.append(Result(
                    name=self.name,
                    method=self.method,
                    url=self.url,
                    validators=self.validators,
                    headers=self.headers
                ))
        else:
            self.result_list.append(Result(
                name=self.name,
                method=self.method,
                url=self.url,
                validators=self.validators,
                headers=self.headers
            ))

