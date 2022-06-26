from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory

from adressbook import start_ab
from notebook import start_nb
from file_parser import start_fp

if __name__ == '__main__':
    while True:
        with open("history.txt", "wb"):
            pass
        print("What would you like to start with?\n"
              "{:^10} {:^10} {:^10} {:^10}".format("addressbook", "notebook", "file parser", "quit"))
        user_input = prompt('Enter command >>> ',
                            history=FileHistory('history.txt'),
                            auto_suggest=AutoSuggestFromHistory(),
                            completer=NestedCompleter.from_nested_dict({'addressbook': None, 'notebook': None,
                                                                        'file parser': None, 'quit': None}),
                            )
        if user_input == "addressbook":
            start_ab()
        if user_input == "notebook":
            start_nb()
        if user_input == "file parser":
            start_fp()
        if user_input == "quit":
            print('Good bye!')
            break
