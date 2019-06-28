"""Define the test case class here"""


class CorrectTestApi(object):
    def __init__(self, url_root, url, time, app_name):
        self.url_root = url_root
        self.url = url
        self.time = time
        self.app_name = app_name
        self.passed = True


class FailureTestApi(object):
    def __init__(self, url, method, param, status_code, msg, validator_msg, app_name):
        self.url = url
        self.method = method
        self.param = param
        self.status_code = status_code
        self.msg = msg
        self.validator_msg = validator_msg
        self.app_name = app_name
        self.passed = False
