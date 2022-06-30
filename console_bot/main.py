from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
import colorama
from console_bot.adressbook import start_ab
from console_bot.notebook import start_nb
from console_bot.file_parser import start_fp
from console_bot.command_parser import RainbowLexer

# if __name__ == '__main__':


def start():
    while True:
        with open("history.txt", "wb"):
            pass
        print("")
        print("{:^70}".format("\033[34m What would you like to start with?\033[0m \n"))
        print("{:<25} {:<25} {:<25} {:<25}".format("\033[32m addressbook \033[0m", "\033[32m notebook \033[0m",
                                                   "\033[32m file parser \033[0m", "\033[32m quit \033[0m \n"))
        user_input = prompt("Enter command >>> ",
                            history=FileHistory('history.txt'),
                            auto_suggest=AutoSuggestFromHistory(),
                            completer=NestedCompleter.from_nested_dict({'addressbook': None, 'notebook': None,
                                                                        'file parser': None, 'quit': None}),
                            lexer=RainbowLexer()
                            )
        if user_input == "addressbook":
            start_ab()
        if user_input == "notebook":
            start_nb()
        if user_input == "file parser":
            start_fp()
        if user_input == "quit":
            print('Good luck, it was nice to meet you!')
            break

