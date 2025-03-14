FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置时区为中国时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装系统依赖
RUN apt-get update && &#92;
    apt-get install -y --no-install-recommends cron && &#92;
    rm -rf /var/lib/apt/lists/*

# 复制所有程序文件
COPY main.py push.py config.py your_program4.py ./  # 替换 your_program4.py 为实际文件名

# 创建日志目录并设置权限
RUN mkdir -p /app/logs && chmod 777 /app/logs

# 直接安装 Python 依赖
RUN pip install --no-cache-dir &#92;
    requests>=2.32.3 &#92;
    urllib3>=2.2.3 &#92;
    && pip cache purge

# 配置 cron 任务
RUN echo "0 1 * * * cd /app && /usr/local/bin/python3 main.py >> /app/logs/&#92;$(date +&#92;%Y-&#92;%m-&#92;%d).log 2>&1" | tee /etc/cron.d/wxread-cron &#92;
    && chmod 0644 /etc/cron.d/wxread-cron &#92;
    && crontab /etc/cron.d/wxread-cron

# 启动命令
CMD ["sh", "-c", "service cron start && tail -f /dev/null"]
