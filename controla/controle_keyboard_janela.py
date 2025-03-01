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
    Key.alt:   0x12,   # VK_MENU
    Key.enter: 0x0D   # VK_RETURN
    # Adicione aqui se precisar (Key.shift, Key.ctrl, Key.esc, etc.)
}

# Carregando funções da user32.dll via ctypes
PostMessageW = ctypes.windll.user32.PostMessageW
SendMessageW = ctypes.windll.user32.SendMessageW
ScreenToClient = ctypes.windll.user32.ScreenToClient

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]


# Definições necessárias
SendInput = ctypes.windll.user32.SendInput

# Estruturas para simulação de entrada
PUL = ctypes.POINTER(ctypes.c_ulong)

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ki", KEYBDINPUT)]
    
def make_lparam(repeat_count, scan_code, extended=False, is_keyup=False):
    # Contagem de repetições nos 16 bits inferiores
    lparam = repeat_count & 0xFFFF
    # Código de varredura nos bits 16-23
    lparam |= (scan_code & 0xFF) << 16
    # Flag de tecla estendida (bit 24)
    if extended:
        lparam |= 1 << 24
    # Para key up, definir os bits 30 e 31
    if is_keyup:
        lparam |= 1 << 30  # Previous key state
        lparam |= 1 << 31  # Transition state
    return lparam



def send_ctrl_c(hwnd):
    VK_CONTROL = 0x11  # Tecla Ctrl
    VK_C       = 0x43  # Letra 'C'
    # Para a tecla Ctrl, o scan code normalmente é 0x1D (esquerdo Ctrl)
    lparam_ctrl_down = make_lparam(repeat_count=1, scan_code=0x1D, extended=False, is_keyup=False)
    lparam_ctrl_up   = make_lparam(repeat_count=1, scan_code=0x1D, extended=False, is_keyup=True)

    # Para a tecla 'C', o scan code geralmente é 0x2E
    lparam_c_down = make_lparam(repeat_count=1, scan_code=0x2E, extended=False, is_keyup=False)
    lparam_c_up   = make_lparam(repeat_count=1, scan_code=0x2E, extended=False, is_keyup=True)

    # Envia os eventos: CTRL down -> C down -> C up -> CTRL up
    ctypes.windll.user32.PostMessageW(hwnd, WM_KEYDOWN, VK_CONTROL, lparam_ctrl_down)
    time.sleep(0.01)
    ctypes.windll.user32.PostMessageW(hwnd, WM_KEYDOWN, VK_C, lparam_c_down)
    time.sleep(0.01)
    ctypes.windll.user32.PostMessageW(hwnd, WM_KEYUP, VK_C, lparam_c_up)
    time.sleep(0.01)
    ctypes.windll.user32.PostMessageW(hwnd, WM_KEYUP, VK_CONTROL, lparam_ctrl_up)

def send_maior(hwnd):
    VK_SHIFT = 0xA1         # Tecla SHIFT (esquerdo)
    VK_OEM_PERIOD = 0xBE    # Tecla de ponto (.)
    
    # Scan codes (valores comuns para layout americano)
    SCAN_SHIFT = 0x2A       # Scan code para SHIFT esquerdo
    SCAN_PERIOD = 0x34      # Scan code para a tecla de ponto
    
    # Monta os lParam para cada evento
    lparam_shift_down  = make_lparam(1, SCAN_SHIFT, extended=False, is_keyup=False)
    lparam_shift_up    = make_lparam(1, SCAN_SHIFT, extended=False, is_keyup=True)
    lparam_period_down = make_lparam(1, SCAN_PERIOD, extended=False, is_keyup=False)
    lparam_period_up   = make_lparam(1, SCAN_PERIOD, extended=False, is_keyup=True)
    
    # Envia a sequência: SHIFT down -> '.' down -> '.' up -> SHIFT up
    ctypes.windll.user32.PostMessageW(hwnd, WM_KEYDOWN, VK_SHIFT, lparam_shift_down)
    time.sleep(0.01)
    ctypes.windll.user32.PostMessageW(hwnd, WM_KEYDOWN, VK_OEM_PERIOD, lparam_period_down)
    time.sleep(0.01)
    ctypes.windll.user32.PostMessageW(hwnd, WM_KEYUP, VK_OEM_PERIOD, lparam_period_up)
    time.sleep(0.01)
    ctypes.windll.user32.PostMessageW(hwnd, WM_KEYUP, VK_SHIFT, lparam_shift_up)

def send_enter_input():
    VK_RETURN = 0x0D
    INPUT_KEYBOARD = 1
    KEYEVENTF_KEYUP = 0x0002

    # Cria dois INPUTs: um para key down e outro para key up
    key_down = INPUT(type=INPUT_KEYBOARD,
                     ki=KEYBDINPUT(wVk=VK_RETURN,
                                   wScan=0,
                                   dwFlags=0,
                                   time=0,
                                   dwExtraInfo=ctypes.pointer(ctypes.c_ulong(0))))
    key_up = INPUT(type=INPUT_KEYBOARD,
                   ki=KEYBDINPUT(wVk=VK_RETURN,
                                 wScan=0,
                                 dwFlags=KEYEVENTF_KEYUP,
                                 time=0,
                                 dwExtraInfo=ctypes.pointer(ctypes.c_ulong(0))))
    
    inputs = (key_down, key_up)
    nInputs = len(inputs)
    LPINPUT = INPUT * nInputs
    pInputs = LPINPUT(*inputs)
    SendInput(nInputs, pInputs, ctypes.sizeof(INPUT))

#
# Funções auxiliares
#
def to_vk_code(k):
    """
    Converte `k` (pode ser Key.up, Key.alt, ou 'a', 'f', etc.)
    em um Virtual-Key Code do Windows (inteiro).
    """
    # Caso especial para o ponto, que já pode estar envolvido no '>'
    if k == '.':
        return 0xBE  # VK_OEM_PERIOD
    
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
        self.normal_moves = ['UP','DOWN','LEFT','RIGHT','DIAGONAL_CIMA_DIREITA','DIAGONAL_CIMA_ESQUERDA','DIAGONAL_BAIXO_DIREITA',"DIAGONAL_BAIXO_ESQUERDA"]
        self.movements = {
            'UP': [Key.up],
            'DOWN': [Key.down],
            'LEFT': [Key.left],
            'RIGHT': [Key.right],
            'ENTER': [Key.enter],
            'DIAGONAL_CIMA_DIREITA': [Key.up, Key.right],
            'DIAGONAL_CIMA_ESQUERDA': [Key.up, Key.left],
            'DIAGONAL_BAIXO_DIREITA': [Key.down, Key.right],
            'DIAGONAL_BAIXO_ESQUERDA': [Key.down, Key.left],
            
            'CLICKA': ['m'],
            'CLICKB': [Key.ctrl, 'c'],

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

    def send_key_sequence(self, keys, delay=0.01):
        """
        Envia uma sequência de teclas para a janela (self.hwnd) usando PostMessageW.
        Primeiro, envia todas as mensagens WM_KEYDOWN e depois WM_KEYUP em ordem inversa.
        
        :param keys: Lista de teclas (string ou Key) a serem enviadas.
        :param delay: Delay entre os eventos (em segundos).
        """
        # Envia WM_KEYDOWN para cada tecla na ordem da lista
        for key in keys:
            vk, scan = self.get_vk_scan(key)
            lparam_down = make_lparam(1, scan, extended=False, is_keyup=False)
            ctypes.windll.user32.PostMessageW(self.hwnd, WM_KEYDOWN, vk, lparam_down)
            time.sleep(delay)
        # Em seguida, envia WM_KEYUP em ordem inversa
        for key in reversed(keys):
            vk, scan = self.get_vk_scan(key)
            lparam_up = make_lparam(1, scan, extended=False, is_keyup=True)
            ctypes.windll.user32.PostMessageW(self.hwnd, WM_KEYUP, vk, lparam_up)
            time.sleep(delay)

    def get_vk_scan(self, key):
        """
        Converte uma tecla (string de 1 caractere ou Key do pynput) para (vk_code, scan_code).
        Para caracteres, usa MapVirtualKeyW; para teclas especiais, utiliza um mapeamento fixo.
        """
        if isinstance(key, str) and len(key) == 1:
            # Converte para maiúsculo para padronizar
            vk = ord(key.upper())
            # Usa MapVirtualKeyW para obter o scan code (o 2º parâmetro 0 indica conversão de VK para scan code)
            scan = ctypes.windll.user32.MapVirtualKeyW(vk, 0)
            return vk, scan
        elif isinstance(key, Key):
            KEY_MAP = {
                Key.enter: (0x0D, 0x1C),
                Key.shift: (0xA0, 0x2A),
                Key.alt:   (0x12, 0x38),
                Key.ctrl:  (0x11, 0x1D),
                Key.up:    (0x26, 0x48),
                Key.down:  (0x28, 0x50),
                Key.left:  (0x25, 0x4B),
                Key.right: (0x27, 0x4D),
                # Adicione outros mapeamentos se necessário
            }
            if key in KEY_MAP:
                return KEY_MAP[key]
            else:
                raise ValueError(f"Tecla especial não mapeada: {key}")
        else:
            raise ValueError(f"Tipo de tecla não suportado: {key}")

    def get_movements(self):
        return self.movements
    
    def send_enter(self):
        """
        Envia o comando ENTER para a janela alvo (self.hwnd) utilizando PostMessageW.
        """
        VK_RETURN = 0x0D    # Virtual-Key code para ENTER
        SCAN_ENTER = 0x1C   # Scan code geralmente utilizado para ENTER

        # Monta lParam para WM_KEYDOWN e WM_KEYUP
        lparam_down = make_lparam(repeat_count=1, scan_code=SCAN_ENTER, extended=False, is_keyup=False)
        lparam_up   = make_lparam(repeat_count=1, scan_code=SCAN_ENTER, extended=False, is_keyup=True)

        # Envia as mensagens: ENTER pressionado e solto
        ctypes.windll.user32.PostMessageW(self.hwnd, WM_KEYDOWN, VK_RETURN, lparam_down)
        time.sleep(0.01)
        ctypes.windll.user32.PostMessageW(self.hwnd, WM_KEYUP, VK_RETURN, lparam_up)

    def send_shift(self):
        """
        Envia o comando SHIFT para a janela alvo (self.hwnd) utilizando PostMessageW.
        Simula o pressionamento e a liberação da tecla SHIFT.
        """
        VK_SHIFT = 0xA0       # Virtual-Key code para SHIFT esquerdo
        SCAN_SHIFT = 0x2A     # Scan code comum para SHIFT esquerdo
        
        # Monta os lParam para SHIFT down e SHIFT up
        lparam_down = make_lparam(repeat_count=1, scan_code=SCAN_SHIFT, extended=False, is_keyup=False)
        lparam_up   = make_lparam(repeat_count=1, scan_code=SCAN_SHIFT, extended=False, is_keyup=True)
        
        # Envia a mensagem: SHIFT pressionado
        ctypes.windll.user32.PostMessageW(self.hwnd, WM_KEYDOWN, VK_SHIFT, lparam_down)
        time.sleep(0.5)
        post_keydown(self.hwnd, 0xBE)
        # Envia a mensagem: SHIFT liberado
        ctypes.windll.user32.PostMessageW(self.hwnd, WM_KEYUP, VK_SHIFT, lparam_up)

    def send_text(self, text, delay=0.05):
        """
        Envia o texto caractere por caractere para a janela alvo (self.hwnd) via PostMessageW.
        Caso o caractere seja '>', simula a combinação SHIFT + ponto.
        
        :param text: string a ser digitada.
        :param delay: intervalo em segundos entre os eventos.
        """
        # Opcional: Envia ENTER antes do texto, se desejado
        self.send_enter()

        for char in text:
            # Se o caractere for '>', envia SHIFT + ponto
            if char == '>':
                send_maior(self.hwnd)
            else:
                # Para outros caracteres, converte usando uma função auxiliar (exemplo: to_vk_code)
                vk_code = to_vk_code(char)
                # Para simplificar, usamos lParam 0; porém, para teclas especiais pode ser necessário montá-lo corretamente
                ctypes.windll.user32.PostMessageW(self.hwnd, WM_KEYDOWN, vk_code, 0)
                time.sleep(delay)
                #ctypes.windll.user32.PostMessageW(self.hwnd, WM_KEYUP, vk_code, 0)
        self.send_enter()


    def press_and_release(self, movement, delay_ini=0.5, delay_end=None):
        """
        Executa um movimento que pode ser:
          - Lista de teclas [Key.up, Key.right]
          - String única ['a']
          - Dict com 'type':'scroll', dx,dy
          - Dict com 'type':'click', button, count
        """
        strmove = movement
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
            if (strmove in self.normal_moves):
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
                self.send_key_sequence(movement, 0.1)
        else:
            # String única
            if (strmove in self.normal_moves):
                vk_code = to_vk_code(movement)
                post_keydown(self.hwnd, vk_code)
                if delay_ini:
                    time.sleep(delay_ini)
                post_keyup(self.hwnd, vk_code)
            else:
                self.send_key_sequence([movement], delay_ini)
                
            
            

        if delay_end:
            time.sleep(delay_end)
