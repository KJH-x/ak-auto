import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict
from urllib.parse import quote

from bark import bark
from config_manager import ConfigManager
from logger import log_function_call, setup_logger

logger = setup_logger()


@log_function_call
def stop_simulator(im_name: str, config: Dict[str, str]) -> None:
    MumuManager = os.path.join(config['MumuManagerPath'], "MumuManager.exe")
    cmd = f"\"{MumuManager}\" api -v {im_name} shutdown_player"
    logger.info(cmd)
    os.system(cmd)
    return None


@log_function_call
def stop_full() -> None:
    subprocess.Popen(
        "taskkill -f -im maa.exe -t",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    subprocess.Popen(
        "taskkill -f -im adb.exe -t",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return None


def report_time() -> str:
    return f"[{datetime.now().strftime('%H:%M:%S')}]"


@log_function_call
def process_finish_kill_report(group: str, message: str, simulator_name: str,  config: ConfigManager):
    with open(timelog_path, 'r+', encoding="utf-8") as file:
        time_rec = json.load(file)
        time_rec[0][group][1] = "off"
        file.seek(0)
        json.dump(time_rec, file)
        file.truncate()

    # 获取当前时间并计算持续时间
    start_time = datetime.strptime(time_rec[0][group][0], "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()
    duration = (current_time-start_time).seconds
    d_minutes = int(duration // 60)
    d_seconds = int(duration % 60)
    report_duration = f"历时{d_minutes}分{d_seconds}秒"

    logger.info(f"stop sim: {simulator_name}")
    stop_simulator(simulator_name, config.get_mumu_config())

    if {time_rec[0][str(x)][1] for x in time_rec[0]} == {"off"}:
        logger.info("全部完成")

    content = quote(f"{report_time()}[MAA][ {group} ] {message} {report_duration}")
    bark(content=content, config=config.get_bark_config())


@log_function_call
def process_start_up_record(group: str, message: str, config: ConfigManager):
    current_time = datetime.now()
    with open(timelog_path, 'r+', encoding="utf-8") as file:
        time_rec = json.load(file)
        time_rec[0][group] = [current_time.strftime("%Y-%m-%d %H:%M:%S"), "on"]
        file.seek(0)
        json.dump(time_rec, file)
        file.truncate()

    content = quote(f"{report_time()}[MAA][ {group} ] {message}")
    bark(content=content, config=config.get_bark_config())


def main() -> None:
    config_manager = ConfigManager(config_path)

    try:
        parser = argparse.ArgumentParser(description='auto report')

        parser.add_argument('--action', '-a', type=str, help='record / report')
        parser.add_argument('--group', '-g', type=str, help='sim-maa group')
        parser.add_argument('--message', '-m', type=str, help='extra message')
        parser.add_argument('--quit', '-q', type=str, help='simulator to stop')
        action = str(parser.parse_args().action)
        message = str(parser.parse_args().message)
        group = str(parser.parse_args().group)
        simulator_name = str(parser.parse_args().quit)

        # 打印接收到的参数
        logger.info(f"收到参数：{action},{message},{group},{simulator_name}")

        os.chdir(sys.path[0])

        if action == "finishKillReport" and group:
            process_finish_kill_report(group, message, simulator_name,
                                       config_manager)
        elif action == "startUpRecord" and group:
            process_start_up_record(group, message, config_manager)
        else:
            logger.warning("无效参数")

    except Exception as e:
        logger.error(f"发生错误: {e}")


if __name__ == '__main__':
    timelog_path = "./config/timeRecord.json"
    config_path = "./config/common.json"
    main()
