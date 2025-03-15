import logging
from functools import wraps
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Callable


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("MaaScriptRT")

    if logger.handlers:
        logger.debug("[Warning] Logger 再次实例化")
        return logger

    logger.setLevel(logging.DEBUG)  # 让 logger 记录 DEBUG 及以上级别的日志

    # 控制台输出 INFO 及以上级别
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(message)s", datefmt='%H:%M:%S'
    ))

    # 文件输出 DEBUG 及以上级别
    file_handler = TimedRotatingFileHandler(
        "logs/MaaScriptRT.log",
        when="midnight",
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)8s | %(filename)20s | %(message)s"
    ))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def log_function_call(func: Callable[..., Any]):
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f"[Function call] 调用 {func.__name__}，参数: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"[Function call] 函数 {func.__name__} 返回: {result}")
        return result
    return wrapper


logger = setup_logger()
