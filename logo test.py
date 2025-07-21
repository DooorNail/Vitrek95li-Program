from colorama import init, Fore, Style

init(autoreset=True)

logo_lines = [
    "   ██████╗ █████╗ ██████╗        ██╗      █████╗ ██████╗ ",
    "  ██╔════╝██╔══██╗██╔══██╗       ██║     ██╔══██╗██╔══██╗",
    "  ██║     ███████║██████╔╝       ██║     ███████║██████╔╝",
    "  ██║     ██╔══██║██╔═══╝        ██║     ██╔══██║██╔══██╗",
    "  ╚██████╗██║  ██║██║            ███████╗██║  ██║██████╔╝",
    "   ╚═════╝╚═╝  ╚═╝╚═╝            ╚══════╝╚═╝  ╚═╝╚═════╝  ~MG"
]


output = []
for index, line in enumerate(logo_lines):
    line_out = []
    for line_index, symb in enumerate(line):
        value = ord(symb) * 1 + ((index*5 + line_index*3)%7) + (7*line_index)%22
        if not value % 2:
            value*=2
            value-=10
        line_out.append(chr(value))
    output.append("".join(line_out))

for i in output:
    print(i)
    
# for index, line in enumerate(output):
#     for line_index, symb in enumerate(line):
#         if va

def print_ascii_colored(ascii_art):
    bright_magenta = Style.BRIGHT + Fore.MAGENTA
    dim_cyan = Style.DIM + Fore.CYAN
    reset = Style.RESET_ALL

    for line in ascii_art:
        if not line:
            print()
            continue
        
        output = []
        prev_was_block = None  # Track if previous char was █

        for char in line:
            if char == '█':
                if prev_was_block != True:
                    output.append(bright_magenta)
                    prev_was_block = True
                output.append(char)
            else:
                if prev_was_block != False:
                    output.append(dim_cyan)
                    prev_was_block = False
                output.append(char)
        
        output.append(reset)  # Reset at end of line
        print(''.join(output))
        
        
print_ascii_colored(logo_lines)

def colorize_ascii_art(ascii_art):
    bright_magenta = Style.BRIGHT + Fore.MAGENTA
    dim_cyan = Style.DIM + Fore.CYAN
    reset = Style.RESET_ALL

    colored_lines = []

    for line in ascii_art:
        if not line:
            colored_lines.append('')  # keep empty lines as is
            continue

        output = []
        prev_was_block = None

        for char in line:
            if char == '█':
                if prev_was_block != True:
                    output.append(bright_magenta)
                    prev_was_block = True
                output.append(char)
            else:
                if prev_was_block != False:
                    output.append(dim_cyan)
                    prev_was_block = False
                output.append(char)

        output.append(reset)
        colored_lines.append(''.join(output))

    return colored_lines

coloured_lines = colorize_ascii_art(logo_lines)

print(coloured_lines)

coloured_lines = ["\x1b[2m\x1b[36m   \x1b[1m\x1b[35m██████\x1b[2m\x1b[36m╗ \x1b[1m\x1b[35m█████\x1b[2m\x1b[36m╗ \x1b[1m\x1b[35m██████\x1b[2m\x1b[36m╗        \x1b[1m\x1b[35m██\x1b[2m\x1b[36m╗      \x1b[1m\x1b[35m█████\x1b[2m\x1b[36m╗ \x1b[1m\x1b[35m██████\x1b[2m\x1b[36m╗ \x1b[0m",
"\x1b[2m\x1b[36m  \x1b[1m\x1b[35m██\x1b[2m\x1b[36m╔════╝\x1b[1m\x1b[35m██\x1b[2m\x1b[36m╔══\x1b[1m\x1b[35m██\x1b[2m\x1b[36m╗\x1b[1m\x1b[35m██\x1b[2m\x1b[36m╔══\x1b[1m\x1b[35m██\x1b[2m\x1b[36m╗       \x1b[1m\x1b[35m██\x1b[2m\x1b[36m║     \x1b[1m\x1b[35m██\x1b[2m\x1b[36m╔══\x1b[1m\x1b[35m██\x1b[2m\x1b[36m╗\x1b[1m\x1b[35m██\x1b[2m\x1b[36m╔══\x1b[1m\x1b[35m██\x1b[2m\x1b[36m╗\x1b[0m",
"\x1b[2m\x1b[36m  \x1b[1m\x1b[35m██\x1b[2m\x1b[36m║     \x1b[1m\x1b[35m███████\x1b[2m\x1b[36m║\x1b[1m\x1b[35m██████\x1b[2m\x1b[36m╔╝       \x1b[1m\x1b[35m██\x1b[2m\x1b[36m║     \x1b[1m\x1b[35m███████\x1b[2m\x1b[36m║\x1b[1m\x1b[35m██████\x1b[2m\x1b[36m╔╝\x1b[0m",
"\x1b[2m\x1b[36m  \x1b[1m\x1b[35m██\x1b[2m\x1b[36m║     \x1b[1m\x1b[35m██\x1b[2m\x1b[36m╔══\x1b[1m\x1b[35m██\x1b[2m\x1b[36m║\x1b[1m\x1b[35m██\x1b[2m\x1b[36m╔═══╝        \x1b[1m\x1b[35m██\x1b[2m\x1b[36m║     \x1b[1m\x1b[35m██\x1b[2m\x1b[36m╔══\x1b[1m\x1b[35m██\x1b[2m\x1b[36m║\x1b[1m\x1b[35m██\x1b[2m\x1b[36m╔══\x1b[1m\x1b[35m██\x1b[2m\x1b[36m╗\x1b[0m",
"\x1b[2m\x1b[36m  ╚\x1b[1m\x1b[35m██████\x1b[2m\x1b[36m╗\x1b[1m\x1b[35m██\x1b[2m\x1b[36m║  \x1b[1m\x1b[35m██\x1b[2m\x1b[36m║\x1b[1m\x1b[35m██\x1b[2m\x1b[36m║            \x1b[1m\x1b[35m███████\x1b[2m\x1b[36m╗\x1b[1m\x1b[35m██\x1b[2m\x1b[36m║  \x1b[1m\x1b[35m██\x1b[2m\x1b[36m║\x1b[1m\x1b[35m██████\x1b[2m\x1b[36m╔╝\x1b[0m",
"\x1b[2m\x1b[36m   ╚═════╝╚═╝  ╚═╝╚═╝            ╚══════╝╚═╝  ╚═╝╚═════╝  ~\x1b[34mMG\x1b[0m"]

for line in coloured_lines:
    print(line)