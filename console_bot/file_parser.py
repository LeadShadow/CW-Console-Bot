from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from console_bot.command_parser import RainbowLexer

import shutil
from console_bot.parser import *
from console_bot.normalize import normalize
from console_bot.command_parser import command_parser


def help_me(*args):
    return """\nCommand format:
    help or ? - this help;
    parse folder_name- sorts files in the folder;
    good bye or close or exit or . - exit the program"""


def goodbye(*args):
    return 'You have finished working with file_parser'


def handle_media(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / (normalize(filename.name[:-len(filename.suffix)]) + filename.suffix))


def handle_other(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / (normalize(filename.name[:-len(filename.suffix)]) + filename.suffix))


def handle_archive(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(filename.name.replace(filename.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(filename.resolve()), str(folder_for_file.resolve()))
        #     normalize archive files
        for file in folder_for_file.iterdir():
            file.replace(folder_for_file / (normalize(file.name[:-len(file.suffix)]) + file.suffix))

    except shutil.ReadError:
        print(f'Not an archive {filename}!')
        folder_for_file.rmdir()
        return None
    filename.unlink()
    # .resolve gives absolute path


def handle_folder(folder: Path):
    try:
        folder.rmdir()
    except OSError:
        return f"Folder deletion failed {folder}"


def file_parser(*args):
    try:
        folder_for_scan = Path(args[0])
        scan(folder_for_scan.resolve())
    except FileNotFoundError:
        return f"Not able to find '{args[0]}' folder. Please enter a correct folder name."
    except IndexError:
        return "Please enter a folder name."
    for file in JPEG_IMAGES:
        handle_media(file, Path(args[0] + '/' + 'images' + '/' + 'JPEG'))
    for file in JPG_IMAGES:
        handle_media(file, Path(args[0] + '/' + 'images' + '/' + 'JPG'))
    for file in PNG_IMAGES:
        handle_media(file, Path(args[0] + '/' + 'images' + '/' + 'PNG'))
    for file in SVG_IMAGES:
        handle_media(file, Path(args[0] + '/' + 'images' + '/' + 'SVG'))
    for file in MP3_AUDIO:
        handle_media(file, Path(args[0] + '/' + 'audio' + '/' + 'MP3'))
    for file in OGG_AUDIO:
        handle_media(file, Path(args[0] + '/' + 'audio' + '/' + 'OGG'))
    for file in WAV_AUDIO:
        handle_media(file, Path(args[0] + '/' + 'audio' + '/' + 'WAV'))
    for file in AMR_AUDIO:
        handle_media(file, Path(args[0] + '/' + 'audio' + '/' + 'AMR'))
    for file in AVI_VIDEO:
        handle_media(file, Path(args[0] + '/' + 'video' + '/' + 'AVI'))
    for file in MP4_VIDEO:
        handle_media(file, Path(args[0] + '/' + 'video' + '/' + 'MP4'))
    for file in MOV_VIDEO:
        handle_media(file, Path(args[0] + '/' + 'video' + '/' + 'MOV'))
    for file in MKV_VIDEO:
        handle_media(file, Path(args[0] + '/' + 'video' + '/' + 'MKV'))
    for file in DOC_DOCUMENT:
        handle_media(file, Path(args[0] + '/' + 'document' + '/' + 'DOC'))
    for file in DOCX_DOCUMENT:
        handle_media(file, Path(args[0] + '/' + 'document' + '/' + 'DOCX'))
    for file in TXT_DOCUMENT:
        handle_media(file, Path(args[0] + '/' + 'document' + '/' + 'TXT'))
    for file in PDF_DOCUMENT:
        handle_media(file, Path(args[0] + '/' + 'document' + '/' + 'PDF'))
    for file in XLSX_DOCUMENT:
        handle_media(file, Path(args[0] + '/' + 'document' + '/' + 'XLSX'))
    for file in PPTX_DOCUMENT:
        handle_media(file, Path(args[0] + '/' + 'document' + '/' + 'PPTX'))
    for file in OTHER:
        handle_other(file, Path(args[0] + '/' + 'other'))

    for file in ARCHIVES:
        handle_archive(file, Path(args[0] + '/' + 'archives'))

    for folder in FOLDERS[::-1]:
        handle_folder(folder)

    return f"Files in {args[0]} sorted succesffully"


COMMANDS_F = {file_parser: ['parse '], help_me: ['?', 'help'], goodbye: ['good bye', 'close', 'exit', '.']}


def start_fp():
    print('\n\033[033mWelcome to file parser!\033[0m')
    print(f"\033[032mType command or '?' for help \033[0m\n")
    while True:
        with open("history.txt", "wb"):
            pass
        user_command = prompt('Enter command >>> ',
                              history=FileHistory('history.txt'),
                              auto_suggest=AutoSuggestFromHistory(),
                              completer=Completer,
                              lexer=RainbowLexer()
                              )
        command, data = command_parser(user_command, COMMANDS_F)
        print(command(*data), '\n')
        if command is goodbye:
            break


Completer = NestedCompleter.from_nested_dict({'help': None, '?': None, 'parse': None, 'good bye': None,
                                              'close': None, 'exit': None, '.': None})

