# 使用 Python 3.10 的精简版镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置时区为中国时区
ENV TZ=Asia/Shanghai
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# 复制程序文件
COPY main.py push.py config.py your_program4.py ./  # 替换 your_program4.py 为实际文件名

# 复制 Python 依赖文件
COPY requirements.txt .  

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt && pip cache purge

# 创建日志目录并设置权限
RUN mkdir -p /app/logs && chmod 777 /app/logs

# 配置 cron 任务
RUN echo "0 1 * * * cd /app && /usr/local/bin/python3 main.py >> /app/logs/\$(date +\%Y-\%m-\%d).log 2>&1" > /etc/cron.d/wxread-cron && \
    chmod 0644 /etc/cron.d/wxread-cron && \
    crontab /etc/cron.d/wxread-cron

# 启动 cron 并保持容器运行
CMD ["sh", "-c", "service cron start && tail -f /dev/null"]