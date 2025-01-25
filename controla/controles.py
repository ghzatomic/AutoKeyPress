import random
import time
import vgamepad as vg
from inputs import get_gamepad
import keyboard

gamepad = vg.VX360Gamepad()
# Movimentos possíveis com suas direções relativas
movements = {
    'UP': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    'DOWN': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    'LEFT': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    'RIGHT': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    'DIAGONAL_CIMA_DIREITA': [vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT],
    'DIAGONAL_CIMA_ESQUERDA': [vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT],
    'DIAGONAL_BAIXO_ESQUERDA': [vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT],
    'DIAGONAL_BAIXO_DIREITA': [vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT],
    'CLICK': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    'CLICKA': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    'CLICKX': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    'CLICKY': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y
}

BUTTON_MAPPING = {
    "ABS_HAT0Y": {1: 0x0002, -1: 0x0001, 0: None},  # DPAD_DOWN, DPAD_UP, liberar
    "ABS_HAT0X": {1: 0x0008, -1: 0x0004, 0: None},  # DPAD_RIGHT, DPAD_LEFT, liberar
    "BTN_SOUTH": {1: 0x1000, 0: None},  # A, liberar
    "BTN_EAST": {1: 0x2000, 0: None},   # B, liberar
    "BTN_NORTH": {1: 0x4000, 0: None},  # X, liberar
    "BTN_WEST": {1: 0x8000, 0: None}    # Y, liberar
}

def random_sleep(min_seconds, max_seconds):
    """
    Faz um sleep com uma duração aleatória entre min_seconds e max_seconds.

    Args:
        min_seconds (float): Duração mínima do intervalo em segundos.
        max_seconds (float): Duração máxima do intervalo em segundos.
    """
    duration = random.uniform(min_seconds, max_seconds)
    print(f"Dormindo por {duration:.2f} segundos...")
    time.sleep(duration)

def clica_loot(qtde=1,delay_ini=0.2):
    for i in range(qtde):
        # Simula o movimento no gamepad
        pressiona_botao(movements["CLICK"],delay_ini=delay_ini)

def pressiona_solta(btn,delay=0.3):
    pressiona_botao(btn,delay_end=delay)

def pressiona_botao(movimento, delay_ini=1, delay_end=None):
    # Simula o movimento no gamepad
    if isinstance(movimento, list):
        for m in movimento:
            gamepad.press_button(m)
            gamepad.update()
    else:
        gamepad.press_button(movimento)
        gamepad.update()
    if delay_ini:
        time.sleep(delay_ini)
    
    if isinstance(movimento, list):
        for m in movimento:
            gamepad.release_button(m)
            gamepad.update()
    else:
        gamepad.release_button(movimento)
        gamepad.update()
    if delay_end:
        time.sleep(delay_end)

def perform_random_movements_with_breaks(
    num_movements=50, 
    delay=0.4, 
    pause_duration=60, 
    pause_interval=10,
    move_keys = ['UP', 'RIGHT', 'DOWN', 'LEFT'],
    func_beteen_moves=None
):
    """
    Realiza movimentos aleatórios e faz pausas periódicas para atrair e lidar com inimigos.

    Args:
        num_movements (int): Número total de movimentos antes de encerrar.
        delay (float): Tempo de espera entre os movimentos, em segundos.
        pause_duration (int): Duração de cada pausa, em segundos.
        pause_interval (int): Número de movimentos antes de uma pausa.
    """
    movements_done = 0  # Contador de movimentos realizados

    print("Iniciando movimentos aleatórios com pausas...")

    while movements_done < num_movements:
        # Escolhe um movimento aleatório
        move = random.choice(list(move_keys))
        movements_done += 1

        pressiona_botao(movements[move],delay_ini=delay)

        # Faz uma pausa a cada `pause_interval` movimentos
        if movements_done % pause_interval == 0:
            print(f"Pausa para atrair inimigos por {pause_duration} segundos...")
            time.sleep(pause_duration)
        if func_beteen_moves:
            func_beteen_moves()

    print("Movimentos completos com pausas.")


def perform_random_movements(num_movements=5, delay=0.1, performBack=False):
    """
    Realiza movimentos aleatórios e retorna ao ponto inicial.
    
    Args:
        num_movements (int): Quantidade de movimentos aleatórios a executar.
        delay (float): Tempo de espera entre as ações, em segundos.
    """
    position = {'x': 0, 'y': 0}  # Posição inicial
    move_sequence = []  # Sequência de movimentos realizados

    print("Iniciando movimentos aleatórios...")

    for _ in range(num_movements):
        move = random.choice(list(movements.keys()))
        move_sequence.append(move)

        # Atualiza a posição
        if move == 'UP':
            position['y'] += 1
        elif move == 'DOWN':
            position['y'] -= 1
        elif move == 'LEFT':
            position['x'] -= 1
        elif move == 'RIGHT':
            position['x'] += 1

        pressiona_botao(movements[move],delay_ini=delay,delay_end=delay)

        print(f"Botão '{move}' liberado!")
        if (delay):
            time.sleep(delay)
    if (performBack):
        print("\nRetornando ao ponto inicial...")
        while position['x'] != 0 or position['y'] != 0:
            if position['x'] > 0:
                move = 'LEFT'
                position['x'] -= 1
            elif position['x'] < 0:
                move = 'RIGHT'
                position['x'] += 1
            elif position['y'] > 0:
                move = 'DOWN'
                position['y'] -= 1
            elif position['y'] < 0:
                move = 'UP'
                position['y'] += 1
                
            pressiona_botao(movements[move],delay_ini=delay)

        print("Finalizado! De volta ao ponto inicial.")


def perform_square_movements(duration=1, delay=0.1):
    """
    Realiza movimentos em formato de quadrado por uma duração especificada.
    
    Args:
        duration (float): Duração total para os movimentos, em segundos.
        delay (float): Tempo de espera entre as ações, em segundos.
    """
    print("Iniciando movimentos em quadrado...")
    start_time = time.time()
    square_sequence = ['UP', 'RIGHT', 'DOWN', 'LEFT','UP']  # Sequência de movimentos

    while time.time() - start_time < duration:
        for move in square_sequence:
            pressiona_botao(movements[move],delay_ini=delay)

    print("Finalizado! Movimentos em quadrado completos.")

def record_movements(output_file="movements.txt"):
    """
    Grava os movimentos do controle físico em um arquivo de texto.
    Registra períodos de inatividade entre ações.
    A gravação pode ser interrompida pressionando ESC.

    Args:
        output_file (str): Nome do arquivo para salvar os movimentos.
    """
    print("Gravando movimentos... Pressione ESC para parar.")
    start_time = time.time()
    last_event_time = start_time  # Rastreamento do último evento

    with open(output_file, "w") as file:
        while not keyboard.is_pressed('esc'):  # Para quando ESC for pressionado
            events = get_gamepad()
            current_time = time.time()

            # Detecta períodos de inatividade
            if current_time - last_event_time > 0.1:  # Mais de 100 ms sem ação
                inactivity_duration = current_time - last_event_time
                file.write(f"INACTIVE,0,{inactivity_duration}\n")
                file.flush()
                last_event_time = current_time  # Atualiza o último evento
                print(f"Registrado inatividade por {inactivity_duration:.2f} segundos.")

            for event in events:
                if event.ev_type in ["Key", "Absolute"]:
                    timestamp = current_time - start_time
                    file.write(f"{event.code},{event.state},{timestamp}\n")
                    file.flush()
                    last_event_time = current_time  # Atualiza o último evento
                    print(f"Gravado: {event.code},{event.state},{timestamp}")

    print(f"Gravação finalizada! Movimentos salvos em {output_file}.")

def replay_movements(input_file="movements.txt", return_to_origin_flag=False):
    """
    Reproduz os movimentos salvos de um arquivo de texto, incluindo períodos de inatividade.
    Pode opcionalmente retornar ao ponto de origem.

    Args:
        input_file (str): Nome do arquivo com os movimentos gravados.
        return_to_origin_flag (bool): Se True, retorna ao ponto inicial após a reprodução.
    """
    print(f"Lendo movimentos de {input_file}...")

    movements_list = []
    with open(input_file, "r") as file:
        for line in file:
            code, state, timestamp = line.strip().split(",")
            movements_list.append((code, int(state), float(timestamp)))

    # Reproduz os movimentos
    start_time = time.time()
    for code, state, timestamp in movements_list:
        # Sincroniza o tempo dos eventos
        while time.time() - start_time < timestamp:
            time.sleep(0.001)

        if code == "INACTIVE":
            print(f"Inatividade por {timestamp:.2f} segundos.")
            time.sleep(timestamp)
        elif code in BUTTON_MAPPING:
            if isinstance(BUTTON_MAPPING[code], dict):  # Mapeamento de eixo
                if state != 0:  # Pressionar
                    button = BUTTON_MAPPING[code].get(state)
                    if button:
                        gamepad.press_button(button)
                        gamepad.update()
                        print(f"Pressionado: {button}")
                else:  # Liberar todos os botões associados ao eixo
                    for btn in BUTTON_MAPPING[code].values():
                        if btn:  # Ignorar valores None
                            gamepad.release_button(btn)
                            gamepad.update()
                            print(f"Liberado: {btn}")
            else:  # Botões simples
                button = BUTTON_MAPPING[code]
                if state != 0:  # Pressionar
                    gamepad.press_button(button)
                    gamepad.update()
                    print(f"Pressionado: {button}")
                else:  # Liberar
                    gamepad.release_button(button)
                    gamepad.update()
                    print(f"Liberado: {button}")
        else:
            print(f"Evento desconhecido: {code}")

    # Retorna ao ponto de origem, se habilitado
    if return_to_origin_flag:
        return_to_origin(movements_list)

    print("Reprodução dos movimentos concluída.")



def return_to_origin(movements_list):
    """
    Retorna ao ponto de origem reproduzindo os movimentos na ordem inversa.

    Args:
        movements_list (list): Lista de movimentos com os eventos capturados.
    """
    print("Retornando ao ponto de origem...")

    # Inverter a lista de movimentos para retornar ao ponto inicial
    for code, state, timestamp in reversed(movements_list):
        # Ignorar inatividade (não afeta a posição)
        if code == "INACTIVE":
            continue

        # Reverter o movimento:
        # - Para eixos: inverter o estado (1 -> -1, -1 -> 1).
        # - Para botões simples, usar o mesmo estado.
        if code in BUTTON_MAPPING:
            if isinstance(BUTTON_MAPPING[code], dict):  # Eixos
                if state != 0:
                    reversed_state = -state  # Inverte o estado (1 -> -1, -1 -> 1)
                    button = BUTTON_MAPPING[code].get(reversed_state)
                else:
                    # Libera todos os botões associados ao eixo
                    for btn in BUTTON_MAPPING[code].values():
                        if btn:  # Ignorar valores None
                            gamepad.release_button(btn)
                            gamepad.update()
                            print(f"Liberado (retorno): {btn}")
                    continue
            else:  # Botões simples
                button = BUTTON_MAPPING[code]

            # Simular a ação no gamepad
            if button:
                if state != 0:  # Pressionar
                    gamepad.press_button(button)
                    gamepad.update()
                    print(f"Pressionado (retorno): {button}")
                else:  # Liberar
                    gamepad.release_button(button)
                    gamepad.update()
                    print(f"Liberado (retorno): {button}")
                time.sleep(0.1)  # Pequena pausa para simular o movimento
            else:
                print(f"Estado desconhecido ou botão não mapeado: {code}")
        else:
            print(f"Evento desconhecido ao retornar: {code}")

    print("Movimentos finalizados. Retornou ao ponto de origem!")


def movimento_eldrich_sobe_desce():
    """
    Realiza movimentos em formato de quadrado por uma duração especificada.
    
    Args:
        duration (float): Duração total para os movimentos, em segundos.
        delay (float): Tempo de espera entre as ações, em segundos.
    """
    print("Iniciando movimentos do eldrich...")
    pressiona_solta(movements["CLICKX"])
    time.sleep(0.5)
    pressiona_solta(movements["DIAGONAL_BAIXO_DIREITA"],delay=0.5)
    pressiona_solta(movements["CLICKY"])
    pressiona_solta(movements["DIAGONAL_CIMA_ESQUERDA"],delay=0.5)
    pressiona_solta(movements["CLICKY"])
    pressiona_solta(movements["DIAGONAL_BAIXO_DIREITA"],delay=0.5)
    pressiona_solta(movements["CLICKY"])
    pressiona_solta(movements["DIAGONAL_CIMA_ESQUERDA"],delay=0.5)
    pressiona_solta(movements["CLICKY"])
    pressiona_solta(movements["DIAGONAL_BAIXO_DIREITA"],delay=1)
    pressiona_solta(movements["CLICKA"])
    time.sleep(0.5)

    print("Finalizado! Movimentos Eldritch.")