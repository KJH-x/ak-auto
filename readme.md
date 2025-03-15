## MAA+MuMu 自动化脚本套件

### 项目概述

本项目是一个用于管理 MAA 和 Mumu 模拟器的自动化脚本套件，包含模拟器控制、任务报告、窗口管理、资源更新等功能。

### 主要功能模块

1. **MaaReport**  
   - 任务开始/结束记录
   - 模拟器控制
   - 任务时长统计
   - 通知推送

2. **MumuLauncher**  
   - 模拟器批量启动
   - ADB 连接管理
   - MAA 程序启动
   - 窗口自动排列

3. **MaaHotFix**  
   - 资源自动更新
   - 版本管理
   - 资源清理

4. **WindowManager**  
   - 窗口位置管理
   - 窗口自动排列
   - 窗口状态检测

5. **Bark 通知**  
   - 任务状态推送
   - 自定义通知内容
   - 通知分组管理

### 配置文件说明

配置文件使用 JSON 格式，主要包含以下配置项：

```json
{
    "bark": {
        "icon": "图标URL",
        "level": "通知级别",
        "group": "通知分组",
        "ApiKey": "Bark API Key",
        "ApiUrlBase": "Bark 服务器地址"
    },
    "mumu": {
        "MumuManagerPath": "模拟器管理器路径"
    },
    "windows": {
        "窗口标识": {
            "name": "窗口名称",
            "x": "窗口X坐标",
            "y": "窗口Y坐标", 
            "w": "窗口宽度",
            "h": "窗口高度"
        }
    },
    "hotfix_remote": {
        "repo_info": {
            "username": "GitHub 用户名",
            "reponame": "仓库名称"
        },
        "proxy": {
            "http": "HTTP 代理地址",
            "https": "HTTPS 代理地址"
        },
        "headers": {
            // HTTP 请求头配置
        },
        "local": {
            "download_path": "资源下载路径"
        }
    },
    "launcher": {
        "common": {
            "MumuManager": "模拟器管理器路径",
            "MumuADB": "ADB 路径",
            "maa_root": "MAA 根目录"
        },
        "maa": {
            "maa_instances": ["实例1", "实例2"],
            "maa_configs": ["配置1", "配置2"],
            "indexes": ["1", "2"]
        }
    }
}
```

### 使用说明

1. 安装依赖

    ```bash
    pip install -r requirements.txt
    ```

2. 配置环境

    - 复制 `common.template.json` 为 `common.json`
    - 根据实际情况修改配置

3. 运行脚本

    - 启动模拟器：`python mumu_launcher.py`
    - 生成批处理文件：`python _load_MaaReport_batch.py`

### 注意事项

- 请确保配置文件中所有路径均为绝对路径
- 使用前请仔细检查配置文件
- 建议在 Windows 系统下运行
- 需要安装 MuMu 模拟器并配置好环境变量

### 依赖项

- Python 3.8+
- win32api
- requests
- pywin32

### 文件结构

``` bash
.
├── _load_MaaReport_batch.py    # 批处理文件生成
├── Arrange_windows.py          # 窗口管理
├── bark.py                     # 通知模块
├── config_manager.py           # 配置管理
├── GitRepoDownload.py          # 资源下载
├── logger.py                   # 日志模块
├── MaaHotFix.py                # 资源更新
├── MaaReport.py                # 任务报告
├── mumu_launcher.py            # 模拟器启动
├── config/
│   ├── common.schema.json      # 配置校验规则
└── README.md                   # 说明文档
```

### 许可证

本项目采用 MIT 许可证
