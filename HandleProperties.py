import tempfile
import os
import re


class Properties(object):

    def __init__(self, fileName):
        self.fileName = fileName
        self.properties = {}

        try:
            with open(self.fileName, 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    if line.find('=') > 0 and not line.startswith('#'):
                        strs = line.split('=')
                        self.properties[strs[0].strip()] = strs[1].strip()
        except Exception as e:
            raise e

    def get(self, key, default_value=''):
        if self.properties.get(key):
            return self.properties[key]
        return default_value

    def has_key(self, key):
        return self.properties.get(key)

    def put(self, key, value):
        self.properties.setdefault(key, value)
        self.replace_property(key + '=.*', key + '=' + value, True)

    def write_new_config(self, key):
        if self.get(key):
            return
        with open(self.fileName, 'a') as f:
            f.write("".join(["\n", key, "=***"]))

    def replace_property(self, from_regex, to_str, append_on_not_exists=True):
        file = tempfile.TemporaryFile()

        if os.path.exists(self.fileName):
            r_open = open(self.fileName, 'r')
            pattern = re.compile(r'' + from_regex)
            found = None
            for line in r_open:
                if pattern.search(line) and not line.strip().startswith('#'):
                    found = True
                    line = re.sub(from_regex, to_str, line)
                file.write(bytes(line, 'utf-8'))
            if not found and append_on_not_exists:
                file.write('\n' + to_str)
            r_open.close()
            file.seek(0)

            content = file.read()

            if os.path.exists(self.fileName):
                os.remove(self.fileName)

            with open(self.fileName, 'wb') as w_open:
                w_open.write(content)

            file.close()
        else:
            print("file %s not found" % self.fileName)

