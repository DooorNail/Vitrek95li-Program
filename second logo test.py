from colorama import Fore, Style, init

init(autoreset=True)


SPLASH_SCREEN = [
    "   $██████@╗ $█████@╗ $██████@╗        $██@╗      $█████@╗ $██████@╗ ",
    "  $██@╔════╝$██@╔══$██@╗$██@╔══$██@╗       $██@║     $██@╔══$██@╗$██@╔══$██@╗",
    "  $██@║     $███████@║$██████@╔╝       $██@║     $███████@║$██████@╔╝",
    "  $██@║     $██@╔══$██@║$██@╔═══╝        $██@║     $██@╔══$██@║$██@╔══$██@╗",
    "@  ╚$██████@╗$██@║  $██@║$██@║            $███████@╗$██@║  $██@║$██████@╔╝",
    "@   ╚═════╝╚═╝  ╚═╝╚═╝            ╚══════╝╚═╝  ╚═╝╚═════╝  ~$MG"
]

# -----------------------------
# Display Splash Screen
# -----------------------------

def disp_splash_screen(foreground, background):
    print("\n"*2)
    for line in SPLASH_SCREEN:
        # print(" "*15+line.replace("@","\x1b[2m\x1b[36m").replace("$","\x1b[0m\x1b[1m\x1b[35m"))
        # print(" "*15+line.replace("@",Style.RESET_ALL+Fore.RED+Style.DIM).replace("$",Style.RESET_ALL+Fore.LIGHTRED_EX+Style.BRIGHT))
        # print(" "*15+line.replace("@",Style.RESET_ALL+Fore.YELLOW+Style.DIM).replace("$",Style.RESET_ALL+Fore.GREEN+Style.BRIGHT))
        print(" "*15+line.replace("@",background).replace("$",foreground))
        
    print(background + " "*18+"PEDOT Capacitor HV-Test Procedures\n")
    
    

colours = [
    [Style.RESET_ALL+Fore.GREEN+Style.BRIGHT, Style.RESET_ALL+Fore.YELLOW+Style.DIM],
    [Style.RESET_ALL+Fore.YELLOW+Style.DIM, Style.RESET_ALL+Fore.CYAN+Style.DIM],
    [Style.RESET_ALL+Fore.YELLOW, Style.RESET_ALL+Fore.LIGHTCYAN_EX+Style.DIM],
    [Style.RESET_ALL+Fore.BLUE+Style.BRIGHT, Style.RESET_ALL+Fore.LIGHTYELLOW_EX+Style.DIM],
    [Style.RESET_ALL+Fore.LIGHTCYAN_EX+Style.BRIGHT, Style.RESET_ALL+Fore.LIGHTWHITE_EX+Style.DIM],
    [Style.RESET_ALL+Fore.RED+Style.BRIGHT, Style.RESET_ALL+Fore.LIGHTBLACK_EX+Style.DIM]
    
    ]


for pair in colours:
    disp_splash_screen(pair[0], pair[1])
    print("\n"*2)
# disp_splash_screen(Style.RESET_ALL+Fore.GREEN+Style.BRIGHT, Style.RESET_ALL+Fore.YELLOW+Style.DIM)
input()


    
    