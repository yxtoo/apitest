
import os
import sys
from ruamel import yaml
from optparse import OptionParser
from HandleProperties import Properties


class Config(object):
    def __init__(self, args=None):
        if not args:
            raise Exception(
                "Configuration information not captured, please check the necessary basic configuration information")
        self.app_name = args["appName"]
        self.app_url = args["appUrl"]
        self.app_base_url = args["appBaseUrl"]

    def make_java_url(self):
        try:
            self.swagger_url = "".join([args["appUrl"], "/v2/api-docs"])
            self.yml_path = "".join([args["appName"], ".yaml"])
        except Exception as e:
            raise e

    def make_python_url(self):
        try:
            self.swagger_url = "".join([args["appUrl"], args["appBaseUrl"], "/swagger.json"])
            try:
                self.yml_path = "".join([args["appBaseUrl"].split('/')[1], "_", args["appBaseUrl"].split('/')[2], ".yaml"])
            except:
                raise Exception(
                    "In order to meet the restful style, the value of {{{ appBaseUrl }}} must have a version number !!!")
        except:
            self.swagger_url = "".join([args["appUrl"], "/swagger.json"])
            self.yml_path = "".join([args["appName"], ".yaml"])


def read_file(path):
    """ Read an input into a file, doing necessary conversions around relative path handling """
    with open(path, "r", encoding="utf-8") as f:
        string = f.read()
        f.close()
    return string


def read_yml_file(path):
    """ Read test file at 'path' in YAML """
    return yaml.safe_load(read_file(path))


def parse_command_line_args(args_in):
    # handling command line arguments
    parser = OptionParser()
    parser.add_option("-n", "--name", dest="appName", help="the project app name")
    parser.add_option("-u", "--url", dest="appUrl", help="the project app url")
    parser.add_option("-b", "--BaseUurl", dest="appBaseUrl", help="the project app url prefix")
    parser.add_option("-s", "--schedule", dest="schedule",
                      help="whether to run periodically, if there is, run once a day")
    (args, unparsed_args) = parser.parse_args(args_in)
    args = vars(args)
    if args["schedule"]:
        return "schedule"
    if not args['appName'] or not args['appUrl']:
        return read_yml_file("restful_test.yml")
    return args


def load_config(key, value):
    """"Reparse the properties configuration file"""
    pro = Properties('config.properties')
    if not pro.get(key):
        pro.write_new_config(key)
    elif pro.get(key) and pro.get(key) != value:
        pro.put(key, value)
    pro = Properties('config.properties')
    if pro.get(key) == value:
        print("The configuration is successfully loaded.")


def check_yaml_content_and_count(context):
    """check the contents of the yml file and count it """
    if not isinstance(context, list):
        print("please check the yml format, only support the preparation of array form...")
        return
    api_count = 0
    name_count = 0
    for test in context:
        items = test.get("test", None)
        if items:
            api_count += 1
            for item in items:
                name = item.get("name", None)
                if name == 'null':
                    name_count += 1

    print("TOTAL: {api_count} APIs in total. {name_count} apis have no names;".format(
        api_count=api_count, name_count=name_count
    ))


def main(args):
    if args == "schedule":
        from api_test import timing_test
        timing_test()
    else:
        conf = Config(args)
        if conf.app_base_url is None:
            conf.make_java_url()
        else:
            conf.make_python_url()

        api_key = "API_DOC_URL"
        yml_key = "YAML_FILE_PATH"

        # processing the properties configuration file
        load_config(api_key, conf.swagger_url)
        load_config(yml_key, conf.yml_path)

        try:
            from api_test import api_auto_test_main
            api_auto_test_main()
        except Exception as e:
            raise e

        # # check if the file exists
        # yml_file = Properties('config.properties').get(yml_key)
        #
        # if not os.path.exists("".join(["./", conf.yml_path])):
        #     print("YML file generated failed, Please check and try again!!!")
        #     return
        # print("successfully successfully")
        #
        # with open(yml_file, encoding="utf-8") as linux_f:
        #     context = yaml.load(linux_f)
        #
        #     check_yaml_content_and_count(context)

        try:
            from pyresttest.resttest import command_line_run
            command_line_run(base_url=conf.app_url, test_file=conf.yml_path)
            print("\033[1;35m Good news: \n -------华丽的分割线------ \n command execution successfully ! \033[0m")
        except Exception as e:
            raise e


if __name__ == '__main__':
    args = parse_command_line_args(sys.argv[1:])
    main(args)
