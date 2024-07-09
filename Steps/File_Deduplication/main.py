import argparse
from logic import *

parser = argparse.ArgumentParser(
    prog="Deduplicator",
    epilog='Программа для поиска дубликатов и выполнения дальнейши действий с ними.'
)


def main():
    parser.add_argument("-rp", "--root_path",
                        default=os.getcwd(), help="Путь к каталогу в котором нужно найти дубликаты.")
    parser.add_argument("-ms", "--min_size",
                        default=0, type=int, help="Минимальный размер файлов которые нужно искать. В байтах")
    parser.add_argument("-i", "--ignore",
                        default=None, nargs="+", help="Перечислите названия папок и/или файлов которые нужно игнорировать.")
    parser.add_argument("-p", "--preview",
                        action="store_true", help="Показывать первые 100 символов файла")
    
    
    p_args = parser.parse_args()
    deduplication = Deduplication(p_args.root_path, p_args.min_size, p_args.ignore)
    deduplication.print_duplicates(p_args.preview)
    if isinstance(duplications:=deduplication.get_duplicates(), dict):
        match input("Выбрать действие для дубликатов? (y/n) или (use default): ").lower():
            case "y" | "yes":
                actions = ("remove all", "save")
                for number in range(1, len(duplications)+1):
                    user_input = input(f"{number}. 'remove all', 'save <numbers separated by space>', ''<SKIP>: ").lower()
                    
                    if user_input.startswith(actions[0]):
                        deduplication.remove_duplicates(number-1)
                    elif user_input.startswith(actions[1]):
                        indexes = user_input.split()[1:]
                        ignored_indexes = [index-1 for index in list(map(int, indexes))]
                        deduplication.remove_duplicates(number-1, list(map(int, ignored_indexes)))
                    else:
                        continue
            case "use default":
                default_action = input("Действие по умолчанию (Remove all, Save fitst/last): ").lower()
                default_actions = (
                    default_action.startswith("remove all"),
                    default_action.startswith("save first"),
                    default_action.startswith("save last"),
                )
                
                while not any(default_actions):
                    default_action = input("Действие по умолчанию (Remove all, Save fitst/last): ").lower()
                    default_actions = (
                        default_action.startswith("remove all"),
                        default_action.startswith("save first"),
                        default_action.startswith("save last"),
                    )
                
                if default_action not in ("save first", "save last"):
                    [deduplication.remove_duplicates(number) for number in range(len(duplications))]
                else:
                    keep_index = [0] if default_action == "save first" else [-1]
                    [deduplication.remove_duplicates(number, keep_index) for number in range(len(duplications))]
            
            case _:
                pass


if __name__ == "__main__":
    main()
