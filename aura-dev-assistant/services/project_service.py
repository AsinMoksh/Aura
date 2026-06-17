import ast
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import BinaryIO


TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".h",
    ".cs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
    ".txt",
    ".sql",
    ".sh",
    ".ps1",
}

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".next"}


class ProjectService:
    def analyze_zip(self, uploaded_file: BinaryIO, max_files: int = 60, max_chars: int = 1800) -> dict:
        temp_root = Path(tempfile.mkdtemp(prefix="aura_zip_"))
        try:
            zip_path = temp_root / "project.zip"
            zip_path.write_bytes(uploaded_file.getbuffer())
            extract_dir = temp_root / "project"
            extract_dir.mkdir()
            with zipfile.ZipFile(zip_path) as archive:
                self._safe_extract(archive, extract_dir)
            return self.analyze_directory(extract_dir, max_files=max_files, max_chars=max_chars)
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)

    def analyze_directory(self, root: Path, max_files: int = 60, max_chars: int = 1800) -> dict:
        files = self._collect_files(root, max_files)
        tree = self._build_tree(root)
        file_summaries = []
        context_parts = [f"Project tree:\n{tree}\n"]

        for path in files:
            rel = path.relative_to(root).as_posix()
            content = path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
            summary = self._summarize_file(path, content)
            file_summaries.append({"path": rel, "summary": summary})
            context_parts.append(f"\nFILE: {rel}\nSUMMARY: {summary}\nCONTENT SAMPLE:\n{content}\n")

        return {
            "tree": tree,
            "file_summaries": file_summaries,
            "context": "\n".join(context_parts),
        }

    @staticmethod
    def _safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
        destination_resolved = destination.resolve()
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if not target.is_relative_to(destination_resolved):
                raise ValueError("ZIP contains an unsafe path.")
        archive.extractall(destination)

    @staticmethod
    def _collect_files(root: Path, max_files: int) -> list[Path]:
        collected: list[Path] = []
        for path in root.rglob("*"):
            if path.is_dir():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if path.stat().st_size > 350_000:
                continue
            collected.append(path)
            if len(collected) >= max_files:
                break
        return collected

    @staticmethod
    def _build_tree(root: Path, limit: int = 220) -> str:
        lines: list[str] = []
        count = 0
        for path in sorted(root.rglob("*")):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            rel_parts = path.relative_to(root).parts
            if not rel_parts:
                continue
            indent = "  " * (len(rel_parts) - 1)
            suffix = "/" if path.is_dir() else ""
            lines.append(f"{indent}{rel_parts[-1]}{suffix}")
            count += 1
            if count >= limit:
                lines.append("... tree truncated ...")
                break
        return "\n".join(lines) or "(empty project)"

    def _summarize_file(self, path: Path, content: str) -> str:
        if path.suffix.lower() == ".py":
            return self._summarize_python(content)
        first_line = next((line.strip() for line in content.splitlines() if line.strip()), "")
        return f"{path.suffix or 'Text'} file. First notable line: {first_line[:180] or 'No text content.'}"

    @staticmethod
    def _summarize_python(content: str) -> str:
        try:
            tree = ast.parse(content)
        except SyntaxError as exc:
            return f"Python file with syntax issue near line {exc.lineno}: {exc.msg}"

        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)

        parts = ["Python module"]
        if imports:
            parts.append(f"imports {', '.join(imports[:8])}")
        if classes:
            parts.append(f"classes: {', '.join(classes[:8])}")
        if functions:
            parts.append(f"functions: {', '.join(functions[:12])}")
        return "; ".join(parts) + "."
