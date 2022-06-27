from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from command_parser import RainbowLexer
import datetime
import pickle
from pathlib import Path
from collections import UserDict
from datetime import date
import colorama
import re

from pygments.lexers import SqlLexer

from command_parser import command_parser

N = 3  # кількість записів для представлення телефонної книги


class Field:
    def __init__(self, value: str) -> None:
        self.__value = None
        self.value = value

    def __str__(self) -> str:
        return f'{self.value}'

    def __eq__(self, other) -> bool:
        return self.value == other.value


class Name(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        self.__value = value


class Phone(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        def is_code_valid(phone_code: str) -> bool:
            if phone_code[:2] in ('03', '04', '05', '06', '09') and phone_code[2] != '0' and phone_code != '039':
                return True
            return False

        result = None
        phone = value.removeprefix('+').replace('(', '').replace(')', '').replace('-', '')
        if phone.isdigit():
            if phone.startswith('0') and len(phone) == 10 and is_code_valid(phone[:3]):
                result = '+38' + phone
            if phone.startswith('380') and len(phone) == 12 and is_code_valid(phone[2:5]):
                result = '+' + phone
            if 10 <= len(phone) <= 14 and not phone.startswith('0') and not phone.startswith('380'):
                result = '+' + phone
        if result is None:
            raise ValueError(f'Неправильний тип значення {value}')
        self.__value = result


class Birthday(Field):
    def __str__(self):
        if self.value is None:
            return 'Unknown'
        else:
            return f'{self.value:%d %b %Y}'

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
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


class Address(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        self.__value = value


class Email(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if value is None:
            self.__value = None
        else:
            result = None
            get_emails = re.findall(r'\b[a-zA-Z][\w\.]+@[a-zA-Z]+\.[a-zA-Z]{2,}', value)
            if get_emails:
                for i in get_emails:
                    result = i
            if result is None:
                raise AttributeError(f"Неправильний тип значення {value}")
            self.__value = result


class Record:
    def __init__(self, name: Name, phones=[], birthday=None, email=None, address=None) -> None:
        self.name = name
        self.phone_list = phones
        self.birthday = birthday
        self.address = address
        self.email = email

    def __str__(self) -> str:
        return f' User \033[35m{self.name.value:20}\033[0m - Birthday {self.birthday}\n' \
               f'     Phones: {", ".join([phone.value for phone in self.phone_list])}\n' \
               f' Email: {self.email}\n' \
               f' Address: {self.address}'

    def add_phone(self, phone: Phone) -> None:
        self.phone_list.append(phone)

    def del_phone(self, phone: Phone) -> None:
        self.phone_list.remove(phone)

    def edit_phone(self, phone: Phone, new_phone: Phone) -> None:
        self.phone_list.remove(phone)
        self.phone_list.append(new_phone)

    def days_to_birthday(self, birthday: Birthday):
        if birthday.value is None:
            return None
        this_day = date.today()
        birthday_day = date(this_day.year, birthday.value.month, birthday.value.day)
        if birthday_day < this_day:
            birthday_day = date(this_day.year + 1, birthday.value.month, birthday.value.day)
        return (birthday_day - this_day).days


class AddressBook(UserDict):
    def __init__(self, filename: str) -> None:
        super().__init__()  # виклик базового конструктора
        self.filename = Path(filename)
        if self.filename.exists():
            with open(self.filename, 'rb') as db:
                self.data = pickle.load(db)

    def save(self):
        with open(self.filename, 'wb') as db:
            pickle.dump(self.data, db)

    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def iterator(self, func=None, days=0):
        index, print_block = 1, '-' * 50 + '\n'
        for record in self.data.values():
            if func is None or func(record):
                print_block += str(record) + '\n'
                if index < N:
                    index += 1
                else:
                    yield print_block
                    index, print_block = 1, '-' * 50 + '\n'
        yield print_block


class PhoneUserAlreadyExists(Exception):
    """You cannot add an existing phone number to a user"""


class DateIsNotValid(Exception):
    """You cannot add an invalid date"""


class EmailIsNotValid(Exception):
    """Email is not valid, try again"""


class InputError:
    def __init__(self, func) -> None:
        self.func = func

    def __call__(self, contacts, *args):
        try:
            return self.func(contacts, *args)
        except IndexError:
            return 'Error! Give me name and phone or birthday please!'
        except KeyError:
            return 'Error! User not found!'
        except ValueError:
            return 'Error! Phone number is incorrect!'
        except PhoneUserAlreadyExists:
            return 'Error! You cannot add an existing phone number to a user'
        except DateIsNotValid:
            return 'Error! Date is not valid'
        except AttributeError:
            return 'Error! Email is not valid'


def salute(*args):
    return 'Hello! How can I help you?'


@InputError
def add_contact(contacts, *args):
    name = Name(args[0])
    phone = Phone(args[1])
    birthday = None
    email = None
    address = None
    if name.value in contacts:
        if phone in contacts[name.value].phone_list:
            raise PhoneUserAlreadyExists
        else:
            contacts[name.value].add_phone(phone)
            return f'Add phone {phone} to user {name}'

    else:
        if len(args) > 2:
            birthday = Birthday(args[2])
        if len(args) > 3:
            email = Email(args[3])
        if len(args) > 4:
            address = Address(args[4])
        if len(args) <= 2:
            birthday = Birthday(None)
        if len(args) <= 3:
            email = Email(None)
        if len(args) <= 4:
            address = Address(None)
        contacts[name.value] = Record(name, [phone], birthday, email, address)
        return f'Add user {name} with phone number {phone}'


@InputError
def change_contact(contacts, *args):
    name, old_phone, new_phone = args[0], args[1], args[2]
    contacts[name].edit_phone(Phone(old_phone), Phone(new_phone))
    return f'Change to user {name} phone number from {old_phone} to {new_phone}'


@InputError
def show_phone(contacts, *args):
    name = args[0]
    phone = contacts[name]
    return f'{phone}'


@InputError
def del_phone(contacts, *args):
    name, phone = args[0], args[1]
    contacts[name].del_phone(Phone(phone))
    return f'Delete phone {phone} from user {name}'


def show_all(contacts, *args):
    if not contacts:
        return 'Address book is empty'
    result = 'List of all users:\n'
    print_list = contacts.iterator()
    for item in print_list:
        result += f'{item}'
    return result


@InputError
def add_birthday(contacts, *args):
    name, birthday = args[0], args[1]
    contacts[name].birthday = Birthday(birthday)
    return f'Add/modify birthday {contacts[name].birthday} to user {name}'


@InputError
def days_to_user_birthday(contacts, *args):
    name = args[0]
    if contacts[name].birthday.value is None:
        return 'User has no birthday'
    return f'{contacts[name].days_to_birthday(contacts[name].birthday)} days to user {name} birthday'


@InputError
def show_birthday(contacts, *args):
    def func_days(record):
        return record.birthday.value is not None and record.days_to_birthday(record.birthday) <= days

    days = int(args[0])
    result = f'List of users with birthday in {days} days:\n'
    print_list = contacts.iterator(func_days)
    for item in print_list:
        result += f'{item}'
    return result


def goodbye(contacts, *args):
    contacts.save()
    return 'Good bye!'


def search(contacts, *args):
    def func_sub(record):
        return substring.lower() in record.name.value.lower() or \
               any(substring in phone.value for phone in record.phone_list) or \
               (record.birthday.value is not None and substring in record.birthday.value.strftime('%d.%m.%Y'))

    substring = args[0]
    result = f'List of users with \'{substring.lower()}\' in data:\n'
    print_list = contacts.iterator(func_sub)
    for item in print_list:
        result += f'{item}'
    return result


@InputError
def del_user(contacts, *args):
    name = args[0]
    yes_no = input(f'Are you sure you want to delete the user {name}? (Y/n) ')
    if yes_no == 'Y':
        del contacts[name]
        return f'Delete user {name}'
    else:
        return 'User not deleted'


def clear_all(contacts, *args):
    yes_no = input('Are you sure you want to delete all users? (Y/n) ')
    if yes_no == 'Y':
        contacts.clear()
        return 'Address book is empty'
    else:
        return 'Removal canceled'


@InputError
def add_email(contacts, *args):
    name, email = args[0], args[1]
    contacts[name].email = Email(email)
    return f'Add/modify email {contacts[name].email} to user {name}'


@InputError
def add_address(contacts, *args):
    name, address = args[0], " ".join(args[1:])
    contacts[name].address = Address(address)
    return f'Add/modify address {contacts[name].address} to user {name}'


def help_me(*args):
    return """Command format:
    help or ? - this help;
    hello - greeting;
    add name phone [birthday] - add user to directory;
    change name old_phone new_phone - change the user's phone number;
    del name phone - delete the user's phone number;
    delete name - delete the user;
    clear - delete all users;
    birthday name birthday - add/modify the user's birthday;
    email name email - add/modify the user's email;
    address name address - add/modify the user's address;
    show name - show the user's data;
    show all - show data of all users;
    find or search sub - show data of all users with sub in name, phones or birthday;
    days to birthday name - show how many days to the user's birthday;
    show birthday days N - show the user's birthday in the next N days;
    good bye or close or exit or . - exit the program"""


COMMANDS_A = {salute: ['hello'], add_contact: ['add '], change_contact: ['change '], help_me: ['?', 'help'],
              show_all: {'show all'}, goodbye: ['good bye', 'close', 'exit', '.'], del_phone: ['del '],
              add_birthday: ['birthday'], days_to_user_birthday: ['days to birthday '],
              show_birthday: ['show birthday days '], show_phone: ['show '], search: ['find ', 'search '],
              del_user: ['delete '], clear_all: ['clear'], add_email: ['email '], add_address: ['address']}


def start_ab():
    contacts = AddressBook(filename='contacts.dat')
    print(f"\033[031m {help_me()} \033[0m\n")
    while True:
        with open("history.txt", "wb"):
            pass
        # user_command = input('Enter command >>> ')
        user_command = prompt('Enter command >>> ',
                              history=FileHistory('history.txt'),
                              auto_suggest=AutoSuggestFromHistory(),
                              completer=Completer,
                              lexer=RainbowLexer()
                              )
        command, data = command_parser(user_command, COMMANDS_A)
        print(command(contacts, *data), '\n')
        if command is goodbye:
            break


Completer = NestedCompleter.from_nested_dict({'help': None, 'hello': None, 'good bye': None, 'exit': None,
                                              'close': None, '?': None, '.': None, 'birthday': None,
                                              'days to birthday': None, 'add': None,
                                              'show': {'all': None, 'birthday days': None},
                                              'change note': None, 'del': None, 'delete': None,
                                              'clear': None, 'email': None, 'find': None, 'search': None,
                                              'address': None})

if __name__ == "__main__":
    start_ab()
