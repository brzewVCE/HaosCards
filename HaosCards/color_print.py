# color_print.py

def print_info(message):
    print("\033[1;37;40m" + "[INFO] " + message + "\033[0m")

def print_error(message):
    print("\033[1;31;40m" + "[ERROR] " + message + "\033[0m")

def print_warning(message):
    print("\033[1;33;40m" + "[WARNING] " + message + "\033[0m")
