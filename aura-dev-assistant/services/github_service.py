import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests
from git import Repo

from services.project_service import ProjectService


class GitHubService:
    def analyze_repository(self, repo_url: str, max_files: int = 45, max_chars: int = 2200) -> dict[str, str]:
        if "github.com" not in repo_url:
            raise ValueError("Only GitHub repository URLs are supported.")

        temp_root = Path(tempfile.mkdtemp(prefix="aura_repo_"))
        try:
            repo_dir = temp_root / "repo"
            Repo.clone_from(repo_url, repo_dir, depth=1)
            project_data = ProjectService().analyze_directory(
                repo_dir, max_files=max_files, max_chars=max_chars
            )
            readme = self._read_readme(repo_dir) or self._fetch_readme(repo_url)
            context = (
                f"Repository URL: {repo_url}\n\n"
                f"README:\n{readme[:6000]}\n\n"
                f"Repository tree:\n{project_data['tree']}\n\n"
                f"File samples and summaries:\n{project_data['context']}"
            )
            return {"tree": project_data["tree"], "context": context}
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)

    @staticmethod
    def _read_readme(repo_dir: Path) -> str:
        for name in ["README.md", "readme.md", "README.txt", "README"]:
            path = repo_dir / name
            if path.exists():
                return path.read_text(encoding="utf-8", errors="ignore")
        return ""

    @staticmethod
    def _fetch_readme(repo_url: str) -> str:
        token = os.getenv("GITHUB_TOKEN")
        parsed = urlparse(repo_url)
        parts = parsed.path.strip("/").replace(".git", "").split("/")
        if len(parts) < 2:
            return ""
        api_url = f"https://api.github.com/repos/{parts[0]}/{parts[1]}/readme"
        headers = {"Accept": "application/vnd.github.raw"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            response = requests.get(api_url, headers=headers, timeout=12)
            if response.ok:
                return response.text
        except requests.RequestException:
            return ""
        return ""
