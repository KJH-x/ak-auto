import os
import sys
from typing import List

import MaaReport
from config_manager import ConfigManager

batch_path = MaaReport.__file__
os.chdir(sys.path[0])

common_config_path = 'config/common.json'

common_config = ConfigManager(common_config_path)
maa_config = common_config.get_launcher_maas_config()
maa_instances: List[str] = maa_config["maa_instances"]
instance_count: int = len(maa_instances)
work_dir = os.path.dirname(batch_path)

for i in range(1, instance_count+1):

    start_batch_content = "\n".join([
        "@echo off>nul",
        "chcp 65001>nul",
        f"cd {work_dir}",
        " ".join([
            # "@REM",
            sys.executable, batch_path,
            "--action", '"startUpRecord"',
            "--group", str(i),
            "--message", '"任务开始"'
        ]),
    ])

    finish_batch_content = "\n".join([
        "@echo off>nul",
        "chcp 65001>nul",
        f"cd {work_dir}",
        " ".join([
            # "@REM",
            sys.executable, batch_path,
            "--action", '"finishKillReport"',
            "--group", str(i),
            "--message", '"任务完成"',
            "--quit", f"\"{i}\""
        ]),
    ])

    with open(f".\\bl\\S{i}.bat", "w", encoding="utf-8") as s:
        s.write(start_batch_content)
    with open(f".\\bl\\F{i}.bat", "w", encoding="utf-8") as s:
        s.write(finish_batch_content)
