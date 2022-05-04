from termcolor import colored

def colored_if_true(val, bool_val, color):
    if bool_val:
        return colored(str(val), color)
    return str(val)