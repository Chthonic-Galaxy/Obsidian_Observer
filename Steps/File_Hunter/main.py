import os
import argparse

from logic import FileHunter

parser = argparse.ArgumentParser(
    prog="File Hunter",
    epilog='Программа для поиска файлов по критериям.'
)


def main():
    parser.add_argument("-p", "--path",
                        default=os.getcwd(), help="Путь к каталогу в котором нужно найти дубликаты.")
    parser.add_argument("-pat", "--pattern",
                        default=["*"], nargs="+", help="Паттерн(ы) соответственно которму(ым) нужно найти файлы.")
    parser.add_argument("-ms", "--min_size",
                        default=0, type=int, help="Минимальный размер файлов которые нужно искать. В байтах")
    parser.add_argument("-i", "--ignore",
                        default=None, nargs="+", help="Перечислите названия папок и/или файлов которые нужно игнорировать.")
    parser.add_argument("-d", "--date",
                        default=None, help="Дата для поска файлов.")
    parser.add_argument("-ai", "--addition_info",
                        action="store_true")
    
    
    p_args = parser.parse_args()
    file_hunter = FileHunter(p_args.path, p_args.pattern, p_args.ignore, p_args.min_size, p_args.date)
    matched_files = file_hunter.file_search(p_args.addition_info)
    for matched_file in sorted(matched_files):
        print(matched_file)
    if isinstance(matched_files, set):
        print(f"\n\nFiles was founded: {len(matched_files)}")


if __name__ == "__main__":
    main()
