import os
import subprocess
import time
from typing import Dict

import requests

from logger import log_function_call, setup_logger

logger = setup_logger()


class GitRepoDownload:
    def __init__(self, info: Dict[str, Dict[str, str]]):
        self.username = info['repo_info']['username']
        self.reponame = info['repo_info']['reponame']
        self.header = info['headers']
        self.download_path = info['local']['download_path']
        # self.target_path = local_info['target_path']
        self.proxies = info['proxy']
        self.hash = None
        self.extract_path = None
        self.zip_path = None

    @log_function_call
    def get_latest_commit_hash(self) -> str:
        url = f'https://api.github.com/repos/{self.username}/{self.reponame}/commits'
        logger.info(f"Checking the latest commit for {self.username}/{self.reponame}")
        while True:
            try:
                response = requests.get(url, headers=self.header)
                # Raise for HTTP errors
                response.raise_for_status()
                break
            except requests.exceptions.ConnectionError as e:
                logger.error(f"An error occurred: {e}")
                time.sleep(5)  # Wait before retrying
        commits = response.json()
        # Update self.hash with the short hash
        self.hash = str(commits[0]['sha'][:7])
        logger.info(f"The Latest commit for {self.username}/{self.reponame} is {self.hash}")
        return self.hash

    @log_function_call
    def download(self) -> None:
        def _download_file(url: str, download_path: str) -> None:
            with requests.get(url, headers=self.header, proxies=self.proxies, stream=True) as response:
                response.raise_for_status()
                with open(download_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
        if self.hash:
            zip_url = f'https://github.com/{self.username}/{
                self.reponame}/archive/{self.hash}.zip'
            self.zip_path = os.path.join(
                self.download_path, f'{self.hash}.zip')
            if os.path.exists(self.zip_path):
                logger.info(f"Already Downloaded to {self.zip_path}, skipped")
                return
            while True:
                try:
                    _download_file(zip_url, self.zip_path)
                    logger.info(f"Downloaded {zip_url} to {self.zip_path}")
                    break
                except Exception as e:
                    logger.error(f"An error occurred: {e}")
                    time.sleep(5)

    @log_function_call
    def unzip(self) -> None:
        if self.hash and self.zip_path and os.path.exists(self.zip_path):
            self.extract_path = os.path.join(self.download_path, self.hash)
            if not os.path.exists(self.extract_path):
                os.makedirs(self.extract_path)
                subprocess.run(['7z', 'x', self.zip_path,
                                f'-o{self.extract_path}', '-y'], check=True)
                logger.info(f"Unzipped {self.zip_path} \n -> {self.extract_path}")
            else:
                logger.info("Unzipped have done before, skipping...")

    @log_function_call
    def update(self, to_path: str) -> None:
        if self.extract_path:
            if os.path.exists((hotfixVersion := os.path.join(to_path, "hotfixVersion.txt"))):
                with open(hotfixVersion, mode='r', encoding='utf8') as version:
                    if version.readlines()[0] == self.hash:
                        logger.info(f"Dir {to_path} is Up-to-date")
                        return
            for root in os.listdir(self.extract_path):
                for item in os.listdir(os.path.join(self.extract_path, root)):
                    source_item = os.path.join(self.extract_path, root, item)
                    target_item = os.path.join(to_path, item)
                    logger.info(f"Copy -> {target_item}")
                    if os.path.isdir(source_item):
                        subprocess.run(['xcopy', source_item, target_item, '/E',
                                       '/H', '/C', '/I', '/Y', '/Q'], shell=True, check=True)
                    else:
                        subprocess.run(
                            ['xcopy', source_item, target_item, '/Y', '/Q'], shell=True, check=True)
            with open(hotfixVersion, mode='w', encoding='utf8') as version:
                version.write(str(self.hash))
            logger.info(f"Dir {to_path} is updated")

    @log_function_call
    def cleanup(self) -> None:
        import shutil
        if self.hash:
            for fileOrFolder in [_ for _ in os.listdir(self.download_path) if not _.startswith(self.hash)]:
                full_path = os.path.join(self.download_path, fileOrFolder)
                logger.info(f"Deleting Old updates: {fileOrFolder}")
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                elif os.path.exists(full_path):
                    os.remove(full_path)


if __name__ == "__main__":
    example_info = {
        "repo_info": {
            "username": "your-username",
            "reponame": "your-reponame"
        },
        "proxy": {
            'http': "http://your-proxy:port",
            'https': "http://your-proxy:port"
        },
        "headers": {
            "user-agent": "your-user-agent"
        },
        "local": {
            "download_path": "path/to/download",
            "target_path": "path/to/target"
        }
    }
    repo = GitRepoDownload(example_info)
    repo.get_latest_commit_hash()
    repo.download()
    repo.unzip()
    repo.update(example_info['local']['target_path'])
