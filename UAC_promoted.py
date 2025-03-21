import subprocess

from logger import log_function_call


@log_function_call
def run_with_UAC(core_command: str) -> None:
    command = "Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile -Command & {" + \
        core_command + "}' -Verb RunAs"
    subprocess.run(
        ["pwsh", "-NoProfile", "-Command", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )