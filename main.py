from adressbook import *


COMMANDS = {salute: ['hello'], add_contact: ['add '], change_contact: ['change '], help_me: ['?', 'help'],
            show_all: ['show all'], goodbye: ['good bye', 'close', 'exit', '.'], del_phone: ['del '],
            add_birthday: ['birthday'], days_to_user_birthday: ['days to birthday '],
            show_birthday: ['show birthday days '], show_phone: ['show '], search: ['find ', 'search '],
            del_user: ['delete '], clear_all: ['clear'], add_email: ['email '], add_address: ['address']}


def command_parser(user_command: str) -> (str, list):
    for key, list_value in COMMANDS.items():
        for value in list_value:
            if user_command.lower().startswith(value):
                args = user_command[len(value):].split()
                return key, args
    else:
        return unknown_command, []


def main():
    contacts = AddressBook(filename='contacts.dat')
    while True:
        user_command = input('Enter command >>> ')
        command, data = command_parser(user_command)
        print(command(contacts, *data), '\n')
        if command is goodbye:
            break


if __name__ == '__main__':
    main()
