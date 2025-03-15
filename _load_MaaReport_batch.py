import os
import sys

import MaaReport

batch_location = MaaReport.__file__
os.chdir(sys.path[0])


for i in range(1, 6):

    start_batch_content = "\n".join([
        "@echo off>nul",
        "chcp 65001>nul",
        " ".join([
            # "@REM",
            sys.executable, batch_location,
            "--action", '"startUpRecord"',
            "--group", str(i),
            "--message", '"任务开始"'
        ]),
    ])

    finish_batch_content = "\n".join([
        "@echo off>nul",
        "chcp 65001>nul",
        " ".join([
            # "@REM",
            sys.executable, batch_location,
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
