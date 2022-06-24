def unknown_command(*args):
    return 'Unknown command! Enter again!'


def command_parser(user_command: str, COMMANDS: dict) -> (str, list):
    for key, list_value in COMMANDS.items():
        for value in list_value:
            if user_command.lower().startswith(value):
                args = user_command[len(value):].split()
                return key, args
    else:
        return unknown_command, []


