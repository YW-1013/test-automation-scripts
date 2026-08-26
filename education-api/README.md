# education #
education是为教育平台提供保障的服务，提供了一系列包括接口、webUI方面的测试

## 执行方式 ##
- 环境准备
  - python环境准备
  ```
  安装python3
  ```
  - 依赖包准备
  ```
  python -m pip install -r requirements.txt
  ```
- 执行测试
    ```
    python main.py 
    ```
    - 支持参数
        ```
        -h --help   查看帮助
        --env       测试的环境
        --host      没有在配置文件配置地址时，直接传入host，例如ip
        --protocol  网络协议(http/https)，配合host使用, 默认是http
        --port      端口，配合host使用，默认是30017
        --code      组织号， 配合host使用
        --private   是否是私有化项目
        --tags      执行对应标签的用例
        ```
      
## 脚本编写规范 ##

### 版本管理 ###
|分支名| 说明                                                                  |备注|
|-|---------------------------------------------------------------------|-|
|master| 核心分支，有且只有一个，最新最稳定的代码。只有能正常运行且通过code review的代码，才允许合入主分支              ||
|private| 私有化基线分支，提供私有化基线测试能力                                                 ||
|feature| 临时开发分支，存在多个，当有新功能时，使用feature分支进行开发调试，通常从master上获取                   ||
|project| 项目分支，用于支持对应私有化项目，从private/master分支获取，project分支创建出来后会长期存在用于持续支持对应项目  ||
|bugfix| bug修复分支，从master上获取，当有bug修复时，创建bugfix分支进行修复验证，通过code review后合入master ||


### 标签管理 ###
- 模块标签：表示当前feature归属于哪一个模块，例如：auth、edu
- 
- 功能标签：通过功能标签能具体到对应功能，方便调试和用例筛选，例如：login、live
  
- 特殊标签：用于声明需要特定条件的标签


### pycharm支持pytest_bdd ###
- 编译器：pycharm专业版
- 支持pytest_bdd:
  - 打开setting
  - 直接搜索bdd
  - 在languages中点击BDD，然后右边设置下拉框选择pytest_bdd


### 文件说明 ###
- conftest：pytest的配置文件
- pytest.ini: pytest主配置文件，定义一些选项参数
- main.py： 用python执行测试时的启动文件
- env：定义命令行传参文件
- .gitignore: git提交时忽略的文件，避免调试过程中产生的无效数据提交到仓库
- features：feature测试文件
- report：报告存放文件
- tests：测试代码文件
  - before：用于定义前置操作
    ```
    feature前 置:  before_feature_ + feature名称 的fixture函数
    scenario前置： before_scenario_ + scenario名称 的fixture函数
    
    如需新增其他前置函数，详细配置：tests/before_and_teardown.py

    ```
    
  - teardown: 用于定义后置操作
    ```
    feature 后 置:  teardown_feature_ + feature名称 的fixture函数
    scenario 后置： teardown_scenario_ + scenario名称 的fixture函数
    
    如需新增其他后置函数，详细配置：tests/before_and_teardown.py

    ```
  - library：基础工具，包括一些自定义功能函数，以及api的封装调用都放在这个目录
  - setup：用于初始化的操作，例如用户、设备登录、基本环境校验等
  - steps: 定义实现步骤，和features中的Given、When、Then对应
    - given：执行前置步骤，默认这里执行的是会成功的前置步骤
    - when：执行测试流程，即需要测试的操作
    - then：验证步骤，用于对when结果的验证
