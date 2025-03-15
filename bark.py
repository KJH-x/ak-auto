import subprocess
from typing import Dict
from urllib.parse import quote, urlencode

from logger import log_function_call


@log_function_call
def bark(content: str, config: Dict[str, str]) -> None:
    args = [
        ('icon', config['icon']),
        ('level', config['level']),
        ('group', config['group']),
    ]
    arg = urlencode(args)
    title = quote('AUTO Notification')

    url = f'https://{config['ApiUrlBase']}/{config['ApiKey']}/{title}/{content}/?{arg}'
    subprocess.Popen(
        ["curl", "-s", "-o", "/dev/null", url],
        start_new_session=True
    )
    return
