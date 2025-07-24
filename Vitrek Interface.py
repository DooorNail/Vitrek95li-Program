import socket
import threading
import time
import csv
import os
import glob
import configparser
from dataclasses import dataclass
from datetime import datetime, date
from colorama import init, Fore, Style
import signal
import sys

init(autoreset=True)

CONFIG_DIR = "Test Configs"
RAW_DATA_DIR = "Data/Raw"
SUMMARY_DIR = "Data/Summaries"
SETUP_CONFIG_PATH = "setup_config.ini" # Define path for setup config

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)

MAX_RETRIES = 3


SPLASH_SCREEN = [
    "@   $██████@╗ $█████@╗ $██████@╗        $██@╗      $█████@╗ $██████@╗ ",
    "@  $██@╔════╝$██@╔══$██@╗$██@╔══$██@╗       $██@║     $██@╔══$██@╗$██@╔══$██@╗",
    "@  $██@║     $███████@║$██████@╔╝       $██@║     $███████@║$██████@╔╝",
    "@  $██@║     $██@╔══$██@║$██@╔═══╝        $██@║     $██@╔══$██@║$██@╔══$██@╗",
    "@  ╚$██████@╗$██@║  $██@║$██@║            $███████@╗$██@║  $██@║$██████@╔╝",
    "@   ╚═════╝╚═╝  ╚═╝╚═╝            ╚══════╝╚═╝  ╚═╝╚═════╝  ~$MG"
]

# -----------------------------
# Display Splash Screen
# -----------------------------

def disp_splash_screen():
    print("\n"*2)
    for line in SPLASH_SCREEN:
        print(" "*15+line.replace("@","\x1b[2m\x1b[36m").replace("$","\x1b[0m\x1b[1m\x1b[35m"))
        
    print(Fore.MAGENTA + " "*18+"Vitrek 95LI DCW Program Interface\n")

# -----------------------------
# Graceful Shutdown Handling
# -----------------------------
running_test_thread = None

def signal_handler(signum, frame):
    global running_test_thread
    print(Fore.MAGENTA + "\n[INFO] Ctrl+C detected.")
    if running_test_thread and running_test_thread.is_alive():
        print(Fore.MAGENTA + "[INFO] Aborting running test...")
        running_test_thread.abort()
        running_test_thread.join()
        print(Fore.MAGENTA + "[INFO] Test aborted cleanly.")
    print(Fore.MAGENTA + "[INFO] Exiting program.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# -----------------------------
# Test Configuration Dataclass
# -----------------------------
@dataclass
class DCWTestConfig:
    name: str
    voltage: int
    current_limit: float
    ramp_time: int
    dwell_time: int
    discharge: str
    on_fail: str

def format_dcw_command(cfg: DCWTestConfig) -> str:
    fields = [""] * 16
    fields[0] = "ADD"
    fields[1] = "DCW"
    fields[2] = str(cfg.voltage)
    fields[3] = str(cfg.current_limit)
    fields[4] = str(cfg.ramp_time)
    fields[5] = str(cfg.dwell_time)
    fields[6] = "0"
    fields[7] = "AMPS"
    fields[8] = "0"
    fields[9] = str(cfg.current_limit)

    fields[12] = cfg.discharge
    fields[13] = cfg.on_fail
    return ",".join(fields)

# -----------------------------
# Config Loader
# -----------------------------
def load_configs(config_folder=CONFIG_DIR):
    patterns = glob.glob(os.path.join(config_folder, "*.ini"))
    if not patterns:
        default_path = os.path.join(config_folder, "default.ini")
        with open(default_path, 'w') as f:
            f.write("""[DCW]
voltage = 1000
current_limit = 0.01
ramp_time = 500
dwell_time = 100
discharge = FAST
on_fail = ABORT
""")
        patterns.append(default_path)

    configs = []
    for cfg_file in patterns:
        cp = configparser.ConfigParser()
        cp.read(cfg_file)
        if "DCW" not in cp:
            continue
        cfg = DCWTestConfig(
            name=os.path.splitext(os.path.basename(cfg_file))[0],
            voltage=cp.getint("DCW", "voltage", fallback=1000),
            current_limit=cp.getfloat("DCW", "current_limit", fallback=0.01),
            ramp_time=cp.getint("DCW", "ramp_time", fallback=500),
            dwell_time=cp.getint("DCW", "dwell_time", fallback=100),
            discharge=cp.get("DCW", "discharge", fallback="FAST"),
            on_fail=cp.get("DCW", "on_fail", fallback="ABORT")
        )
        configs.append(cfg)
    return configs

# -----------------------------
# Load Setup Configuration
# -----------------------------
def load_setup_config(config_path=SETUP_CONFIG_PATH):
    cp = configparser.ConfigParser()
    try:
        cp.read(config_path)
        ip = cp.get("Vitrek", "ip", fallback="169.254.107.36")
        port = cp.getint("Vitrek", "port", fallback=10733)
        local_ip = cp.get("Vitrek", "local_ip", fallback="169.254.202.17")
        timeout = cp.getfloat("Vitrek", "timeout", fallback=0.1)
        return ip, port, local_ip, timeout
    except (configparser.Error, FileNotFoundError) as e:
        print(Fore.RED + f"[ERROR] Could not load setup config from {config_path}: {e}")
        return "169.254.107.36", 10733, "169.254.202.17", 0.1  # Return defaults

# -----------------------------
# Logger for Test Data
# -----------------------------
class TestLogger:
    def __init__(self, test_id: str, cfg_name: str):
        self.cfg_name = cfg_name
        self.test_id = test_id
        self.filename = self._generate_filename(test_id, cfg_name)
        self.file = open(self.filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Time', 'Voltage', 'Current'])
        self.max_v = 0.0
        self.max_i = 0.0
        self.lock = threading.Lock()

    def _generate_filename(self, test_id, cfg_name):
        base = os.path.join(RAW_DATA_DIR, f"{test_id} - {cfg_name}")
        i = 0
        fname = f"{base}.csv"
        while os.path.exists(fname):
            i += 1
            fname = f"{base} ({i}).csv"
        return fname

    def log(self, t, v, i):
        with self.lock:
            self.writer.writerow([t, v, i])
        self.max_v = max(self.max_v, v)
        self.max_i = max(self.max_i, i)

    def close(self):
        with self.lock:
            self.file.close()

    def summary(self, result, duration):
        summary = {
            'Datetime': datetime.now().isoformat(),
            'Test_Config': self.cfg_name,
            'Test_ID': self.test_id,
            'Test_Result': result,
            'Max_Voltage (V)': self.max_v,
            'Max_Current (A)': self.max_i,
            'Duration (s)': round(duration, 2)
        }
        
        date_str = date.today().strftime("%Y-%m-%d")
        fname = os.path.join(SUMMARY_DIR, f"TestSummaries_{date_str}.csv")
        new_file = not os.path.exists(fname)
        with open(fname, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
            if new_file:
                writer.writeheader()
            writer.writerow(summary)
        
        return summary
        

# -----------------------------
# Instrument Communication with Retries
# -----------------------------
class Vitrek95LI:
    def __init__(self, ip="169.254.107.36", port=10733, local_ip="169.254.202.17",timeout=0.1):
        self.ip = ip
        self.port = port
        self.local_ip = local_ip
        self.timeout = timeout
        self.sock = None
        self.lock = threading.Lock()  # to protect socket use

    def connect(self):
        for attempt in range(MAX_RETRIES):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.bind((self.local_ip, 0))
                self.sock.settimeout(self.timeout)
                self.sock.connect((self.ip, self.port))

                print(Fore.CYAN + "[INFO] Connected to Vitrek 95LI at", self.ip)
                return True
            except Exception as e:
                print(Fore.RED + f"[ERROR] Connection attempt {attempt+1} failed: {e}")
                time.sleep(1)
        return False

    def close(self):
        if self.sock:
            try:
                self.sock.close()
                print(Fore.CYAN + "[INFO] Connection closed.")
            except:
                pass
            self.sock = None

    def send_command(self, cmd):
        """Send a command with retry."""
        cmd = cmd.strip() + "\n"
        for attempt in range(MAX_RETRIES):
            try:
                with self.lock:
                    self.sock.sendall(cmd.encode())
                return True
            except Exception as e:
                print(Fore.RED + f"[ERROR] Send attempt {attempt+1} failed: {e}")
                time.sleep(0.5)
        return False

    def query(self, cmd):
        """Send a command and receive the response with retry."""
        for attempt in range(MAX_RETRIES):
            try:
                with self.lock:
                    self.sock.sendall((cmd.strip() + "\n").encode())
                    data = self.sock.recv(4096)
                if not data:
                    raise IOError("No data received")
                return data.decode().strip()
            except Exception as e:
                print(Fore.RED + f"[ERROR] Query attempt {attempt+1} failed: {e}")
                time.sleep(0.5)
        return None

    def check_connection(self):
        """Basic command to verify instrument is responsive."""
        resp = self.query("*IDN?")
        if resp:
            print(Fore.CYAN + f"[INFO] Instrument ID: {resp}")
            return True
        print(Fore.RED + "[ERROR] No response from instrument.")
        return False

# -----------------------------
# Test Thread that runs the DCW test sequence
# -----------------------------
class TestRunnerThread(threading.Thread):
    def __init__(self, instrument: Vitrek95LI, config: DCWTestConfig, test_id: str):
        super().__init__()
        self.instrument = instrument
        self.config = config
        self.test_id = test_id
        self.logger = TestLogger(test_id, config.name)
        self.abort_event = threading.Event()
        self.result = "UNKNOWN"
        self.duration = 0

    def run(self):
##        print(Fore.CYAN + f"[INFO] Test thread started for test ID {self.test_id}")
        max_duration = self.config.ramp_time + self.config.dwell_time + 10  # extra 10s buffer
        elapsed = 0
        last_measurement = 0

        for attempt in range(MAX_RETRIES):
            try:
                test_running = self.instrument.query("RUN?")

                self.instrument.send_command("*RST")
                time.sleep(2 if test_running == "1" else 0.1)
                self.instrument.send_command(format_dcw_command(self.config))
                # print(format_dcw_command(self.config))
                time.sleep(0.05)
                self.instrument.send_command("RUN")
                start_time = time.time()
                time.sleep(0.05)

                if self.instrument.query("RUN?") == "1":
##                    print(Fore.BLUE + f"[INFO] Test sequence started for test ID {self.test_id}")
                    break
                else:
                    print(Fore.RED + "[ERROR] Failed to start test.")
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Test start attempt {attempt+1} failed: {e}")
        else:
            print(f"{Fore.RED}[FATAL] Unable to start test")
            self.result = "FAIL"
            self.abort_event.set()

        try:
            while elapsed < max_duration and not self.abort_event.is_set():
                if time.time() - last_measurement < 0.1:
                    continue
                
                voltage_resp = self.instrument.query("MEASRSLT?,VOLTS")
                current_resp = self.instrument.query("MEASRSLT?,AMPS")
                test_running = self.instrument.query("RUN?")
                last_measurement = time.time()
                
                if test_running != "1":
##                    print(Fore.CYAN + "\n[INFO] Test no longer running")
                    summary_data = self.instrument.query("STEPRSLT?,1").split(",")
                    # print(summary_data)
                    
                    if summary_data[2] == "0":
                        self.result = "PASS"
                    elif summary_data[2] == "4":
                        self.result = "BREAKDOWN DETECTED"
                    else:
                        self.result = f"VITREK ERROR: {summary_data[2]}"                    
                    break

                if voltage_resp is None or current_resp is None:
                    print(Fore.RED + "   [ERROR] Failed to read instrument data.")
                    # self.result = "FAIL"
                    # break

                try:
                    voltage = float(voltage_resp)
                    current = float(current_resp)
                except ValueError:
                    print(Fore.RED + "   [ERROR] Invalid data received.")
                    # self.result = "FAIL"
                    # break

                self.logger.log(round(elapsed,2), voltage, current)

                if current > self.config.current_limit:
                    print(Fore.RED + f"   [FAIL] Current limit exceeded: {current:.4f}A > {self.config.current_limit}A")
                    # self.result = "FAIL"
            
                # time.sleep(0.1)  # 10 Hz approx
                elapsed = time.time() - start_time
                
                render_dual_section_bar(elapsed,self.config.ramp_time,self.config.dwell_time)
                # print(elapsed)

        except Exception as e:
            print(Fore.RED + f"   [ERROR] Exception in test thread: {e}")
            self.result = "FAIL"

        self.duration = time.time() - start_time
        self.logger.close()
        print(Fore.CYAN + f"\r[INFO] Test thread for test ID {self.test_id} finished with result: {self.result}       ")

    def abort(self):
        print(Fore.MAGENTA + "[INFO] Abort signal received.")
        
        self.abort_event.set()

# -----------------------------
# User Input Helpers with Validation Loops
# -----------------------------
def select_config(configs):
    while True:
        print(Style.BRIGHT + Fore.CYAN + "\n"*2 + "=" * 90 + "\n"
              + "     TEST CONFIGURATIONS     ".center(90, "~") + "\n"
              + "=" * 90)        
        
        print(f"{'─' * 4}┬{'─' * 85}")
        for i, cfg in enumerate(configs, 1):
            print(f"{Fore.MAGENTA}{Style.BRIGHT}{i:^4}{Style.RESET_ALL}│ {Style.BRIGHT}{cfg.name:<15} {Fore.LIGHTBLACK_EX} {cfg.voltage}V, {cfg.current_limit*1e3}mA breakdown limit, {cfg.ramp_time}s ramp time, {cfg.dwell_time}s dwell time")
            if i < len(configs):   print(f"{'─' * 4}┼{'─' * 85}")
        print(f"{'─' * 4}┴{'─' * 85}")
        choice = input(Fore.MAGENTA + "Select a configuration by number: \n"+Fore.RESET+">>> ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(configs):
                print(f"{Fore.CYAN}Selected config: {configs[idx].name}")
                return configs[idx]
        print(Fore.RED + "Invalid selection. Please enter a valid number.")

def prompt_test_id():
    while True:
        test_id = input(Fore.MAGENTA + "\nEnter test ID: \n"+Fore.RESET+">>> ").strip()
        if test_id:
            return test_id
        print(Fore.RED + "Invalid test ID")

def render_dual_section_bar(elapsed, section1_duration, section2_duration, total_width=50):
    total_duration = section1_duration + section2_duration
    bar_width = total_width

    # Calculate widths of the two sections
    section1_width = int((section1_duration / total_duration) * bar_width)
    section2_width = bar_width - section1_width

    # Calculate progress
    section1_elapsed = min(elapsed, section1_duration)
    section2_elapsed = max(0, elapsed - section1_duration)

    section1_fill = int((section1_elapsed / section1_duration) * section1_width) if section1_duration > 0 else 0
    section2_fill = int((section2_elapsed / section2_duration) * section2_width) if section2_duration > 0 else 0

    # Create bar parts
    section1_bar = (
        Fore.CYAN + '█' * section1_fill +
        Fore.LIGHTBLACK_EX + '░' * (section1_width - section1_fill)
    )

    section2_bar = (
        Fore.MAGENTA + '█' * section2_fill +
        Fore.LIGHTMAGENTA_EX + '░' * (section2_width - section2_fill)
    )
    
     # Combine and print
    bar = Style.BRIGHT + Fore.WHITE + '┃' + section1_bar + section2_bar + Fore.WHITE + '┃'
    sys.stdout.write(f"\r{bar}{Style.RESET_ALL}   {elapsed:.1f} / {total_duration:.1f}s")
    sys.stdout.flush()

# -----------------------------
# Main Loop
# -----------------------------
def main():
    global running_test_thread

    disp_splash_screen()    

    configs = load_configs()
    ip, port, local_ip, timeout = load_setup_config() # Load setup config

    instrument = Vitrek95LI(ip, port, local_ip, timeout) # Pass setup config to Vitrek95LI
    if not instrument.connect():
        input(Fore.RED + "[FATAL] Could not connect to instrument. Exiting.")
        # return
    if not instrument.check_connection():
        instrument.close()
        input(Fore.RED + "[FATAL] Instrument check failed. Exiting.")
        # return

    try:
        config = select_config(configs)
        
        while True:
            test_id = prompt_test_id()

            running_test_thread = TestRunnerThread(instrument, config, test_id)
            running_test_thread.start()

            while running_test_thread.is_alive():
                time.sleep(0.1)

            summary = running_test_thread.logger.summary(running_test_thread.result, running_test_thread.duration)

            print(Fore.GREEN + f"\nTest Summary:\n"
                  f"  Result: {summary['Test_Result']}\n"
                  f"  Max Voltage: {summary['Max_Voltage (V)']:.2f} V\n"
                  f"  Max Current: {summary['Max_Current (A)']*1e3:.4f} mA\n"
                  f"  Duration: {summary['Duration (s)']} seconds\n")

    finally:
        instrument.send_command("ABORT")
        instrument.close()
        input(Fore.MAGENTA + "Exiting program. Goodbye!")
        
if __name__ == "__main__":
    main()
