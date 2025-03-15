import json
from typing import Any, Dict, List


class ConfigManager:
    def __init__(self, config_path: str) -> None:
        self.config_path: str = config_path
        self._config: Dict[str, Dict[str, str]] = {}

    @property
    def config(self) -> Dict[str, Any]:
        if not self._config:
            self.load_config()
        return self._config

    def load_config(self) -> None:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)

    def get_bark_config(self) -> Dict[str, str]:
        return self.config.get('bark', {})

    def get_mumu_config(self) -> Dict[str, str]:
        return self.config.get('mumu', {})

    def get_arrange_config(self) -> Dict[str, Dict[str, str]]:
        return self.config.get('windows', {})

    def get_hotfix_config(self) -> Dict[str, Dict[str, str]]:
        return self.config.get('hotfix_remote', {})

    def get_launcher_common_config(self) -> Dict[str, str]:
        return self.config.get('launcher', {}).get('common', {})

    def get_launcher_maas_config(self) -> Dict[str, List[str]]:
        return self.config.get('launcher', {}).get('maa', {})
