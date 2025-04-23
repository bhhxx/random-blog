# config.py
# 主页面主题
MAXI_PAGE = "index.html"
DEFAULT_BACKGROUND_IMAGE = "images/space_background.jpg"
BACKGROUND_CONFIG_FILE = "static/background_setting.json"
# 文件路径配置
URL_FILE = "urls.json"

# 服务器配置
HOST = "0.0.0.0"
PORT = 5002
DEBUG = True

# 网络配置
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）

# 爬取过滤规则
FILTER_RULES = [
    r'/tags?/',      # 过滤 /tag/ 和 /tags/
    r'/archives/',   # 过滤 /archives/
    r'/categories/', # 过滤 /categories/
    r'/search/',     # 过滤 /search/
    r'/posts/'
]

EXCLUDE_PARAMS = ['=tag', '=tags']  # 排除URL参数
# 爬取配置
UserAgent = "https://github.com/bhhxx/random-blog"
# 密码
SECRET_PASSWORD = "xxxxxxxx"