import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import time
import random
import threading
import ctypes
import pyautogui
import keyboard
import win32gui

# Importa os módulos do seu bot
from controla.controles import MovementHelper
from assist_connector import UOAssistConnector
from controla.controle_keyboard import KeyboardController
from controla.controle_keyboard_janela import KeyboardControllerWindow




#from controla.controles import MovementHelper
#from assist_connector import UOAssistConnector
#from controla.controle_keyboard import KeyboardController
#from controla.controle_keyboard_janela import KeyboardControllerWindow
#import win32gui
#import ctypes
#import time
#import random
#import pyautogui
#import keyboard

def input_boolean(prompt="Deseja continuar? (s/n): "):
    while True:
        resposta = input(prompt).strip().lower()
        if resposta in ["s", "sim"]:
            return True
        elif resposta in ["n", "nao", "não"]:
            return False
        else:
            print("❌ Entrada inválida! Digite 's' para Sim ou 'n' para Não.")

WM_KEYDOWN = 0x0100
WM_KEYUP   = 0x0101

# Códigos de teclas virtuais (VK_*)
VK_A = 0x41  # Letra 'A'
VK_RETURN = 0x0D

# Funções da User32.dll
PostMessage = ctypes.windll.user32.PostMessageW

def capturar_posicao_mouse():
    print("Coloque o mouse na posição desejada e pressione F1...")
    # Aguarda até que a tecla F1 seja pressionada
    keyboard.wait('F1')
    # Após a tecla ser pressionada, captura a posição atual do mouse
    pos = pyautogui.position()
    print(f"Posição capturada: {pos}")  # Exibe, por exemplo, Point(x=100, y=200)
    return pos.x, pos.y

def list_visible_windows(filter_list=("uo", "ultima online")):
    """
    Retorna uma lista de (hwnd, título) para todas as janelas visíveis cujo título
    contenha alguma das substrings especificadas em filter_list (ignora maiúsculas/minúsculas).

    Parâmetros:
      filter_list (tuple of str): Tupla com as substrings para filtrar os títulos das janelas.
                                  Valor padrão: ("uo", "ultima online")
    """
    windows = []
    
    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                title_lower = title.lower()
                # Verifica se alguma das substrings está presente no título
                if any(sub in title_lower for sub in filter_list):
                    windows.append((hwnd, title))
    
    win32gui.EnumWindows(enum_windows_callback, None)
    return windows

def choose_window_and_focus():
    """
    Exibe um menu com as janelas disponíveis e permite que o usuário
    escolha uma delas. Retorna (hwnd, titulo) da janela selecionada.
    """
    all_windows = list_visible_windows()
    
    if not all_windows:
        print("Nenhuma janela visível encontrada.")
        return None, None
    
    # Exibe o menu enumerado
    print("=== Selecione a janela desejada ===")
    for i, (hwnd, title) in enumerate(all_windows):
        print(f"{i}) {title} (HWND={hwnd})")
    
    # Loop de leitura
    while True:
        choice_str = input("Digite o número da janela: ")
        try:
            choice = int(choice_str)
            if 0 <= choice < len(all_windows):
                break
        except ValueError:
            pass
        print("Opção inválida. Tente novamente.")
    
    target_hwnd, target_title = all_windows[choice]
    
    # Traz a janela para frente
    
    print(f"\nJanela selecionada: {target_title} (HWND={target_hwnd})")
    return target_hwnd, target_title

SETTINGS_FILE = "settings.json"



# -----------------------------------------------------------
# Tela principal (menu)
# -----------------------------------------------------------
class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Charger")
        self.settings_file = "settings.json"
        self.create_widgets()

        self.load_settings()

        self.uo_assist = UOAssistConnector()
        self.uo_assist.run_as_admin()
        if self.uo_assist.attach_to_assistant():
            coords = self.uo_assist.get_character_coords()
            print("Coordenadas iniciais:", coords)

    def create_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Escolha a função:").grid(row=0, column=0, pady=5)
        btn_record = ttk.Button(frame, text="Gravar Posições", command=self.open_record_window)
        btn_record.grid(row=1, column=0, pady=5)
        btn_read = ttk.Button(frame, text="Ler Movimentos", command=self.open_read_window)
        btn_read.grid(row=2, column=0, pady=5)
        btn_exit = ttk.Button(frame, text="Sair", command=self.destroy)
        btn_exit.grid(row=3, column=0, pady=5)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def load_settings(self):
        # Carrega configurações gerais (por exemplo, delays, checkbox, etc.)
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                settings = json.load(f)
            self.default_min_delay = float(settings.get("delay_min", "0.2"))
            self.default_max_delay = float(settings.get("delay_max", "0.5"))
        else:
            self.default_min_delay = 0.2
            self.default_max_delay = 0.5

    def open_record_window(self):
        RecordWindow(self, self.default_min_delay, self.default_max_delay, self.settings_file)

    def open_read_window(self):
        ReadWindow(self, self.settings_file, self.uo_assist)


# -----------------------------------------------------------
# Janela para gravação de posições (Gravar Posições)
# -----------------------------------------------------------
class RecordWindow(tk.Toplevel):
    def __init__(self, parent, default_min_delay, default_max_delay, settings_file):
        super().__init__(parent)
        self.title("Gravar Posições")
        self.settings_file = settings_file
        self.default_min_delay = default_min_delay
        self.default_max_delay = default_max_delay
        self.create_widgets()
        # Instancia o UOAssistConnector e controlador (aqui, podemos utilizar o modo padrão)
        self.uo_assist = UOAssistConnector()
        self.uo_assist.run_as_admin()
        if self.uo_assist.attach_to_assistant():
            coords = self.uo_assist.get_character_coords()
            print("Coordenadas iniciais:", coords)
        # Para este exemplo, usamos o controlador padrão
        from_controlador = KeyboardController()
        self.helper = MovementHelper(from_controlador)

    def create_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Delay mínimo (s):").pack(pady=5)
        self.entry_min = ttk.Entry(frame)
        self.entry_min.pack(pady=5)
        self.entry_min.insert(0, str(self.default_min_delay))

        ttk.Label(frame, text="Delay máximo (s):").pack(pady=5)
        self.entry_max = ttk.Entry(frame)
        self.entry_max.pack(pady=5)
        self.entry_max.insert(0, str(self.default_max_delay))

        btn_start = ttk.Button(frame, text="Iniciar Gravação", command=self.start_recording)
        btn_start.pack(pady=10)

    def start_recording(self):
        try:
            min_delay = float(self.entry_min.get())
            max_delay = float(self.entry_max.get())
            # Chama o método real de gravação passando os delays da tela
            self.helper.record_position_xy(self.uo_assist, default_min_delay=min_delay, default_max_delay=max_delay)
            messagebox.showinfo("Gravar Posições", "Gravação finalizada.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gravar posições: {e}")


# -----------------------------------------------------------
# Janela para leitura/executar movimentos (Ler Movimentos)
# -----------------------------------------------------------
class ReadWindow(tk.Toplevel):
    def __init__(self, parent, settings_file, uo_assist):
        super().__init__(parent)
        self.title("Ler Movimentos")
        self.settings_file = settings_file
        self.uo_assist = uo_assist
        self.path = None
        self.current_index = 0
        self.click_mode_var = tk.BooleanVar(value=True)  # Ativado por padrão
        self.macro_loop_var = tk.BooleanVar(value=True)    # Loop ativado por padrão
        self.macro_running = True
        self.macro_paused = False
        self.selected_filename = None
        self.json_data = None
        self.selected_window = None
        self.selected_position = None

        self.create_widgets()
        self.helper = MovementHelper(KeyboardController())
        self.load_path()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        btn_select = ttk.Button(frame, text="Selecionar Arquivo de Movimentos", command=self.load_path)
        btn_select.pack(pady=5)

        self.btn_click_mode = ttk.Button(frame, text="Desativar Click Sem Foco", command=self.toggle_click_mode)
        self.btn_click_mode.pack(pady=5)

        self.ignore_delay_var = tk.BooleanVar(value=False)
        self.checkbox_ignore = ttk.Checkbutton(frame, text="Ignorar delay (Manual)", variable=self.ignore_delay_var)
        self.checkbox_ignore.pack(pady=5)
        self.ignore_delay_var.trace_add("write", self.update_buttons)

        self.checkbox_loop = ttk.Checkbutton(frame, text="Macro Loop", variable=self.macro_loop_var)
        self.checkbox_loop.pack(pady=5)

        # Botões de controle em linha
        control_frame = ttk.Frame(frame)
        control_frame.pack(pady=5)
        self.btn_prev = ttk.Button(control_frame, text="<<", command=self.execute_prev)
        self.btn_prev.pack(side="left", padx=5)
        self.btn_pause = ttk.Button(control_frame, text="||", command=self.toggle_pause)
        self.btn_pause.pack(side="left", padx=5)
        self.btn_next = ttk.Button(control_frame, text=">>", command=self.execute_next)
        self.btn_next.pack(side="left", padx=5)

        self.btn_execute_auto = ttk.Button(frame, text="Executar Macro Automática", command=self.execute_auto)
        self.btn_execute_auto.pack(pady=5)

        self.btn_exit = ttk.Button(frame, text="Sair", command=self.exit_macro)
        self.btn_exit.pack(pady=5)

        self.status_label = ttk.Label(frame, text="Nenhum arquivo carregado.")
        self.status_label.pack(pady=5)

        self.json_text = tk.Text(frame, height=10, width=50)
        self.json_text.pack(pady=5)
        self.update_json_text()

    def update_buttons(self, *args):
        # Aqui os botões de controle já ficam disponíveis
        pass

    def toggle_click_mode(self):
        current = self.click_mode_var.get()
        self.click_mode_var.set(not current)
        if self.click_mode_var.get():
            self.btn_click_mode.config(text="Desativar Click Sem Foco")
        else:
            self.btn_click_mode.config(text="Ativar Click Sem Foco")

    def toggle_pause(self):
        self.macro_paused = not self.macro_paused
        if self.macro_paused:
            self.btn_pause.config(text="▶")
            self.status_label.config(text="Macro pausada.")
        else:
            self.btn_pause.config(text="||")
            self.status_label.config(text="Macro em execução.")

    def exit_macro(self):
        self.macro_running = False
        self.destroy()

    def update_json_text(self):
        self.json_text.delete("1.0", tk.END)
        header = f"Movimento atual: {self.current_index+1} de {len(self.path) if self.path else 0}\n"
        if self.json_data and self.current_index < len(self.json_data):
            movement = self.json_data[self.current_index]
            json_str = json.dumps(movement, indent=2)
        else:
            json_str = "Nenhum movimento a executar."
        self.json_text.insert(tk.END, header + json_str)

    def load_path(self):
        def gui_selection_callback(files):
            if files is None:
                files = [f for f in os.listdir("gravados") if f.endswith(".json")]
            file_list = "\n".join([f"{i+1}: {file}" for i, file in enumerate(files)])
            choice = simpledialog.askinteger("Selecionar Arquivo",
                                             f"Arquivos disponíveis:\n{file_list}\n\nDigite o número do arquivo:")
            if choice is None or choice < 1 or choice > len(files):
                messagebox.showwarning("Aviso", "Nenhum arquivo selecionado!")
                return None
            return files[choice - 1]
        self.status_label.config(text="Carregando arquivo de movimentos...")
        if not self.selected_filename:
            files = [f for f in os.listdir("gravados") if f.endswith(".json")]
            if not files:
                messagebox.showwarning("Aviso", "Nenhum arquivo encontrado na pasta 'gravados'.")
                return
            filename = gui_selection_callback(files)
            if filename is None:
                self.status_label.config(text="Nenhum caminho de movimento carregado.")
                return
            self.selected_filename = filename
        path = self.helper.load_movement_path_with_selection(
            self.uo_assist,
            selection_callback=lambda files: self.selected_filename
        )
        if path:
            self.path = path
            self.current_index = 0
            self.status_label.config(text=f"Arquivo carregado: {len(self.path)} pontos.")
            try:
                with open(os.path.join("gravados", self.selected_filename), "r") as f:
                    self.json_data = json.load(f)
            except Exception as e:
                self.json_data = None
                messagebox.showerror("Erro", f"Erro ao ler JSON: {e}")
            self.update_json_text()
        else:
            self.status_label.config(text="Nenhum caminho de movimento carregado.")
            self.json_data = None
            self.update_json_text()

    def choose_window_and_focus(self):
        windows = []
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and ("uo" in title.lower() or "ultima online" in title.lower()):
                    windows.append((hwnd, title))
        win32gui.EnumWindows(enum_windows_callback, None)
        if not windows:
            messagebox.showerror("Erro", "Nenhuma janela visível encontrada.")
            return None, None
        lista = "\n".join([f"{i}: {title} (HWND={hwnd})" for i, (hwnd, title) in enumerate(windows)])
        selection = simpledialog.askinteger("Selecionar Janela", f"Escolha o número da janela:\n{lista}")
        if selection is None or selection < 0 or selection >= len(windows):
            return None, None
        hwnd, title = windows[selection]
        messagebox.showinfo("Janela selecionada", f"{title} (HWND={hwnd})")
        return hwnd, title

    def capturar_posicao_mouse(self):
        messagebox.showinfo("Capturar Posição", "Coloque o mouse na posição desejada e pressione F1.")
        keyboard.wait('F1')
        pos = pyautogui.position()
        messagebox.showinfo("Posição Capturada", f"Posição: {pos}")
        return pos.x, pos.y

    def run_macro_auto(self, new_path):
        self.status_label.config(text="Executando macro automática...")
        while self.macro_running:
            for idx, point in enumerate(new_path):
                while self.macro_paused and self.macro_running:
                    time.sleep(0.1)
                if not self.macro_running:
                    break
                self.current_index = idx
                self.after(0, self.update_json_text)
                (x, y, step_delay_fn, move_callback_before, move_callback_after,
                 tolerance, moves_after, exec_callback_after, exec_callback_before,
                 wait_between_moves_after, exec_scripts_after) = point
                if exec_callback_before and move_callback_before:
                    move_callback_before()
                if self.click_mode_var.get():
                    def on_move():
                        self.helper.clica_loot(qtde=1)
                else:
                    def on_move():
                        print("Movimento executado.")
                self.helper.move_to_target_smart_v2(
                    self.uo_assist,
                    target_x=x,
                    target_y=y,
                    step_delay_fn=lambda: 0.26,
                    tolerance=tolerance,
                    stuck_threshold=5,
                    on_move_callback=on_move
                )
                if moves_after:
                    for move in moves_after:
                        self.helper.controlador.press_and_release(move, delay_ini=0.3)
                        if wait_between_moves_after:
                            time.sleep(wait_between_moves_after)
                if exec_scripts_after:
                    for script in exec_scripts_after:
                        self.helper.controlador.send_text(script, delay=0.3)
                        if wait_between_moves_after:
                            time.sleep(wait_between_moves_after)
                if exec_callback_after and move_callback_after:
                    move_callback_after()
                time.sleep(step_delay_fn())
                self.after(0, self.update_json_text)
            self.current_index = 0
            self.after(0, self.update_json_text)
            if not self.macro_loop_var.get():
                break
        try:
            self.status_label.config(text="Macro finalizada.")
            self.after(0, self.update_json_text)
        except:
            pass

    def execute_auto(self):
        if self.click_mode_var.get():
            if self.selected_window is None:
                hwnd, title = self.choose_window_and_focus()
                if hwnd:
                    pos = self.capturar_posicao_mouse()
                    if pos:
                        self.selected_window = hwnd
                        self.selected_position = pos
                        new_controller = KeyboardControllerWindow(hwnd, pos[0], pos[1]-20)
                        self.helper = MovementHelper(new_controller)
                    else:
                        messagebox.showerror("Erro", "Não foi possível capturar a posição do mouse. Usando controlador padrão.")
                        self.helper = MovementHelper(KeyboardController())
                else:
                    messagebox.showerror("Erro", "Nenhuma janela selecionada. Usando controlador padrão.")
                    self.helper = MovementHelper(KeyboardController())
            if self.click_mode_var.get():
                def on_move():
                    self.helper.clica_loot(qtde=1)
                    time.sleep(random.uniform(0.4, 0.6))
                # Se não estiver no modo click, apenas imprime
            else:
                def on_move():
                    print("Movimento executado.")
            new_path = []
            for point in self.path:
                new_tuple = (point[0], point[1], point[2], on_move, on_move, point[5],
                             point[6], point[7], point[8], point[9], point[10])
                new_path.append(new_tuple)
            self.macro_running = True
            threading.Thread(target=self.run_macro_auto, args=(new_path,), daemon=True).start()

    def execute_next(self):
        if self.path is None:
            messagebox.showwarning("Aviso", "Nenhum caminho carregado.")
            return
        if self.current_index >= len(self.path):
            self.current_index = 0
            messagebox.showinfo("Reiniciar", "Todos os movimentos foram executados. Reiniciando macro.")
            self.update_json_text()
        if self.click_mode_var.get() and self.selected_window is None:
            hwnd, title = self.choose_window_and_focus()
            if hwnd:
                pos = self.capturar_posicao_mouse()
                if pos:
                    self.selected_window = hwnd
                    self.selected_position = pos
                    new_controller = KeyboardControllerWindow(hwnd, pos[0], pos[1]-20)
                    self.helper = MovementHelper(new_controller)
                else:
                    messagebox.showerror("Erro", "Não foi possível capturar a posição do mouse. Usando controlador padrão.")
                    self.helper = MovementHelper(KeyboardController())
            else:
                messagebox.showerror("Erro", "Nenhuma janela selecionada. Usando controlador padrão.")
                self.helper = MovementHelper(KeyboardController())
        self.update_json_text()
        point = self.path[self.current_index]
        (x, y, step_delay_fn, move_callback_before, move_callback_after,
         tolerance, moves_after, exec_callback_after, exec_callback_before,
         wait_between_moves_after, exec_scripts_after) = point
        if exec_callback_before and move_callback_before:
            move_callback_before()
        if self.click_mode_var.get():
            def on_move():
                self.helper.clica_loot(qtde=1)
        else:
            def on_move():
                print("Movimento executado.")
        self.helper.move_to_target_smart_v2(
            self.uo_assist,
            target_x=x,
            target_y=y,
            step_delay_fn=lambda: 0.26,
            tolerance=tolerance,
            stuck_threshold=5,
            on_move_callback=on_move
        )
        if moves_after:
            for move in moves_after:
                self.helper.controlador.press_and_release(move, delay_ini=0.3)
                if wait_between_moves_after:
                    time.sleep(wait_between_moves_after)
        if exec_scripts_after:
            for script in exec_scripts_after:
                self.helper.controlador.send_text(script, delay=0.3)
                if wait_between_moves_after:
                    time.sleep(wait_between_moves_after)
        if exec_callback_after and move_callback_after:
            move_callback_after()
        self.current_index += 1
        self.status_label.config(text=f"Movimento {self.current_index} de {len(self.path)} executado.")
        self.update_json_text()

    def execute_prev(self):
        if self.path is None:
            messagebox.showwarning("Aviso", "Nenhum caminho carregado.")
            return
        if self.current_index <= 0:
            self.current_index = len(self.path) - 1
        else:
            self.current_index -= 1
        self.update_json_text()
        point = self.path[self.current_index]
        (x, y, step_delay_fn, move_callback_before, move_callback_after,
         tolerance, moves_after, exec_callback_after, exec_callback_before,
         wait_between_moves_after, exec_scripts_after) = point
        if exec_callback_before and move_callback_before:
            move_callback_before()
        if self.click_mode_var.get():
            def on_move():
                self.helper.clica_loot(qtde=1)
        else:
            def on_move():
                print("Movimento executado.")
        self.helper.move_to_target_smart_v2(
            self.uo_assist,
            target_x=x,
            target_y=y,
            step_delay_fn=lambda: 0.26,
            tolerance=tolerance,
            stuck_threshold=5,
            on_move_callback=on_move
        )
        self.status_label.config(text=f"Retornou para movimento {self.current_index+1} de {len(self.path)}.")
        self.update_json_text()


# -----------------------------------------------------------
# Main: escolha entre GUI ou Console
# -----------------------------------------------------------
def run_console_mode():
    print("Modo Console selecionado.")
    resposta_click_focus = input("Você quer ativar o modo de click sem foco? (s/n): ").strip().lower() in ["s", "sim"]
    uo_assist = UOAssistConnector()
    uo_assist.run_as_admin()
    if uo_assist.attach_to_assistant():
        coords = uo_assist.get_character_coords()
        print("Coordenadas iniciais:", coords)

    if resposta_click_focus:
        windows = []
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and ("uo" in title.lower() or "ultima online" in title.lower()):
                    windows.append((hwnd, title))
        win32gui.EnumWindows(enum_windows_callback, None)
        if not windows:
            print("Nenhuma janela visível encontrada.")
            return
        print("=== Selecione a janela desejada ===")
        for i, (hwnd, title) in enumerate(windows):
            print(f"{i}) {title} (HWND={hwnd})")
        while True:
            try:
                choice = int(input("Digite o número da janela: "))
                if 0 <= choice < len(windows):
                    break
            except ValueError:
                pass
            print("Opção inválida. Tente novamente.")
        hwnd, title = windows[choice]
        print(f"Janela selecionada: {title} (HWND={hwnd})")
        print("Coloque o mouse na posição desejada e pressione F1...")
        keyboard.wait('F1')
        pos = pyautogui.position()
        print(f"Posição capturada: {pos}")
        controlador = KeyboardControllerWindow(hwnd, pos.x, pos.y - 20)
    else:
        controlador = KeyboardController()

    helper = MovementHelper(controlador)

    print("1. Gravar posições")
    print("2. Ler posições")
    choice = input("Escolha uma opção: ").strip()
    if choice == "1":
        print("Iniciando gravação de posições...")
        helper.record_position_xy(uo_assist, default_min_delay=0.2, default_max_delay=0.5)
    elif choice == "2":
        path = helper.load_movement_path_with_selection(uo_assist)
        if path:
            print("Iniciando macro. Vá para a tela.")
            time.sleep(3)
            helper.execute_movement_path(uo_assist, path, stuck_threshold=5, tolerance=0)
        else:
            print("Nenhum caminho de movimento carregado.")
    else:
        print("Opção inválida!")

if __name__ == "__main__":
    use_gui = True#input("Executar com interface gráfica? (s/n): ").strip().lower() in ["s", "sim"]
    if use_gui:
        app = MainMenu()
        app.mainloop()
    else:
        run_console_mode()

'''
if __name__ == "__main__":
    pause_flag = False
    resposta_click_focus = input_boolean("Você quer ativar o modo de click sem foco ? (s/n): ")
    uo_assist = UOAssistConnector()
    
    # Executar como administrador
    uo_assist.run_as_admin()

    # Conectar ao UOAssist
    if uo_assist.attach_to_assistant():
        # Obter coordenadas
        coords = uo_assist.get_character_coords()

    controlador = None
    if resposta_click_focus:
        hwnd_uo, title = choose_window_and_focus()
        
        if hwnd_uo:
            if not hwnd_uo:
                print("Janela do Ultima Online não encontrada.")
                exit(1)

            print(f"HWND da janela do UO = {hwnd_uo}")
            posicaox,posicaoy = capturar_posicao_mouse()
            print(f"Posicao capturada : {posicaox},{posicaoy}")
            controlador = KeyboardControllerWindow(hwnd_uo,posicaox,posicaoy-20)
        else:
            print("Nenhuma janela selecionada ou erro ao focar a janela.")
        if not controlador:
            controlador = KeyboardController()
    else:
        controlador = KeyboardController()
    helper = MovementHelper(controlador)
    print("1. Gravar posições ")
    print("2. Ler posições ")
    print("3. Andar mina randomicamente")
    choice = input("Escolha uma opção: ")
    
    if choice == "1":

        helper.record_position_xy(uo_assist)
    
    elif choice == "2":
        def delay_variavel():
            return random.uniform(0.2, 0.3)
        
        def clica_loot_timer():
            helper.clica_loot(qtde=10)
            helper.random_sleep(0.2,0.3)
        
        def on_move_log():
            print(f"Personagem se moveu... ")

        def on_move_click():
            clica_loot_timer()
            helper.random_sleep(0.4,0.6)
        
        resposta_click = input_boolean("Você quer ativar o modo de click ? (s/n): ")
        resposta_click_loop = input_boolean("Você quer o macro em loop ? (s/n): ")

        move_callback_before = on_move_click if resposta_click else on_move_log
        move_callback_after = on_move_click if resposta_click else on_move_log

        path = helper.load_movement_path_with_selection(uo_assist,move_callback_after=move_callback_after, move_callback_before=move_callback_before)
        if path:
            if resposta_click_loop:
                while True:
                    print("Iniciando "+choice+" - Va para a tela")
                    time.sleep(3)
                    helper.execute_movement_path(uo_assist, path,stuck_threshold=5,tolerance=0) 
            else:
                print("Iniciando "+choice+" - Va para a tela")
                time.sleep(3)
                helper.execute_movement_path(uo_assist, path,stuck_threshold=5,tolerance=0)
    elif choice == "3":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        helper.random_walk_neighbors(x_ini=2482, y_ini=678, x_fim=2593, y_fim=727, uo_assist=uo_assist)
    else:
        print("Opção inválida!")


'''