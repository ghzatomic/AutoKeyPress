import win32gui
import win32con
import win32api
import time

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

def choose_window_and_send_key(key):
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

    # Envia a tecla para a janela escolhida
    send_key_to_window_by_handle(hwnd, key)

# Exemplo de uso: Escolher uma janela e enviar a tecla "a"
choose_window_and_send_key("left")
