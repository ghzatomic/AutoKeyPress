import time
from pynput.keyboard import Controller, Key
from pynput.mouse import Controller as MouseController, Button

class KeyboardController:
    def __init__(self):
        # Cria o controlador de teclado do pynput
        self.keyboard = Controller()
        self.mouse = MouseController()

        # Mapeamento das “teclas”: diagonais serão listas
        # Usamos Key.up, Key.down, Key.left e Key.right para as setas
        # e mantemos as letras como strings ('a','b','x','y', etc.)
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
            'CLICKX': {'type': 'scroll', 'dx': 0,  'dy':  2},
            'CLICKY': {'type': 'click', 'button': Button.left,  'count': 1},
            'CLICKSTART': ['-'],
            'CLICKBACK': ['='],
            'CLICKGUIDE': ['1'],
            'CLICKRSHOULDER': ['1'],
            'CLICKLSHOULDER': ['1'],

            'SCROLL_UP':   {'type': 'scroll', 'dx': 0,  'dy':  2},  # rola para cima
            'SCROLL_DOWN': {'type': 'scroll', 'dx': 0,  'dy': -2},  # rola para baixo
            'SCROLL_RIGHT': {'type': 'scroll', 'dx': 2, 'dy': 0},   # rola para a direita
            'SCROLL_LEFT':  {'type': 'scroll', 'dx': -2,'dy': 0},    # rola para a esquerda
            # Movimentos de CLIQUE
            # Exemplo de clique esquerdo simples
            'MOUSE_CLICK_LEFT':  {'type': 'click', 'button': Button.left,  'count': 1},
            # Se quiser clique duplo esquerdo:
            'MOUSE_DBLCLICK_LEFT': {'type': 'click', 'button': Button.left, 'count': 2},

            # Você poderia adicionar clique direito, se desejar
            'MOUSE_CLICK_RIGHT': {'type': 'click', 'button': Button.right, 'count': 1},
        }

    def get_movements(self):
        """Retorna o dicionário de movimentos disponíveis."""
        return self.movements

    def send_text(self, text, delay=0.05):
        """
        Digita o texto caractere por caractere utilizando o pynput.
        Se o caractere for uma letra maiúscula, utiliza a tecla SHIFT.
        Ao final, envia um ENTER.
        
        :param text: String a ser digitada.
        :param delay: Tempo de delay (em segundos) entre os eventos.
        """
        # Após digitar o texto, envia ENTER
        self.keyboard.press(Key.enter)
        time.sleep(delay)
        self.keyboard.release(Key.enter)
        for char in text:
            # Se for letra maiúscula, pressiona SHIFT junto
            if char.isalpha() and char.isupper():
                self.keyboard.press(Key.shift)
                self.keyboard.press(char.lower())
                time.sleep(0.1)
                self.keyboard.release(char.lower())
                self.keyboard.release(Key.shift)
            else:
                # Para outros caracteres, incluindo letras minúsculas, números e símbolos
                self.keyboard.press(char)
                time.sleep(0.1)
                self.keyboard.release(char)
        
        # Após digitar o texto, envia ENTER
        self.keyboard.press(Key.enter)
        time.sleep(delay)
        self.keyboard.release(Key.enter)

    def press_and_release(self, movement, delay_ini=0.5, delay_end=None):
        """
        Executa um movimento que pode ser:
          - Lista de teclas (ex.: [Key.up, Key.right])
          - String de tecla única (ex.: ['a'])
          - Um dicionário indicando scroll {'type':'scroll','dx':...,'dy':...}
          - Um dicionário indicando clique {'type':'click','button':...,'count':...}

        :param movement: Valor do dicionário self.movements. Pode ser list, str ou dict.
        :param delay_ini: Tempo para "segurar" se for teclado, ou aguardar após ação se for scroll/clique.
        :param delay_end: Tempo para esperar ao final da ação.
        """
        #print(f"Executando o {movement}")
        if movement in self.get_movements():
            movement = self.get_movements()[movement]

        # 1) Verifica se é um dict (scroll ou click)
        if isinstance(movement, dict):
            # Scroll
            if movement.get('type') == 'scroll':
                dx = movement.get('dx', 0)
                dy = movement.get('dy', 0)
                self.mouse.scroll(dx, dy)
                if delay_ini:
                    time.sleep(delay_ini)
                return

            # Clique
            if movement.get('type') == 'click':
                button = movement.get('button', Button.left)  # Padrão: clique esquerdo
                count = movement.get('count', 1)             # Padrão: 1 clique
                self.mouse.click(button, count)
                # Se quiser "segurar" tempo entre cliques (geralmente não se faz), ou esperar
                if delay_ini:
                    time.sleep(delay_ini)
                return

        # 2) Se não for dict, assumimos que é teclado (list ou str)
        if isinstance(movement, list):
            # Pressiona todas as teclas
            if ("MOUSE" in movement):
                button = movement.get('button', Button.left)  # Padrão: clique esquerdo
                count = movement.get('count', 1)             # Padrão: 1 clique
                self.mouse.click(button, count)
                # Se quiser "segurar" tempo entre cliques (geralmente não se faz), ou esperar
                if delay_ini:
                    time.sleep(delay_ini)
            else:

                for k in movement:
                    self.keyboard.press(k)
                # Mantém pressionado por delay_ini
                if delay_ini:
                    time.sleep(delay_ini)
                # Solta todas as teclas em ordem reversa
                for k in reversed(movement):
                    self.keyboard.release(k)
        else:
            # Se for uma string única
            self.keyboard.press(movement)
            if delay_ini:
                time.sleep(delay_ini)
            self.keyboard.release(movement)

        # 3) Aguarda delay_end, se definido
        if delay_end:
            time.sleep(delay_end)