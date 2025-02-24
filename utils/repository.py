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

    def format(self):
        subprocess.run(["mise", "x", "gradle", "--", "gradle", "ktlintFormat"], cwd=self.path, check=True)
