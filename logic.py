import os
import hashlib
import datetime
from typing import Optional, List, Tuple, Iterator, Set
import re
import fnmatch

class TreeMockConstructer:
    
    def __init__(self, path) -> None:
        self.path = path
        self.tree = {}
    
    def construct_tree_iterative(self):

        stack = [(self.path, self.tree)]

        while stack:
            current_path, current_dict = stack.pop()

            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)

                if os.path.isdir(item_path):
                    current_dict[item] = {}
                    stack.append((item_path, current_dict[item]))
                else:
                    size = os.path.getsize(item_path)
                    timestamp = os.path.getmtime(item_path)
                    modified_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    current_dict[item] = (
                        size,
                        modified_time
                    )
        
        return self.tree
    
    def tree_viewer(self):
        if not self.tree:
            self.construct_tree_iterative()
            if not self.tree:
                return "This directory is empty"
        
        mem = [self.tree.copy()]
        output = [f"{self.path if self.path.endswith("/") else f"{self.path}/"}"]
        depth = 0

        while mem:
            cur_tree = mem[-1].copy()
            depth = len(mem)
            for item in cur_tree:
                if cur_tree[item]:
                    if not isinstance(cur_tree[item], tuple):
                        del mem[-1][item]
                        mem.append(cur_tree[item])
                        output.append(f"\n{'  '*depth}{item}")
                        break
                    else:
                        output.append(f"\n{'  '*depth}{item} (size={cur_tree[item][0]}, modified_time={cur_tree[item][1]})")
                        del mem[-1][item]
                else:
                    del mem[-1][item]
            if not mem[-1]:
                mem.pop()

        res = ""
        for line in output:
            res += line

        return res
    
    
    
class TreeCreator:
    def __init__(self, root_path: str, depth_unit: int, structure: list[str], *, force: bool = False) -> None:
        self.root_path = root_path
        self.depth_unit = depth_unit
        self.structure = structure
        self.force = force
        self._tree_creator()
        
    def _tree_parser(self):
        regex = re.compile(r"^\s*(.*?)\s*(\((\d+)\))?\s*$")
        items = []
        for string in self.structure:
            match = regex.match(string)
    
            if match:
                spaces = len(match.group(0)) - len(match.group(0).lstrip())
                name = match.group(1).rstrip()
                is_directory = string.rstrip().endswith("/")
                data = None
                if not is_directory:
                    if match.group(3):
                        data = int(match.group(3))
                    else:
                        data = 0
                items.append({"name": name, "data": data, "spaces": spaces, "is_directory": is_directory})
        return items if items else None
    
    def _path_creator(self):
        paths = []
        current_path = self.root_path
        previous = [(current_path, -1)]
        
        for item in self._tree_parser():
            depth = item["spaces"] // self.depth_unit
            
            while previous and depth <= previous[-1][1]:
                previous.pop()
            
            if not previous:
                current_path = self.root_path
                previous = [(current_path, -1)]
            
            current_path = previous[-1][0] + item["name"]
            
            if item["data"] is not None:
                paths.append((current_path, item["data"]))
            else:
                paths.append((current_path,))
            
            previous.append((current_path, depth))
        
        return paths
    
    def _tree_creator(self):
        dirs, files = [], []
        for item in self._path_creator():
            if len(item) == 2:
                files.append(item)
            else:
                dirs.append(item[0])
        for path in dirs:
            os.makedirs(path, exist_ok=True)
        for item in files:
            if not os.path.exists(item[0]) or self.force:
                if os.path.exists(item[0]):
                    print(f"[FORCED REWRITE] => '{item[0]}' because is already exists")
                with open(item[0], "w", encoding="utf8") as file:
                    file.write(f"{' '*item[1]}")
            else:
                print(f"[SKIPING] => '{item[0]}' is already exists")
                
                
class Deduplication:
    def __init__(
        self,
        path: str,
        min_size: int = 0,
        ignore: list[str] = None
    ):
        self._config = self._config_handler()
        self.path = self._check_path(path)
        self.min_size = min_size
        self.ignore = ignore
        self._duplicates = self._remove_unique_files(self._files_hashing()) if self._remove_unique_files(self._files_hashing()) else "Dir doesn't contain duplicates"
        


    @staticmethod
    def _check_path(path):
        if not os.path.exists(path):
            raise FileNotFoundError("Dir doesn't exists")
        return path
        
    def _config_handler(self):
        return None
    
    def _get_files(self) -> set | str:
        files = set()
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
                        if item.is_file(follow_symlinks=False):
                            files.add(os.path.realpath(item))
                        elif item.is_dir(follow_symlinks=False):
                            stack.append(os.path.realpath(item))
        return files if files else "Dir is empty"

    def _files_hashing(self) -> dict | str:
        hash_files = {}
        if isinstance(files:=self._get_files(), set):
            for file in files:
                if os.path.exists(file):
                    with open(file, "rb") as data:
                        if os.stat(file).st_size:
                            solved_hash = hashlib.new("md5", data.read(), usedforsecurity=False).hexdigest()
                            hash_files.setdefault(solved_hash, set()).add(file)
        else:
            return files
        return hash_files
    
    @staticmethod
    def _remove_unique_files(hash_files: dict):
        if isinstance(hash_files, dict):
            duplicates = {}
            for hash in hash_files.keys():
                if len(hash_files[hash]) > 1:
                    duplicates[hash] = hash_files[hash]
        else:
            return hash_files
        return duplicates
    
    def get_duplicates(self) -> dict | str:
        return self._duplicates
    
    def print_duplicates(self, preview: bool = False):
        if isinstance(self._duplicates, dict):
            number = 1
            for hash, files in self._duplicates.items():
                subnumber = 1
                print(f"{number}. hash - ({hash})")
                for file in files:
                    print(f"\t{subnumber}. {file}")
                    subnumber += 1
                if preview:
                    with open(file, "rb") as summary_f:
                        try:
                            print(f"```preview(utf-8) of Group({number}) hash({hash})\n{summary_f.read(100).decode("utf-8")}\n```preview end\n")
                        except:
                            print(f"```preview(bytes) of Group({number}) hash({hash})\n{summary_f.read(100)}\n```preview end\n")
                number += 1
        else:
            print(self._duplicates)
    
    def remove_duplicates(self, group_index: int, keep_indexes: list[int] | None = None) -> None | str:
        if isinstance(self._duplicates, dict):
            try:
                duplicate_groups = list(self._duplicates.values())
                
                if keep_indexes:
                    for index, valid_index in enumerate(keep_indexes.copy()):
                        if valid_index < 0:
                            keep_indexes[index] = len(keep_indexes)+valid_index
                        else:
                            pass

                if 0 <= group_index < len(duplicate_groups):
                    group = list(duplicate_groups[group_index])
                    if keep_indexes:
                        files_to_keep = [file for i, file in enumerate(group) if i in keep_indexes]
                        files_to_remove = [file for file in group if file not in files_to_keep]
                    else:
                        files_to_remove = group

                    for file in files_to_remove:
                        if os.path.exists(file):
                            os.remove(file)
                    print(f"Removed {len(files_to_remove)} files.")
                else:
                    print("Invalid group index.")
            except PermissionError:
                print("You do not have enough permissions to delete some files.")
        else:
            return "Dir is empty, nothing to remove."
        


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

