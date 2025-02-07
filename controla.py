from controla.controles import MovementHelper
from assist_connector import UOAssistConnector
from controla.controle_keyboard import KeyboardController
from controla.controle_keyboard_janela import KeyboardControllerWindow
import win32gui
import ctypes
import time
import random
import pyautogui
import keyboard

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
    print("3. Calibra posicoes ")
    print("4. Testes gerais ")
    choice = input("Escolha uma opção: ")
    
    if choice == "1":

        helper.record_position_xy(uo_assist)
    
    elif choice == "2":
        def delay_variavel():
            return random.uniform(0.2, 0.3)
        
        def clica_loot_timer():
            helper.clica_loot(qtde=10)
            helper.random_sleep(0.1,0.2)
        
        def on_move_log():
            print(f"Personagem se moveu... ")

        def on_move_click():
            clica_loot_timer()
            helper.random_sleep(0.5,0.7)
        
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
                    helper.execute_movement_path(uo_assist, path,stuck_threshold=5,tolerance=1) 
            else:
                print("Iniciando "+choice+" - Va para a tela")
                time.sleep(3)
                helper.execute_movement_path(uo_assist, path,stuck_threshold=5,tolerance=1)
    elif choice == "4":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
    else:
        print("Opção inválida!")


