import os
import hashlib

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