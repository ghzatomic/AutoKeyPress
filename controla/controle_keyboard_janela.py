import time
import ctypes
from pynput.keyboard import Key
import win32gui
import win32con

#
# Constantes e mapeamentos
#
WM_KEYDOWN     = 0x0100
WM_KEYUP       = 0x0101
WM_MOUSEMOVE   = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP   = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP   = 0x0205
WM_MOUSEWHEEL  = 0x020A
WM_MOUSEHWHEEL = 0x020E

MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002

# A “unidade” de rolagem. Geralmente 120 corresponde a 1 “tick” de scroll
WHEEL_DELTA = 120

# Mapear teclas especiais do pynput.Key para Virtual-Key Codes
KEY_MAP = {
    Key.up:    0x26,  # VK_UP
    Key.down:  0x28,  # VK_DOWN
    Key.left:  0x25,  # VK_LEFT
    Key.right: 0x27,  # VK_RIGHT
    Key.alt:   0x12   # VK_MENU
    # Adicione aqui se precisar (Key.shift, Key.ctrl, Key.esc, etc.)
}

# Carregando funções da user32.dll via ctypes
PostMessageW = ctypes.windll.user32.PostMessageW
SendMessageW = ctypes.windll.user32.SendMessageW
ScreenToClient = ctypes.windll.user32.ScreenToClient

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

#
# Funções auxiliares
#
def to_vk_code(k):
    """
    Converte `k` (pode ser Key.up, Key.alt, ou 'a', 'f', etc.)
    em um Virtual-Key Code do Windows (inteiro).
    """
    if isinstance(k, Key):
        if k not in KEY_MAP:
            raise ValueError(f"Tecla especial {k} não mapeada em KEY_MAP.")
        return KEY_MAP[k]
    elif isinstance(k, str):
        # Converte para maiúsculo e pega o ord
        # Ex.: 'a' -> 'A' -> 65
        c = k.upper()
        return ord(c)
    else:
        raise ValueError(f"Tipo de tecla não suportado: {k}")

def post_keydown(hwnd, vk_code):
    PostMessageW(hwnd, WM_KEYDOWN, vk_code, 0)

def post_keyup(hwnd, vk_code):
    PostMessageW(hwnd, WM_KEYUP, vk_code, 0)

def post_mouse_move(hwnd, x_client, y_client):
    """
    Envia WM_MOUSEMOVE para (x_client, y_client) (coords de cliente).
    lParam = (y << 16) | x
    """
    lparam = (y_client << 16) | (x_client & 0xFFFF)
    PostMessageW(hwnd, WM_MOUSEMOVE, 0, lparam)

def post_left_click(hwnd, x_client, y_client):
    """
    Clique ESQUERDO em coords de cliente (x_client, y_client).
    """
    lparam = (y_client << 16) | (x_client & 0xFFFF)
    # Mover mouse
    PostMessageW(hwnd, WM_MOUSEMOVE, 0, lparam)
    # Botão down
    PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
    # Botão up
    PostMessageW(hwnd, WM_LBUTTONUP, 0, lparam)

def post_right_click(hwnd, x_client, y_client):
    """
    Clique DIREITO em coords de cliente (x_client, y_client).
    """
    lparam = (y_client << 16) | (x_client & 0xFFFF)
    # Mover mouse
    PostMessageW(hwnd, WM_MOUSEMOVE, 0, lparam)
    # Botão down
    PostMessageW(hwnd, WM_RBUTTONDOWN, MK_RBUTTON, lparam)
    # Botão up
    PostMessageW(hwnd, WM_RBUTTONUP, 0, lparam)

def screen_to_client(hwnd, x_screen, y_screen):
    """
    Converte coords de tela (x_screen, y_screen) em coords de cliente (retorna (x_client, y_client)).
    """
    pt = POINT()
    pt.x = x_screen
    pt.y = y_screen
    ScreenToClient(hwnd, ctypes.byref(pt))
    return pt.x, pt.y

def post_mouse_scroll(hwnd, dx=0, dy=0):
    """
    Envia uma rolagem de mouse (vertical/horizontal) em segundo plano.
    - Se dy != 0, usamos WM_MOUSEWHEEL (vertical).
    - Se dx != 0, usamos WM_MOUSEHWHEEL (horizontal).

    A magnitude do scroll = WHEEL_DELTA * “quantidade de ticks”.
    Ex.: dy=2 => 2 ticks => 2*120 = 240
    """
    # Normalmente, a pos do mouse (x,y) não importa tanto para scroll.
    # Mas podemos colocar (0,0) no lParam ou a posição atual do cursor no cliente.
    x_client = 0
    y_client = 0
    lparam = (y_client << 16) | (x_client & 0xFFFF)

    if dy != 0:
        # Vertical scroll
        # wParam: HIWORD = “quantidade de ticks * 120”, LOWORD = MK_CONTROL etc. (se tiver)
        scroll_amount = int(dy * WHEEL_DELTA)
        PostMessageW(hwnd, WM_MOUSEWHEEL, (scroll_amount << 16), lparam)

    if dx != 0:
        # Horizontal scroll
        scroll_amount = int(dx * WHEEL_DELTA)
        PostMessageW(hwnd, WM_MOUSEHWHEEL, (scroll_amount << 16), lparam)

#
# Classe principal
#
class KeyboardControllerWindow:
    def __init__(self, hwnd,x_client=0, y_client = 0):
        self.hwnd = hwnd
        self.x_client = x_client
        self.y_client = y_client
        # Mapeamos todos os movimentos da forma que você mencionou anteriormente
        # Adicionando suporte a type:'scroll', type:'click', etc.
        self.movements = {
            'UP': [Key.up],
            'DOWN': [Key.down],
            'LEFT': [Key.left],
            'RIGHT': [Key.right],
            'DIAGONAL_CIMA_DIREITA': [Key.up, Key.right],
            'DIAGONAL_CIMA_ESQUERDA': [Key.up, Key.left],
            'DIAGONAL_BAIXO_DIREITA': [Key.down, Key.right],
            'DIAGONAL_BAIXO_ESQUERDA': [Key.down, Key.left],
            
            'CLICKA': ['m'],
            'CLICKB': [Key.alt, 'f'],

            # Exemplo: scroll vertical ou horizontal
            'CLICKX': {'type': 'scroll', 'dx': 0, 'dy': 2},
            'CLICKSTART': ['-'],
            'CLICKBACK': ['='],
            'CLICKGUIDE': ['1'],
            'CLICKRSHOULDER': ['1'],
            'CLICKLSHOULDER': ['1'],

            'SCROLL_UP':    {'type': 'scroll', 'dx': 0,  'dy':  2},
            'SCROLL_DOWN':  {'type': 'scroll', 'dx': 0,  'dy': -2},
            'SCROLL_RIGHT': {'type': 'scroll', 'dx': 2,  'dy':  0},
            'SCROLL_LEFT':  {'type': 'scroll', 'dx': -2, 'dy':  0},

            # Clique com pynput.mouse.Button (ex.: Button.left) => adaptado abaixo
            'CLICKY': {'type': 'click', 'button': 'left',  'count': 1},
            'MOUSE_CLICK_LEFT':  {'type': 'click', 'button': 'left',  'count': 1},
            'MOUSE_DBLCLICK_LEFT': {'type': 'click', 'button': 'left', 'count': 2},
            'MOUSE_CLICK_RIGHT': {'type': 'click', 'button': 'right', 'count': 1},
        }

    def get_movements(self):
        return self.movements

    def press_and_release(self, movement, delay_ini=0.5, delay_end=None):
        """
        Executa um movimento que pode ser:
          - Lista de teclas [Key.up, Key.right]
          - String única ['a']
          - Dict com 'type':'scroll', dx,dy
          - Dict com 'type':'click', button, count
        """
        if movement in self.get_movements():
            movement = self.get_movements()[movement]

        # 1) Se for dicionário, tratamos scroll/click
        if isinstance(movement, dict):
            mtype = movement.get('type', '')
            if mtype == 'scroll':
                dx = movement.get('dx', 0)
                dy = movement.get('dy', 0)
                post_mouse_scroll(self.hwnd, dx=dx, dy=dy)

                if delay_ini:
                    time.sleep(delay_ini)
                if delay_end:
                    time.sleep(delay_end)
                return

            elif mtype == 'click':
                button = movement.get('button', 'left')  # 'left' ou 'right'
                count = movement.get('count', 1)
                # Simulamos clique (x=0,y=0) ou ??? -> Precisamos de coords?
                # Se quiser clique em (0,0) no cliente, faça:
                x_client, y_client = self.x_client, self.y_client  # ou a pos que desejar
                for _ in range(count):
                    if button == 'left':
                        post_left_click(self.hwnd, x_client, y_client)
                    elif button == 'right':
                        post_right_click(self.hwnd, x_client, y_client)
                    # Adicione middle se quiser

                    # Se for double-click, normalmente faz 2 loops
                    time.sleep(0.05)

                if delay_ini:
                    time.sleep(delay_ini)
                if delay_end:
                    time.sleep(delay_end)
                return

            else:
                print(f"[KeyboardControllerWindow] Tipo de movimento '{mtype}' não reconhecido.")
                return

        # 2) Se não for dict, assumimos que é teclado
        if isinstance(movement, list):
            # Pressiona todas
            for k in movement:
                vk_code = to_vk_code(k)
                post_keydown(self.hwnd, vk_code)

            if delay_ini:
                time.sleep(delay_ini)

            # Solta em ordem inversa
            for k in reversed(movement):
                vk_code = to_vk_code(k)
                post_keyup(self.hwnd, vk_code)

        else:
            # String única
            vk_code = to_vk_code(movement)
            post_keydown(self.hwnd, vk_code)
            if delay_ini:
                time.sleep(delay_ini)
            post_keyup(self.hwnd, vk_code)

        if delay_end:
            time.sleep(delay_end)
