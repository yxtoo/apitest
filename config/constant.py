import os
from ruamel import yaml


# define all apps ip:port/url prefix
app_url_list = [
    "http://10.10.91.95:29021/navigatorapi/v1/swagger.json",
    # "http://10.10.91.95:29009/datavdashboardapi/v2/swagger.json",
    "http://10.10.91.95:29008/datavorgdashboardapi/v2/swagger.json",
    "http://10.10.85.57:49011/orgskyeyeapi/v4/swagger.json",
    "http://10.10.85.57:29016/skyeyeapi/v3/swagger.json",
    "http://10.10.85.57:29015/skyeyeapi/v2/swagger.json",
    "http://10.10.85.57:29012/srvskyeyeapi/v1/swagger.json",
    # "http://10.10.85.57:29011/orgskyeyeapi/v1/swagger.json",
    # "http://10.10.91.95:29016/datavgraphapi/v2/swagger.json",
]

app_yml_file_name_list = [
    "test.yml"
]

app_names = {
    "/api/v1": "api_v1",
}

all_methods = ["GET", "POST", "DELETE", "PUT", "OPTIONS"]

navigator_token_app_list = [""]

def read_yml(file_name):
    """Can only read the yml file of the current path"""
    if not isinstance(file_name, str):
        return None
    current_path = os.path.dirname(os.path.realpath(__name__))
    yml_config_path = os.path.join(current_path, "config/%s" % file_name)
    with open(yml_config_path, 'r', encoding="utf-8") as yml_file:
         yml_content = yaml.safe_load(yml_file)
    return yml_content


def get_webhook_url():
    config_content = read_yml("dingding_robot.yml")
    return config_content.get("webhook_url")


def read_config_yaml_file(path):
    if not os.path.exists("config/%s" % path):
        return False
    with open("config/%s" % path, "r", encoding="utf-8") as f:
        string = f.read()
        f.close()
    return yaml.safe_load(string)
