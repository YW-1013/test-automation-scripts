# 教育平台 Web UI 自动化框架 education-ui

> 基于 **Selenium + pytest + POM（Page Object Model）** 的教育云平台 Web UI 自动化测试框架，采用页面对象、定位器、测试数据三层分离的分层设计，支持 Allure 报告与数据驱动。

> 🔒 上传前已对真实测试账号、密码、姓名、内网地址等做脱敏处理（替换为 `YOUR_ACCOUNT` / `YOUR_PASSWORD` / `YOUR_NAME` / `your-server.example.com` 等占位符）。使用时请填入你自己的环境与账号。

---

## 分层设计（POM）

```
education-ui/
├── PageLocators/     # 元素定位器（By.XPATH/CSS），与页面对象分离，UI 改版只改这里
│   ├── login_page_locators.py
│   ├── index_page_locators.py
│   ├── organize_page_locators.py
│   └── basic_info_page_locators/     # 基础信息模块定位器
├── PageObjects/      # 页面对象：封装每个页面的操作方法（登录、跳转、读取文本…）
│   ├── login_page.py
│   ├── index_page.py
│   ├── organize_page.py
│   └── basic_info_pages/
├── TestCases/        # 测试用例，按业务模块组织，每模块含独立 conftest
│   ├── ModelLogin/           # 登录模块（正确/错误/空值/密码显隐等）
│   ├── ModelIndex/           # 首页模块
│   └── ModelBaseInfo/        # 组织基础信息模块
├── TestDatas/        # 测试数据（账号、URL、预期值），数据驱动
├── Common/           # 公共工具（显式等待封装、日志）
└── requirements.txt
```

## 设计要点

- **三层分离**：定位器（Locators）/ 页面操作（PageObjects）/ 测试数据（TestDatas）彻底解耦，页面改版时只需改定位器，用例与数据不动，维护成本低。
- **数据驱动**：登录等用例的正例/反例（用户不存在、密码错误、用户名为空、密码为空）由 `TestDatas` 提供，用 `@pytest.mark.parametrize` 驱动。
- **显式等待封装**：`Common/explicit_wait.py` 统一封装 `WebDriverWait`，避免硬编码 sleep，提升稳定性。
- **模块化 conftest**：每个测试模块有自己的 `conftest.py` 管理 fixture（如登录态、页面入口），层级清晰。
- **Allure 报告**：用例中用 `allure.step` 标注步骤，生成结构化可视化报告。

## 技术栈

`Python 3` · `Selenium` · `pytest` · `pytest 参数化`（数据驱动）· `POM 设计模式` · `Allure`（报告）· `WebDriverWait`（显式等待）

## 运行

```bash
pip install -r requirements.txt
pytest TestCases/ --alluredir=./allure-results
```

---

*代码用于个人技术能力展示，敏感信息已脱敏，遵循仓库根目录 [MIT License](../LICENSE)。*
