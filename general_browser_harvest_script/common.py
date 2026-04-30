from datetime import datetime
from time import sleep

RESET = "\033[0m"

BLACK = "\033[30m"
RED = RESET + "\033[31m"
GREEN = RESET + "\033[32m"
YELLOW = RESET + "\033[33m"
BLUE = RESET + "\033[34m"
MAGENTA = "\033[35m"
CYAN = RESET + "\033[36m"
WHITE = "\033[37m"

BRIGHT_BLACK = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
REVERSE = "\033[7m"
HIDDEN = "\033[8m"

BG_BLACK = "\033[40m"
BG_RED = RESET + "\033[41m" + BRIGHT_RED
BG_GREEN = RESET + "\033[42m" + BRIGHT_WHITE
BG_YELLOW = RESET + "\033[43m" + BRIGHT_YELLOW
BG_BLUE = RESET + "\033[44m" + BRIGHT_CYAN
BG_MAGENTA = "\033[45m"
BG_CYAN = RESET + "\033[46m" + BRIGHT_BLUE
BG_WHITE = "\033[47m"

# success output print
def success(text):
	now = datetime.now()
	time = now.strftime("%H:%S")
	sleep(0.08)
	message = f"{BG_GREEN}[+]{RESET}{BRIGHT_GREEN}—{GREEN}[{GREEN}—{BRIGHT_GREEN}Success{GREEN}—]{BRIGHT_GREEN}—{GREEN}[{BG_GREEN}{time}{GREEN}]:{RESET} {text}"

	print(message)

# failed output print
def failed(text):
	now = datetime.now()
	time = now.strftime("%H:%S")
	sleep(0.08)
	message = f"{BG_RED}[!]{RESET}{BRIGHT_RED}—{RED}[{RED}—{BRIGHT_RED}Failed{RED}——]{BRIGHT_RED}—{RED}[{BG_RED}{time}{RED}]:{RESET} {text}"

	print(message)

# information print
def info(text):
	now = datetime.now()
	time = now.strftime("%H:%S")
	sleep(0.08)
	message = f"{BG_BLUE}[i]{RESET}{BRIGHT_BLUE}—{BLUE}[{BLUE}——{BRIGHT_BLUE}Info{BLUE}———]{BRIGHT_BLUE}—{BLUE}[{BG_BLUE}{time}{BLUE}]:{RESET} {text}"

	print(message)

# debug print
def debug(text):
	now = datetime.now()
	time = now.strftime("%H:%S")
	sleep(0.08)
	message = f"{BG_YELLOW}[i]{RESET}{BRIGHT_YELLOW}—{YELLOW}[{YELLOW}——{BRIGHT_YELLOW}Debug{YELLOW}——]{BRIGHT_YELLOW}—{YELLOW}[{BG_YELLOW}{time}{YELLOW}]:{RESET} {text}"

	print(message)

def prompt(text):
	now = datetime.now()
	time = now.strftime("%H:%S")
	sleep(0.08)
	message = f"{BG_CYAN}[p]{RESET}{BRIGHT_CYAN}—{CYAN}[{CYAN}—{BRIGHT_CYAN}Prompt{CYAN}——]{BRIGHT_CYAN}—{CYAN}[{BG_CYAN}{time}{CYAN}]:{RESET} {text}"

	response = input(message)
	return response

if __name__ == '__main__':
	success("test123")
	failed("test123")
	info("test123")
	debug("test123")
	prompt("are you good? [y/n]")
