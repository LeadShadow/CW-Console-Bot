from adressbook import *
from notebook import *
from file_parser import start_fp

if __name__ == '__main__':
    while True:
        print("What would you like to start with?\n"
          "{:^10} {:^10} {:^10} {:^10}".format("addressbook", "notebook", "file parser", "quit"))
        user_input = input('Enter command >>> ')
        if user_input == "addressbook":
            with open("history.txt", "wb"):
                pass
            start_ab()
        if user_input == "notebook":
            with open("history.txt", "wb"):
                pass
            start_nb()
        if user_input == "file parser":
            with open("history.txt", "wb"):
                pass
            start_fp()
        if user_input == "quit":
            print('Good bye!')
            break
