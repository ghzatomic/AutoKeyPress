import ctypes
import win32gui
import win32con
import win32api
import psutil
import subprocess
import sys

class UOAssistConnector:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.hwnd_console = self.kernel32.GetConsoleWindow()
        self.uoassist_hwnd = None
        self.WM_USER = 0x0400
        self.MSG_SEND_ATTACH_TO_UO = self.WM_USER + 200
        self.MSG_SEND_GET_LOCATION_INFO = self.WM_USER + 202
        self.SendMessage = self.user32.SendMessageW
        self.SendMessageA = self.user32.SendMessageA
        self.GetWindowThreadProcessId = self.user32.GetWindowThreadProcessId
        self.GetCurrentProcessId = self.kernel32.GetCurrentProcessId
        self.isAttached = False

    def run_as_admin(self):
        """ Reexecuta o script como administrador, se necessário. """
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Reexecutando como administrador...")

            script_path = sys.argv[0]
            python_exe = sys.executable

            command = f'Start-Process -FilePath "{python_exe}" -ArgumentList "{script_path}" -Verb RunAs'

            try:
                subprocess.run(["powershell", "-Command", command], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Erro ao executar como administrador: {e}")
            sys.exit()

    def list_windows(self):
        """ Lista todas as janelas abertas no sistema. """
        def enum_windows_callback(hwnd, windows_list):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                windows_list.append((hwnd, win32gui.GetWindowText(hwnd)))

        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        return windows

    def find_window_by_class(self, class_name):
        """ Procura uma janela pelo nome da classe """
        hwnd = win32gui.FindWindow(class_name, None)
        if hwnd:
            print(f"Encontrado HWND para {class_name}: {hex(hwnd)}")
        else:
            print(f"Janela {class_name} não encontrada.")
        return hwnd

    def get_process_from_hwnd(self, hwnd):
        """ Obtém o processo associado a um HWND """
        pid = ctypes.c_uint()
        self.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        if pid.value == 0:
            print("Falha ao obter PID.")
            return None

        try:
            proc = psutil.Process(pid.value)
            return proc
        except psutil.NoSuchProcess:
            print("Processo não encontrado.")
            return None

    def attach_to_assistant(self):
        if self.isAttached:
            return True
        """ Conecta o programa ao UOAssist """
        self.uoassist_hwnd = self.find_window_by_class("UOASSIST-TP-MSG-WND")
        
        if not self.uoassist_hwnd:
            print("UOAssist não encontrado.")
            return False

        proc = self.get_process_from_hwnd(self.uoassist_hwnd)
        if proc:
            print(f"Assistants found: {proc.name()}")

            title_buffer = ctypes.create_string_buffer(510)
            self.SendMessageA(self.uoassist_hwnd, 13, 510, title_buffer)
            print(f"Título da Janela: {title_buffer.value.decode('utf-8', errors='ignore')}")

            f = self.SendMessage(self.uoassist_hwnd, self.MSG_SEND_ATTACH_TO_UO, self.hwnd_console, 1)

            if f > 1:
                for _ in range(f):
                    f = self.SendMessage(self.uoassist_hwnd, self.MSG_SEND_ATTACH_TO_UO, self.hwnd_console, 1)

            if f == 1:
                print("Anexado com sucesso!")
                self.isAttached = True
                return True
        self.isAttached = False
        return False

    def get_character_coords(self):
        """ Obtém as coordenadas do personagem no UOAssist """
        if not self.uoassist_hwnd:
            print("Erro: UOAssist não está anexado.")
            return None

        loc = self.SendMessage(self.uoassist_hwnd, self.MSG_SEND_GET_LOCATION_INFO, 0, 0)

        if loc > 0:
            x = loc & 0xFFFF  # Parte baixa (16 bits inferiores)
            y = (loc >> 16) & 0xFFFF  # Parte alta (16 bits superiores)
            #print(f"Coordenadas do personagem: X={x}, Y={y}")
            return x, y
        else:
            print("Falha ao obter coordenadas.")
            return None

# =======================
# Exemplo de Uso da Classe
# =======================
if __name__ == "__main__":
    uo_assist = UOAssistConnector()
    
    # Executar como administrador
    uo_assist.run_as_admin()

    # Conectar ao UOAssist
    if uo_assist.attach_to_assistant():
        # Obter coordenadas
        coords = uo_assist.get_character_coords()
