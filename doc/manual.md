一、API自动测试强依赖如下包：
    ● python（必须是3以上的版本）

    ● requests （不分版本）

    ● pyyaml （不分版本）

    ● ruamel.yaml（不分版本）

    ● pyresttest （不分版本）  

针对不同语言不同框架的api项目，在项目中，需要依赖不同的包，这在后边会讲到。

Note: 文件类API不支持测试！！！

二、下载工具包后解压， 下载地址：tools工具包 
文件说明：

    ● requirements.txt 文件时依赖包安装文件

    ● main.py 文件是脚本运行文件

    ● restful_test.yml 文件是app 信息配置文件，所需信息有：python项目需要配置 app name, app url prefix,  app url 。java项目配置app name, app url。也可以通过命令行传参， 在main.py 后边加上--help可查看参数解释

    ● vars.yaml 文件中定义 body 及 validators 的变量，格式参考yaml文件的对象定义格式。

三、一般问题检查思路
若出现以下情况：

 Test Group Default FAILED: : 3/4Tests Passed!

意思是共有四个case进行测试，通过了三个，有一个失败，具体失败原因可在输出终端上查看，请检查所写的断言规则是否合理，提取器是否能提取到数据。

在linux环境中若出现以下报错：

ImportError: pycurl: libcurl link-timeversion (7.29.0) is older than compile-timeversion (7.59.0)

意思是linux上的libcurl包与python的pycurl包冲突导致，

解决方法：

第一种：可以用rpm命令将libcurl包删除，再运行脚本文件即可。

第二种：使libcurl包与pycurl包版本一致。附：操作步骤
在linux上，装pyresttest包时，可能会遇到异常如下：  No such file or directory: 'curl-config'  ，解决方法参考：linux上python3 装pyresttest包不通过的解决方法



Python语言：
在阅读本页面之前，请先阅读父页面，如已阅读，请忽略。

python 语言编写的Restful API 依赖以下包：

    ● flask-swagger （不分版本， flask项目）

    ● django-rest-swagger （不分版本，django项目）

一、在写API代码时，把要测试的请求体和断言写入到API方法注释中，eg:
 展开源码
下面列出不同请求方法不同参数的定义()：

    Note: 若request请求不需要参数则不定义; 定义所用的引号全部为双引号，不支持单引号！！！

    ● GET:  <query>{"parameter1":  "value1",  "parameter2": "value2"}</query>   // Note: 若参数值为null, 则填写null, null值引号加不加都可。

    ● POST/PUT: <body>{"parameter1": "value1", "parameter2": "value2"}</body>   // body中的参数为dict类型，支持字典中嵌套列表，eg: 

<body>{"parameter1": "value1", "parameter2": "value2", "parameter3": [index1, index2, index3]}</body>
    ● url传参：eg： <option>{"option": "value1"}</option>

    ● headers：<headers> {"token": "value"} </headers>   // 在测试需要登录验证的API时往往需要在headers中携带token，需要注意的是一定要确保headers中token的时效性，避免测试不通过。

                

                注释中定义的<options>标签中的字典的key的名字一定要与URL路径中所定义的相同，就像上图中红色区域的部分。

body和query都支持变量。用"{{varName}}"标示变量名，对应的变量值定义在vars.yaml文件中。具体定义方式如下：  eg:   

def get(self):
    """
    金牌->产品->功能使用
    <query>
    {"date_range": 0, "platform": {{platform}}, "level": "{{level}}", "limit": 20, "offset": 0, "order_by": "pv",
        "direction": "DESC", "pagecode": null, "version": null, "keywords": null}
    </query>
    <validators>
        - compare: {"header": "content-type", "comparator": "contains", "expected": "application/json"}
        - compare: {"jsonpath_mini": "datas.1.name", "comparator": "eq", "expected": "金牌课程"}
    </validators>
    """
    # code
vars.yaml 中定义相应的变量值：

platform: 1601
level: module


支持单个url中定义多个case的测试， 定义的时候务必要加上序号进行说明， 且序号必须是

1:, 2:, 3:, 4:, 5:
        eg：

目前只支持单个URL下最多定义五个测试case！

三、支持的断言规则：
      https://github.com/svanoort/pyresttest/blob/master/advanced_guide.md#validation-basics



Java 语言：
在阅读本页面之前，请先阅读父页面，如已阅读，请忽略。

java语言编写的Restful API 依赖以下包(这里只列出spring-boot框架)：

<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-swagger-ui</artifactId>
    <version>2.9.2</version>
</dependency>
<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-swagger2</artifactId>
    <version>2.9.2</version>
</dependency>
其他框架请自行寻找相关的swagger包。

配置：在Application.java中引入 @EnableSwagger2 来启动swagger注解，如下：

 展开源码
下一步就是在接口中使用注解了，主要是针对 @ApiOperation 的解析。

以下是一个比较简单的例子：在这里，需要注意的是，notes参数必须要用常量字符串，为了做到容易理解，我这里采用多行字符串，你也可以采用单行字符串，那样会很长很长。在java中，多行字符串只能通过加号或者StringBuffer、StringBuilder。

 展开源码
下面列出不同请求方法不同参数的定义()：

    Note: 若request请求不需要参数则不定义; 定义所用的引号全部为双引号，不支持单引号！！！

    ● GET:  <query>{"parameter1":  "value1",  "parameter2": "value2"}</query>   // Note: 若参数值为null, 则填写null, null值引号加不加都可。

    ● POST/PUT: <body>{"parameter1": "value1", "parameter2": "value2"}</body>   // body中的参数为dict类型，支持字典中嵌套列表，eg: 

<body>{"parameter1": "value1", "parameter2": "value2", "parameter3": [index1, index2, index3]}</body>

    ● url传参：eg： <option>{"option": "value1"}</option>

    ● headers：<headers> {"token": "value"} </headers>   // 在测试需要登录验证的API时往往需要在headers中携带token，需要注意的是一定要确保headers中token的时效性，避免测试不通过。



body和query都支持变量。用"{{varName}}"标示变量名，对应的变量值定义在vars.yaml文件中。具体定义方式如下：  eg:   

 展开源码
vars.yaml 中定义相应的变量值：

name: 小明
...
支持单个url中定义多个case的测试， 定义的时候务必要加上序号进行说明， 且序号必须是如下符号，目前只支持单个URL下最多定义五个测试case！

1:... 2:... 3:... 4:... 5:...

支持的断言规则：
      https://github.com/svanoort/pyresttest/blob/master/advanced_guide.md#validation-basics