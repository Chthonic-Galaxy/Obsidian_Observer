import os
import fnmatch

class FileHunter:
    def __init__(
        self,
        path: str = os.getcwd(),
        pattern: str = "*",
        ignore: list[str] = None,
        min_size: int | None = None,
        date = None
    ):
        self.path = self._check_path(path)
        self.pattern = pattern
        self.ignore = ignore
        self.min_size = min_size
        self.date = date
        
        

    @staticmethod
    def _check_path(path):
        if not os.path.exists(path):
            raise FileNotFoundError("Dir doesn't exists")
        return path
        
    def file_search(self) -> set | str:
        matched_files = set()
        stack = [self.path]
        
        while stack:
            with os.scandir(stack[-1]) as scan:
                stack.pop()
                for item in scan:
                    item_name = f"{item.name}/" if item.is_dir() else item.name
                    restrictions = (
                        (item.stat().st_size >= self.min_size) if self.min_size else True,
                        ((item_name not in self.ignore) if self.ignore else True),
                    )
                    
                    if all(restrictions):
                        if item.is_file(follow_symlinks=False) and fnmatch.fnmatch(item.name, self.pattern):
                            matched_files.add(os.path.realpath(item))
                        elif item.is_dir(follow_symlinks=False):
                            stack.append(os.path.realpath(item))
        return matched_files if matched_files else "Nothing was founded"
