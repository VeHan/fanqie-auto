import logging

# 配置日志记录系统
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format='%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s',  # 设置日志格式
    handlers=[
        logging.StreamHandler(),  # 将日志输出到控制台
        logging.FileHandler('app.log')  # 将日志输出到文件
    ]
)

# 获取一个日志记录器（默认是 root 记录器）
logger = logging.getLogger(__name__)