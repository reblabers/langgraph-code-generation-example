from pathlib import Path
import subprocess


class Repository:
    def __init__(self, path: Path):
        self.path = path

    def clean(self):
        subprocess.run(["git", "reset", "--hard"], cwd=self.path, check=True)
        # subprocess.run(["git", "clean", "-fdx"], cwd=self.path)

    def test(self):
        subprocess.run(["mise", "x", "gradle", "--", "gradle", "test"], cwd=self.path, check=True)

    def test2(self) -> tuple[bool, str, str]:
        # 標準出力を取得
        result = subprocess.run(["mise", "x", "gradle", "--", "gradle", "test", "--info"], cwd=self.path, check=False, capture_output=True, text=True)
        # 成功失敗もpairで返す. 成功ならtrue, 失敗ならfalse
        return result.returncode == 0, result.stdout, result.stderr

    def format(self):
        subprocess.run(["mise", "x", "gradle", "--", "gradle", "ktlintFormat"], cwd=self.path, check=True)
