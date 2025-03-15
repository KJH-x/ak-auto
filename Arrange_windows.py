# pyright: reportUnknownMemberType = false

import ctypes

import win32api
import win32con
import win32gui

from config_manager import ConfigManager
from logger import log_function_call, setup_logger

# 初始化日志
logger = setup_logger()

ctypes.windll.shcore.SetProcessDpiAwareness(True)

# Alt 键 键码
VK_MENU = 0x12


@log_function_call
def match_title(partial_title: str) -> list[tuple[int, str]]:
    """
    通过部分标题查找窗口
    :param partial_title: 部分标题
    :return: 匹配到的窗口列表
    """
    def callback(hwnd: int, windows: list[tuple[int, str]]):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if partial_title.lower() in window_title.lower():
                windows.append((hwnd, window_title))
        return True
    windows: list[tuple[int, str]] = []
    win32gui.EnumWindows(callback, windows)
    return windows

@log_function_call
def set_pos(hwnd: int, pos: tuple[int, int, int, int]) -> None:
    """
    设置窗口位置
    :param hwnd: 窗口句柄
    :param pos: 窗口位置信息，包括左上角坐标和宽高
    :return: None
    """
    try:
        x, y, width, height = pos
        win32gui.SetWindowPos(
            hwnd,
            0, x, y, width, height, win32con.SWP_SHOWWINDOW
        )

        # 调用SetForegroundWindow前需要模拟点按alt，否则会抛出错误信息：
        # (0, 'SetForegroundWindow', 'No error message is available')
        win32api.keybd_event(VK_MENU, 0, 0, 0)
        win32api.keybd_event(VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

        # 设为当前最高
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        logger.error(f"设置窗口位置失败 - 句柄: {hwnd}, 位置: {pos}, 错误: {e}")


@log_function_call
def test_pos(title: str, x: int, y: int, w: int, h: int) -> tuple[int, int, int, int]:
    """
    测试窗口位置并返回窗口矩形信息, 位置设置是否符合预期
    :param title: 窗口标题
    :param x: 窗口左上角横坐标
    :param y: 窗口左上角纵坐标
    :param w: 窗口宽度
    :param h: 窗口高度
    :return: 窗口矩形信息元组 (left, top, right, bottom)
    """
    try:
        win32gui.SetWindowPos(
            win32gui.FindWindow(None, title),
            0, x, y, w, h, win32con.SWP_SHOWWINDOW
        )
        return win32gui.GetWindowRect(win32gui.FindWindow(None, title))
    except Exception as e:
        logger.error(f"测试窗口位置失败 - 标题: {title}, 位置: ({x},{y},{w},{h}), 错误: {e}")
        raise


class WindowManager:
    def __init__(self, windows_order: dict[str, dict[str, str]]):
        self.windows_info: dict[str, dict[str, str]] = windows_order

    @log_function_call
    def update_windows_info(self) -> None:
        try:
            for _, window_info in self.windows_info.items():
                info = match_title(str(window_info.get("name")))
                if not info:
                    logger.warning(f"未找到匹配窗口: {window_info.get('name')}")
                    window_info["name"] = ""
                else:
                    window_info["name"] = info[0][1]
                    window_info["hwnd"] = str(win32gui.FindWindow(None, info[0][1]))
                    logger.info(f"找到窗口: {info[0][1]}, 句柄: {window_info['hwnd']}")
        except Exception as e:
            logger.error(f"更新窗口信息失败: {e}")

    @log_function_call
    def arrange_position(self) -> None:
        for _, order in self.windows_info.items():
            if order.get("name") != "":
                hwnd = order["hwnd"]
                set_pos(int(hwnd), (int(order["x"]), int(order["y"]), int(order["w"]), int(order["h"])))


@log_function_call
def arrange(config_path:str):
    wm = WindowManager(ConfigManager(config_path).get_arrange_config())
    wm.update_windows_info()
    wm.arrange_position()


if __name__ == '__main__':
    config_path = "./config/common.json"
    arrange(config_path)