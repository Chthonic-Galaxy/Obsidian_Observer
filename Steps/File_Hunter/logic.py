import os
import datetime
from typing import Optional, List, Tuple, Iterator, Set
import fnmatch

class FileHunter:
    def __init__(self, path: str, patterns: List[str] = None, ignore: Optional[List[str]] = None,
                 min_size: Optional[int] = None, date: Optional[List[str]] = None):
        self.path = self._check_path(path)
        self.patterns = patterns or ["*"]
        self.ignore = set(ignore or [])
        self.min_size = min_size or 0
        self.date_filter = self._create_date_filter(date)

    @staticmethod
    def _check_path(path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Directory doesn't exist: {path}")
        return path

    @staticmethod
    def _create_date_filter(date_input: Optional[List[str]]) -> Optional[callable]:
        if not date_input:
            return None

        date = datetime.datetime.strptime(date_input[0], "%Y-%m-%d")
        option = date_input[1] if len(date_input) > 1 else "on"

        if option == "before":
            return lambda file_date: file_date < date
        elif option == "after":
            return lambda file_date: file_date > date
        else:  # "on" or any other input
            return lambda file_date: file_date.date() == date.date()

    def _fast_scandir(self, path: str) -> Iterator[Tuple[str, List[os.DirEntry], List[os.DirEntry]]]:
        try:
            with os.scandir(path) as it:
                dirs = []
                files = []
                for entry in it:
                    if not entry.is_symlink():
                        if entry.is_dir(follow_symlinks=False):
                            if entry.name not in self.ignore:
                                dirs.append(entry)
                        else:
                            files.append(entry)
                yield path, dirs, files
        except PermissionError:
            print(f"Permission denied: {path}")

    def _matches_criteria(self, entry: os.DirEntry) -> bool:
        try:
            return (
                any(fnmatch.fnmatch(entry.name, pat) for pat in self.patterns) and
                entry.stat().st_size >= self.min_size and
                (not self.date_filter or self.date_filter(datetime.datetime.fromtimestamp(entry.stat().st_mtime)))
            )
        except OSError:
            print(f"Error accessing file: {entry.path}")
            return False

    def file_search(self, addition_info: bool = False) -> Set[Tuple[str, float, int]] | Set[str]:
        matched_files = set()
        stack = [self.path]

        while stack:
            for current_path, dirs, files in self._fast_scandir(stack.pop()):
                stack.extend(entry.path for entry in dirs)
                for entry in files:
                    if self._matches_criteria(entry):
                        if addition_info:
                            stat = entry.stat()
                            matched_files.add((entry.path, stat.st_mtime, stat.st_size))
                        else:
                            matched_files.add(entry.path)

        return matched_files
