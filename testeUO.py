import os
import win32gui
import win32con
import win32api
import time

WM_USER = 0x0400  # Valor base do WM_USER
ATTACH_TO_UO = WM_USER + 200
WM_GET_COORDS = WM_USER + 202

def list_windows():
    """
    Lista todas as janelas abertas no sistema.
    """
    def enum_windows_callback(hwnd, windows_list):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            windows_list.append((hwnd, win32gui.GetWindowText(hwnd)))

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows

def send_key_to_window_by_handle(hwnd, key):
    """
    Envia uma tecla para uma janela específica pelo handle (hwnd).

    Args:
        hwnd (int): Handle da janela onde a tecla será enviada.
        key (str): Tecla a ser enviada (como 'a', 'b', 'up', 'down').
    """
    # Mapear teclas para seus códigos virtuais
    key_mapping = {
        "up": win32con.VK_UP,
        "down": win32con.VK_DOWN,
        "left": win32con.VK_LEFT,
        "right": win32con.VK_RIGHT,
    }

    # Adicionar teclas de caracteres usando ord() para converter em código virtual
    if len(key) == 1 and key.isprintable():  # Verifica se é uma tecla de caractere
        key_code = ord(key.upper())  # Converte para código virtual (e maiúsculo)
    elif key in key_mapping:  # Se for seta ou outra tecla especial
        key_code = key_mapping[key]
    else:
        print(f"Tecla '{key}' não suportada.")
        return

    print(f"Enviando tecla '{key}' para a janela com handle {hwnd}...")

    # Envia o comando de pressionar e liberar a tecla
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key_code, 0)
    time.sleep(0.1)  # Simula o tempo de pressão
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, key_code, 0)

    print(f"Tecla '{key}' enviada com sucesso.")





# Função para separar LOWORD e HIWORD do retorno
def loword(dword):
    return dword & 0xFFFF

def hiword(dword):
    return (dword >> 16) & 0xFFFF

# Função para enviar mensagem e obter as coordenadas
def get_coords(hwnd):
    pid = os.getpid()
    f = win32api.SendMessage(hwnd, ATTACH_TO_UO,pid,1)
    if f > 1:
        f1 = f
        for i in range(f1):
            f = win32api.SendMessage(hwnd, int(ATTACH_TO_UO),pid,1)
    print(f)
    ret_val = win32api.SendMessage(hwnd, WM_GET_COORDS)
    
    # Separar o valor retornado em X (LOWORD) e Y (HIWORD)
    x = loword(ret_val)
    y = hiword(ret_val)
    
    return x, y

def test():
    """
    Lista as janelas disponíveis, permite ao usuário escolher uma, e envia a tecla.

    Args:
        key (str): Tecla a ser enviada (como 'a', 'b', 'up', 'down').
    """
    # Lista todas as janelas visíveis
    windows = list_windows()

    if not windows:
        print("Nenhuma janela encontrada.")
        return

    # Exibe as janelas encontradas
    print("Janelas disponíveis:")
    for i, (hwnd, title) in enumerate(windows):
        print(f"[{i}] {title}")

    # Pede ao usuário para escolher uma janela
    choice = input("Escolha o número da janela onde enviar a tecla: ")
    try:
        choice = int(choice)
        if choice < 0 or choice >= len(windows):
            print("Escolha inválida.")
            return
    except ValueError:
        print("Escolha inválida.")
        return

    hwnd, title = windows[choice]
    print(f"Janela escolhida: {title}")
    try:
        coords = get_coords(hwnd)
        print(f"Coordenadas atuais: {coords[0]}")
    except Exception as e:
        print(f"Erro: {e}")
    # Envia a tecla para a janela escolhida
    #send_key_to_window_by_handle(hwnd, key)



test()
