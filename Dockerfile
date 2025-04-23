# --- 第一阶段：基础镜像 ---
# 使用官方 Python 运行时作为父镜像
# 使用 slim 版本以减小镜像大小
FROM python:3.10-slim

# --- 环境变量 ---
# 设置容器内的工作目录
WORKDIR /app

# --- 安装依赖 ---
# 首先只复制需求文件以利用 Docker 层缓存
COPY requirements.txt .

# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt

# --- 复制应用程序代码 ---
# 将应用程序的其余文件复制到工作目录
# 包括 app.py, config.py, templates/, static/
# 注意：如果 urls.json 尚不存在，默认不会被复制。
#       最好将其作为卷挂载以实现持久化。
COPY . .

# --- 暴露端口 ---
# 暴露应用程序运行的端口 (在 config.py 中定义)
# 这是文档说明；实际端口映射在 `docker run` 时进行
EXPOSE 5002

# --- 定义运行命令 ---
# 使用 Flask 开发服务器运行应用程序的命令
# 对于生产环境，请考虑使用 Gunicorn 或 uWSGI 等生产级服务器
# Gunicorn 示例命令 (需要先通过 requirements.txt 安装 gunicorn):
# CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]
CMD ["python", "app.py"]