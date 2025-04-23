# 宇宙博客传送器 (Cosmic Blog Teleporter)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/flask-2.x%2B-green.svg)](https://flask.palletsprojects.com/)
[![Google AI Studio](https://img.shields.io/badge/Tool-Google_AI_Studio-blue)](https://aistudio.google.com)

本项目基于本人对于随机访问收藏的博客的需求，从前端到后端再到README全部借助**AI工具**（当然除了这段）AI工具是上面提到的Google的Gemini 2.5 Pro Preview 03-25。

一个 Flask 驱动的 Web 应用，允许用户管理一个博客主站列表，并能随机跳转到列表中的某个主站，或该主站下的某一篇随机文章。界面采用了炫酷的“宇宙传送门”主题，并支持中英文切换。**请不要随意恶意爬取他人网站**。
## 📝Todo
自己敲一份正经README

## ⚠免责声明

本软件仅供教育和个人演示目的，按“原样”提供，不作任何明示或暗示的保证，包括但不限于对适销性、特定用途适用性和非侵权性的保证。

本软件的核心功能涉及从第三方网站获取数据。本软件的使用者**全权负责**确保其使用行为符合：

1.  所有适用的地方、州、国家和国际法律法规。
2.  使用者配置本软件访问的网站的**服务条款 (ToS)**、使用条款或任何类似政策。抓取或爬行网站可能被其服务条款明确禁止。
3.  任何适用的数据隐私法规（例如 GDPR, CCPA）。
4.  标准的网络礼仪，包括尊重 `robots.txt` 文件，以及避免可能导致目标服务器过载的过高请求频率。

本软件的作者和贡献者**不承担**任何因本软件、使用本软件或进行其他交易所产生的任何索赔、损害赔偿或其他责任，无论是在合同诉讼、侵权诉讼或其他诉讼中。这包括但不限于因服务中断、数据丢失、网站所有者采取的法律行动、IP 地址被封锁或用户行为引发的任何其他后果所造成的损害。

**使用本软件即表示您确认理解这些风险，并同意为您的行为承担全部责任。** 请勿将本软件用于任何违反法律或任何网站服务条款的目的。如果您不确定使用此工具访问特定网站的合法性或可允许性，请勿使用或寻求法律建议。

## ✨ 主要功能

*   **随机跳转**:
    *   随机访问列表中的一个博客主站 (`/random_url`)。
    *   随机访问某个主站下的一篇内部文章 (`/random_blog`，三步随机：随机选站 -> 爬取站内链接 -> 随机选链接)。
*   **博客列表管理**:
    *   通过 Web 界面添加新的博客主站 URL (`/add_url`)。
    *   通过 Web 界面删除已存在的博客主站 URL (`/delete_url`)。
    *   添加/删除操作需要密码验证。
    *   URL 数据（包括添加时间）存储在 `urls.json` 文件中。
*   **用户界面**:
    *   炫酷的“宇宙传送门”主题界面。
    *   支持**中文**和**英文**两种语言切换，偏好设置会存储在本地 `localStorage`。
    *   在“导航控制台”中统一进行 URL 的添加和删除操作。
    *   在“已存坐标”列表中显示已保存的站点名称（从 URL 提取）和添加时间。
    *   点击随机跳转按钮后，在消息区域显示目标链接，供用户手动点击（解决了移动端 `window.open` 的限制）。
    *   显示操作反馈信息（成功、错误、加载中）。
*   **链接抓取与过滤**:
    *   `fetch_links` 函数能抓取指定博客主站内的所有内部链接。
    *   根据 `config.py` 中的 `FILTER_RULES` (如 `/tags?/`, `/archives/` 等) 和 `EXCLUDE_PARAMS` (如 `=tag`) 过滤掉非文章类型的链接。
*   **Docker 支持**:
    *   提供了 `Dockerfile` 和 `requirements.txt`，方便容器化部署。

## 🚀 技术栈

*   **后端**: Python 3.10+, Flask
*   **库**: Requests, Beautiful Soup 4
*   **前端**: HTML, CSS, JavaScript (无外部框架)
*   **数据存储**: JSON 文件 (`urls.json`)

## 📁 项目结构
```
your_project_directory/
├── Dockerfile # Docker 构建文件
├── requirements.txt # Python 依赖列表
├── app.py # Flask 应用主逻辑
├── config.py # 配置文件 (端口, 密码, 过滤规则等)
├── urls.json # 存储博客 URL 和时间戳 (应用首次运行时若不存在会自动创建)
├── templates/
│ └── index.html # 前端 HTML 模板 (对应 config.py 中的 MAXI_PAGE)
└── static/
└── images/
└── space_background.jpg # 宇宙背景图片 (需要自行放置)
```


## 🛠️ 安装与运行

### 环境准备

*   安装 Python 3.10 或更高版本。
*   安装 `pip` (通常随 Python 一起安装)。
*   (可选但推荐) 创建并激活一个 Python 虚拟环境。

### 本地运行步骤

1.  **克隆仓库** (或下载代码):
    ```bash
    git clone <your-repository-url>
    cd your_project_directory
    ```
2.  **(推荐) 创建并激活虚拟环境**:
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # macOS / Linux:
    source venv/bin/activate
    ```
3.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **配置**:
    *   编辑 `config.py` 文件。
    *   **重要**: 修改 `SECRET_PASSWORD` 为一个强密码！这是添加/删除 URL 的凭证。
    *   根据需要调整 `HOST`, `PORT`, `FILTER_RULES`, `EXCLUDE_PARAMS` 等设置。
5.  **准备静态文件**:
    *   确保 `static/images/` 目录存在。如果不存在，请手动创建：`mkdir -p static/images` (Linux/macOS) 或使用文件浏览器创建。
    *   将你选择的宇宙背景图片放入 `static/images/` 目录，并确保其文件名与 `templates/index.html` 文件 CSS 中的 `background-image` URL 路径匹配 (默认为 `/static/images/space_background.jpg`)。
6.  **运行应用**:
    ```bash
    python app.py
    ```
    应用启动后，如果 `urls.json` 文件不存在，它会被自动创建。
7.  **访问**: 在浏览器中打开 `http://localhost:5002` (或你配置的地址和端口)。

## 🖱️ 使用说明

1.  **访问**: 打开浏览器，输入 Flask 应用运行的地址（默认为 `http://localhost:5002`）。
2.  **语言切换**: 点击页面顶部的 "English" 或 "中文" 按钮来切换界面语言。
3.  **随机访问**:
    *   点击 "Hyperspace Jump (超空间跳跃)" 按钮，会在消息区域显示一个随机博客文章的链接。
    *   点击 "Warp Scan (曲速扫描)" 按钮，会在消息区域显示一个随机博客主站的链接。
    *   点击消息区域显示的链接即可访问。
4.  **管理站点**:
    *   在 "Navigation Console (导航控制台)" 部分输入博客主站的完整 URL (包含 `http://` 或 `https://`)。
    *   输入在 `config.py` 中设置的 `SECRET_PASSWORD`。
    *   点击 "Log Coordinates (Add) / 记录坐标 (添加)" 按钮来添加 URL。
    *   点击 "Erase Coordinates (Delete) / 擦除坐标 (删除)" 按钮来删除 URL。
    *   操作结果会显示在主消息区域。密码错误会显示在输入框下方。
5.  **查看列表**: "Saved Coordinates (已存坐标)" 部分会列出所有已保存的站点名称和添加时间。

## 🐳 Docker 部署

### 1. 构建镜像

在包含 `Dockerfile` 的项目根目录下运行：

```bash
docker build -t cosmic-teleporter .
```
### 2. 运行容器
```
docker run -d \
  -p 5002:5002 \
  -v "$(pwd)/urls.json:/app/urls.json" \
  --name my-teleporter \
  cosmic-teleporter
```
