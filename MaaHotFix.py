from typing import Dict, List

from config_manager import ConfigManager
from GitRepoDownload import GitRepoDownload


class Update():
    def __init__(self, config_path:str) -> None:
        self.info: Dict[str, Dict[str, str]] = ConfigManager(config_path).get_hotfix_config()

    def full(self, distribution: List[str]) -> None:
        repo = GitRepoDownload(self.info)
        repo.get_latest_commit_hash()
        repo.download()
        repo.unzip()
        for dst in distribution:
            repo.update(dst)
        repo.cleanup()
