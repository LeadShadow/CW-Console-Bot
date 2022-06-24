from adressbook import *
from notebook import *
from file_parser import *


def command_parser(user_command: str, COMMANDS: dict) -> (str, list):
    for key, list_value in COMMANDS.items():
        for value in list_value:
            if user_command.lower().startswith(value):
                args = user_command[len(value):].split()
                return key, args
    else:
        return unknown_command, []


if __name__ == '__main__':
    while True:
        print("What would you like to start with?\n"
          "{:^10} {:^10} {:^10} {:^10}".format("addressbook", "notebook", "file parser", "quit"))
        user_input = input('Enter command >>> ')
        if user_input == "addressbook":
            start_ab()
        if user_input == "notebook":
            start_nb()
        if user_input == "file parser":
            start_fp()
        if user_input == "quit":
            print('Good bye!')
            break
