import json
import os
import subprocess
import sys
import time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List

# from requests.exceptions import ConnectTimeout
# import multiprocessing as mp
# from bark import bark
from Arrange_windows import arrange
from config_manager import ConfigManager
from logger import log_function_call, setup_logger
from MaaHotFix import Update

logger = setup_logger()

common_config_path = 'config/common.json'
maa_config_path = 'config/gui.json'
common_config = ConfigManager(common_config_path)
launcher_config = common_config.get_launcher_common_config()
maa_config = common_config.get_launcher_maas_config()
# bark_config = common_config.get_bark_config()

MumuManager: str = launcher_config["MumuManager"]
MumuADB: str = launcher_config["MumuADB"]
maa_root: str = launcher_config["maa_root"]

# Generator:
# f"{[f"{i:02d}_Instance_{i}" for i in range(1, 6)]}".replace("\'","\"")
maa_instances: List[str] = maa_config["maa_instances"]
maa_configs: List[str] = maa_config["maa_configs"]
instance_count: int = len(maa_instances)


@log_function_call
def report_time() -> str:
    return f"[{datetime.now().strftime('%H:%M:%S')}]"


@log_function_call
def start_MAA() -> None:
    for ins, index in zip(maa_instances, range(instance_count)):
        logger.info(f"starting MAA: A{index+1}")
        command = [
            os.path.join(maa_root, ins, "Maa.exe"),
            "--config", maa_configs[index]
        ]
        subprocess.Popen(
            command, creationflags=subprocess.CREATE_NEW_CONSOLE)
        wait(5, "operation interval")


def wait(sleep_sec: int, msg: str = "") -> None:
    logger.info(f"<{sleep_sec:3d}s> [{msg}]")
    time.sleep(sleep_sec)
    return


@log_function_call
def common_command(command: str = "") -> list[str]:
    result_combination: list[str] = []
    result = subprocess.run(
        [command], shell=True, stdout=subprocess.PIPE, text=True
    )
    result_combination = result.stdout.splitlines()
    return result_combination


@log_function_call
def command_adb(command: str = "") -> list[str]:
    result_combination: list[str] = []
    result = subprocess.run(
        [MumuADB, command],
        shell=True, stdout=subprocess.PIPE, text=True
    )
    result_combination = result.stdout.splitlines()
    return result_combination


@log_function_call
def command_all(command_prefix: str, command_suffix: str, indexes: List[str], interval: float = 0) -> list[list[str]]:
    result_combination: list[list[str]] = []
    for index in indexes:
        result = subprocess.run(
            [MumuManager, command_prefix, "-v", index, command_suffix],
            shell=True, stdout=subprocess.PIPE, text=True
        )
        time.sleep(interval)
        result_combination.append(result.stdout.splitlines())
    return result_combination


@log_function_call
def command_byIndex(index: int, command_prefix: str, command_suffix: str = "", interval: float = 0) -> list[str]:
    result_combination: list[str] = []
    result = subprocess.run(
        [MumuManager, command_prefix, "-v", str(index), command_suffix],
        shell=True, stdout=subprocess.PIPE, text=True
    )
    result_combination = result.stdout.splitlines()
    return result_combination


@log_function_call
def update_ports(addr_list: list[str]) -> None:
    for instance, addr, index in zip(maa_instances, addr_list, range(instance_count)):
        with open(os.path.join(maa_root, instance, maa_config_path), mode="r", encoding="utf-8") as config_fp:
            config: Dict[str, Any] = dict(json.load(config_fp))
        del config_fp

        config["Configurations"][maa_configs[index]]["Connect.Address"] = addr
        config["Configurations"][maa_configs[index]]["Connect.AddressHistory"] = f"[\"{str(
            addr).replace('\'', '\"')}\"]"
        config["Configurations"][maa_configs[index]]["Connect.AdbPath"] = MumuADB

        with open(os.path.join(maa_root, instance, maa_config_path), mode="w", encoding="utf-8") as config_fp:
            json.dump(config, config_fp, indent=2, ensure_ascii=False)

        logger.info(f'{index+1}: adb addr set to: {addr}')


@log_function_call
def run_with_UAC(core_command: str) -> None:
    command = "& {Start-Process pwsh -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command \"& {" + \
        core_command+"} \"' -Verb RunAs}"
    subprocess.run(
        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True
    )


@log_function_call
def kill_any_port(port: int) -> None:
    # Privilege required to avoid UAC control prompt
    run_with_UAC(f"Stop-Process -Id (Get-NetTCPConnection -LocalPort " +
                 str(port) + " -ErrorAction Stop).OwningProcess")


@log_function_call
def taskkill(ProcessName: str) -> None:
    # Privilege required to avoid UAC control prompt
    run_with_UAC(f"Stop-Process -Name {ProcessName} -Force -ErrorAction SilentlyContinue")


if __name__ == '__main__':
    # Set run path
    # os.chdir(sys.path[0])
    # Force UTF-8 console
    os.system("chcp 65001>nul|cls")
    logger.info("挂机系统启动器")

    debug_flags = {
        "skip_update": True,
        "skip_shutdown": True,
        "skip_startup": True,
        "skip_arrange": False,
    }

    # Deprecated. Nothing to report
    # report_content = ""
    # bark_sub = mp.Process(target=bark, args=(report_content, bark_config))

    # MAA resource update
    if not debug_flags["skip_update"]:
        try:
            logger.info("Checking Resources Updates for MAA...")
            Update(common_config_path).full([os.path.join(maa_root, i) for i in maa_instances])
            logger.info("Finished Updating.")
        except Exception as e:
            logger.info("Update Error.")
            logger.error(str(e))
        except KeyboardInterrupt as e:
            logger.warning(f"{e}\nCtrl+C, Skip")
            pass

    # Shutdown Active Clients
    if not debug_flags["skip_shutdown"]:
        try:
            # Count down
            for i in range(10, 0, -1):
                wait(1, f"Starting in {i:2d}")

            # Shutdown MAA
            logger.info("Shutdown MAA")
            taskkill("maa")
            # Shutdown ADB
            logger.info("Shutdown ADB")
            taskkill("adb")

            # Shutdown Players
            logger.info("Killing Plyaers...")
            command_all("api", "shutdown_player", maa_config["indexes"])
            wait(20, "Wait for shutdown complete")

            # Force clear
            run_with_UAC("MuMuVMMSVC")
            run_with_UAC("MuMuPlayerService")
            run_with_UAC("MuMuPlayer")

        except KeyboardInterrupt as e:
            print("Ctrl+C, Skip")
            pass

    # Start Up
    if not debug_flags["skip_startup"]:
        try:
            # Launch Players
            logger.info("Launching Plyaers...")
            command_all("api", "launch_player", maa_config["indexes"], interval=10)

            # Check state, Using MumuManager
            # "check player state: state=start_finished."
            while True:

                logger.info("Checking Plyaers status...")
                checks = command_all("api", "player_state", maa_config["indexes"])
                state_all = set()
                for check, index in zip(checks, range(1, instance_count + 1)):
                    if "start_finished" not in check[1]:
                        state_all.add(index)
                if not state_all:
                    break
                else:
                    wait(1, f"Player {state_all} is not ready.")

            logger.info("Players Launched.")

            # Start adb, Connect ADB to Players, Check Connect State
            command_adb("devices")
            retry_count = 0
            while True:
                logger.info("Connectting to ADB ")
                command_all("adb", "connect", maa_config["indexes"])
                logger.info("Checking ADB devices state...")
                adb_state_response: List[str] = command_adb("devices")[1:instance_count+1]
                adb_state = [state.split("\t")[1] for state in adb_state_response]
                if set(adb_state) == {"device"} and len(adb_state) == instance_count:
                    addr_list = [state.split("\t")[0] for state in adb_state_response]
                    logger.info("ADB Ports Fected.")
                    break
                else:
                    retry_count += 1
                    logger.info("ADB connect failed...")
                    command_adb("kill-server")
                    if retry_count == 10:
                        kill_any_port(5037)
                    elif retry_count > 10:
                        raise SystemError("Failed to link adb")
                    wait(1, f"Retrying:{retry_count}")

            logger.info("ADB Connection OK.")

            # Launch Arknights
            logger.info("Launching Arknights ...")
            command_all("api", "launch_app com.hypergryph.arknights", maa_config["indexes"], interval=15)
            logger.info("Arknights Launched.")

            # report_content = "; ".join([addr.split(":")[1] for addr in addr_list])
            # bark_sub = mp.Process(target=bark, args=(report_content, api, key, icon))
            # bark_sub.start()

            # write ADB Ports and adb path:
            update_ports(addr_list)
            logger.info("Configs Upadted.")
            # Start MAA
            start_MAA()
            logger.info("MAA Started.")

        except KeyboardInterrupt:
            input("操作打断")

    # Arrange Windows
    if not debug_flags["skip_arrange"]:
        try:
            arrange(common_config_path)
            logger.info("Windows Arranged.")

            logger.info("ALL DONE!")
            wait(25, "Wait to exit")

            sys.exit(0x0)

        except KeyboardInterrupt:
            input("操作打断")

        except Exception as EXPT:
            logger.info(msg=EXPT)
            logger.error("Error Occurred.")
            wait(3600, "Error Wait")

        finally:
            # print("调试终点")
            try:
                # bark_sub.join()
                pass
            # except ConnectTimeout as e:
                # logger.info(msg=f"bark超时")
                # logger.error("Error Occurred.")
            # except NameError as e:
                # logger.error("Error Occurred.")
                # wait(3600, "Error Wait")
            finally:
                sys.exit(0x0)
