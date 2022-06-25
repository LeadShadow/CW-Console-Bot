"""Модуль для роботи з нотатками"""
import datetime
import pickle
import re
from collections import UserDict
from datetime import date
from pathlib import Path

N = 3  # Кількість нотаток на сторінці


class DateIsNotValid(Exception):
    """You cannot add an invalid date"""


class InputError:
    """Клас для виклику помилки при введенні невірного даних"""
    def __init__(self, func) -> None:
        self.func = func

    def __call__(self, contacts, *args):
        try:
            return self.func(contacts, *args)
        # except IndexError:
        #     return 'Error! Give me name and phone or birthday please!'
        except KeyError:
            return 'Error! Note not found!'
        except ValueError:
            return 'Error! Number of days is incorrect!'
        except DateIsNotValid:
            return 'Error! Date is not valid'


class Field:
    def __init__(self, value: str) -> None:
        self.__value = None
        self.value = value

    def __str__(self) -> str:
        return f'{self.value}'

    def __eq__(self, other) -> bool:
        return self.value == other.value

    def __lt__(self, other) -> bool:
        return self.value < other.value

    def __gt__(self, other) -> bool:
        return self.value > other.value

    def __le__(self, other) -> bool:
        return self.value <= other.value

    def __ge__(self, other) -> bool:
        return self.value >= other.value


class ExecDate(Field):
    def __str__(self) -> str:
        if self.value is None:
            return ' - '
        else:
            return f'{self.value:%d %b %Y}'

    @property
    def value(self) -> datetime.date:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        if value is None:
            self.__value = None
        else:
            try:
                self.__value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                try:
                    self.__value = datetime.datetime.strptime(value, '%d.%m.%Y').date()
                except ValueError:
                    raise DateIsNotValid


class Tag(Field):
    def __str__(self) -> str:
        return f'{self.value}'

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        self.__value = value


class Text(Field):
    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        if value:
            self.__value = value
        else:
            self.__value = 'No text'
        print(self.__value)

    def __str__(self) -> str:
        return f'{self.value}'


class Note:
    """Клас для нотаток"""
    def __init__(self, text: str) -> None:
        NoteBook.id_counter += 1
        self.id = NoteBook.id_counter
        self.is_done = False
        self.exec_date = None
        self.tags = []
        self.text = text

    # def hyphenation_string(self):
    #     self.result_list = re.findall(r'.{49}', self.text)
    #     if self.result_list:
    #         self.result = ''
    #         for i in self.result_list:
    #             self.result += i + "-" + '\n'
    #         self.result = self.result + self.text[len(self.result)-2:]
    #         return self.result
    #     else:
    #         self.result = self.text
    #         return self.result

    def __str__(self):
        def hyphenation_string(text) -> str:
            result_list = re.findall(r'.{50}', text)
            if result_list:
                result = ''
                for i in result_list:
                    if i[49] == " ":
                        result += i + '\n'
                    else:
                        result += i + "-" + '\n'
                result = result + text[len(result) - 2:]
                return result
            else:
                return text

        return f"ID: {self.id:^10} {' ' * 17} Date: {self.exec_date}\n" \
               f"Tags: {', '.join(self.tags)}\n" \
               f"{hyphenation_string(self.text)}"


class NoteBook(UserDict):
    """Клас для роботи з нотатками"""
    id_counter = 0

    def __init__(self, filename: str) -> None:
        super().__init__()  # Викликаємо конструктор базового класу
        self.filename = Path(filename)
        if self.filename.exists():
            with open(self.filename, 'rb') as db:
                self.data = pickle.load(db)
        if len(self.data) > 0:
            NoteBook.id_counter = max(self.data.keys())

    def save(self):
        with open(self.filename, 'wb') as db:
            pickle.dump(self.data, db)

    def iterator(self, func=None):
        index, print_block = 1, '=' * 50 + '\n'
        for note in self.data.values():
            if func is None or func(note):
                print_block += str(note) + '\n' + '-' * 50 + '\n'
                if index < N:
                    index += 1
                else:
                    yield print_block
                    index, print_block = 1, '=' * 50 + '\n'
        yield print_block


@InputError
def add_note(notebook, *args):
    """Додає нотатку"""
    note_text = ' '.join(args)
    note = Note(note_text)
    notebook[note.id] = note
    return f'Note ID:{note.id} added'


@InputError
def change_note(notebook, *args):
    id_note, new_text = int(args[0]), ' '.join(args[1:])
    notebook[id_note].text = new_text
    return f'Note ID:{id_note} changed'


@InputError
def del_note(notebook, *args):
    id_note = int(args[0])
    yes_no = input(f'Are you sure you want to delete the note ID:{id_note}? (Y/n) ')
    if yes_no == 'Y':
        del notebook[id_note]
        return f'Note ID:{id_note} deleted'
    else:
        return 'Note not deleted'


@InputError
def add_date(notebook, *args):
    """Додає дату нотатки"""
    id_note, exec_date = int(args[0]), args[1]
    notebook[id_note].exec_date = ExecDate(exec_date)
    return f'Date {notebook[id_note].exec_date} added to note ID:{id_note}'


def show_all(notebook, *args):
    """Повертає всі нотатки"""
    def filter_func(note):
        return not note.is_done

    result = 'List of all notes:\n'
    print_list = notebook.iterator(filter_func)
    if not print_list:
        return 'Notebook is empty'
    for item in print_list:
        result += f'{item}'
    return result


def show_archiv(notebook, *args):
    """Повертає нотатки з архіву"""
    def filter_func(note):
        return note.is_done

    result = 'List of archived notes:\n'
    print_list = notebook.iterator(filter_func)
    if not print_list:
        return 'Archive is empty'
    for item in print_list:
        result += f'{item}'
    return result


def find_note(notebook, *args):
    """Повертає нотатки за входженням в текст"""
    def filter_func(note):
        return subtext in note.text

    subtext = args[0]
    result = f'List of notes with text "{subtext}":\n'
    print_list = notebook.iterator(filter_func)
    if not print_list:
        return 'List is empty'
    for item in print_list:
        result += f'{item}'
    return result


@InputError
def show_date(notebook, *args):
    """Повертає нотатки з вказаною датою виконання"""
    def filter_func(note):
        if note.exec_date is None:
            return False
        date1 = (date_find.value - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        date2 = (date_find.value + datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        return ExecDate(date1) <= note.exec_date <= ExecDate(date2)

    date_find = ExecDate(args[0])
    if len(args) > 1:
        days = int(args[1])
    else:
        days = 0
    result = 'List of notes with date:\n'
    print_list = notebook.iterator(filter_func)
    if not print_list:
        return 'Notebook is empty'
    for item in print_list:
        result += f'{item}'
    return result


@InputError
def done_note(notebook, *args):
    """Помічає нотатку як виконану"""
    id_note = int(args[0])
    if not notebook[id_note].is_done:
        notebook[id_note].is_done = True
        return f'Note ID:{id_note} marked as done'
    else:
        return f'Note ID:{id_note} is already done'


@InputError
def return_note(notebook, *args):
    """Помічає нотатку як виконану"""
    id_note = int(args[0])
    if notebook[id_note].is_done:
        notebook[id_note].is_done = False
        return f'Note ID:{id_note} marked as not done'
    else:
        return f'Note ID:{id_note} is not done'


@InputError
def add_tag(notebook, *args):
    id_note = int(args[0])
    note_text = ' '.join(args[1:])
    if not notebook[id_note].tags:
        notebook[id_note].tags.append(note_text)
    else:
        notebook[id_note].tags.append(note_text)
        notebook[id_note].tags.sort()
        # notebook[id_note].tags.sort(key=lambda x: x[0])
    return f'Tag {note_text} added to note ID:{id_note}'


def goodbye(notebook, *args):
    notebook.save()
    return 'Good bye!'


def unknown_command(*args):
    return 'Unknown command! Enter again!'


def help_me(*args):
    """Повертає допомогу по списку команд"""
    return """Command format:
    help or ? - this help;
    add note <text> - add note;
    change note <id> <text> - change note;
    delete note <id> - delete note;
    add date id <date> - add/change date;
    add tag id <tag> - add tag;
    done id - mark note as done;
    return id - mark note as not done;
    show all - show all notes;
    show archived - show archived notes;
    show date <date> [<days>] - show notes by date +- days;
    find note <text> - find note by text;
    good bye or close or exit or . - exit the program"""


COMMANDS = {help_me: ['?', 'help'], goodbye: ['good bye', 'close', 'exit', '.'], add_note: ['add note '],
            add_date: ['add date '], show_all: ['show all'], show_archiv: ['show archived'],
            change_note: ['change note '], del_note: ['delete note '], find_note: ['find note '],
            show_date: ['show date '], done_note: ['done '], return_note: ['return '], add_tag: ["add tag"]}


def command_parser(user_command: str) -> (str, list):
    for key, list_value in COMMANDS.items():
        for value in list_value:
            if user_command.lower().startswith(value):
                args = user_command[len(value):].split()
                return key, args
    else:
        return unknown_command, []


def start_nb():
    notebook = NoteBook(filename='notes.dat')
    print(help_me())
    while True:
        user_command = input('Enter command >>> ')
        command, data = command_parser(user_command)
        print(command(notebook, *data), '\n')
        if command is goodbye:
            break


if __name__ == '__main__':
    start_nb()
