import random
import time
import os
import vgamepad as vg
from inputs import get_gamepad
import keyboard
import json
from datetime import datetime
from controla.controle_gamepad import GamepadController
from controla.controle_keyboard import KeyboardController
pause_flag = False

def on_esc_key(event):
    """
    Callback chamada toda vez que a tecla 'esc' for pressionada.
    Define a flag de pausa.
    """
    global pause_flag
    pause_flag = True
    print("Tecla ESC pressionada! Sinalizando pausa...")

# Registra o callback para a tecla "esc"
keyboard.on_press_key("esc", on_esc_key)

controlador = KeyboardController()

def move_randomly_to_unstuck(failed_moves):
    """
    Realiza um movimento aleatório para tentar destravar o personagem.
    Evita movimentos já tentados anteriormente.

    Args:
        failed_moves (set): Conjunto de movimentos que já falharam.
    """
    available_moves = [m for m in controlador.get_movements().keys() if m not in failed_moves]

    if not available_moves:
        print("Nenhum movimento disponível para destravar! Resetando tentativas...")
        failed_moves.clear()
        available_moves = list(controlador.get_movements().keys())

    move_name = random.choice(available_moves)
    print(f"Tentando destravar com o movimento: {move_name}")
    controlador.press_and_release(controlador.get_movements()[move_name], delay_ini=0.5)


def move_away_from_wall(failed_moves):
    """
    Quando o personagem fica preso entre dois obstáculos laterais e uma parede,
    ele tenta se mover para cima ou diagonalmente para sair do canto.
    """
    escape_moves = ["UP", "DIAGONAL_CIMA_ESQUERDA", "DIAGONAL_CIMA_DIREITA", "DIAGONAL_BAIXO_DIREITA","DIAGONAL_BAIXO_ESQUERDA","DOWN","LEFT","RIGHT"]
    
    # Remove movimentos que já falharam para não repetir erros
    available_moves = [m for m in escape_moves if m not in failed_moves]

    if not available_moves:
        print("⚠ Nenhuma opção de saída disponível! Resetando tentativas...")
        failed_moves.clear()
        available_moves = escape_moves  # Tenta novamente com todas as opções

    move_name = random.choice(available_moves)
    print(f"🚀 Tentando escapar com: {move_name}")
    controlador.press_and_release(controlador.get_movements()[move_name], delay_ini=random.uniform(0.5, 1))

import random

def move_away_from_wall_long(failed_moves):
    """
    Quando o personagem fica preso, ele tenta se mover longamente em direções opostas ao destino.
    Se não funcionar, tenta uma direção alternativa.
    
    Args:
        failed_moves (set): Conjunto de movimentos que já falharam.
    """
    escape_moves = [
        ("UP", -1, -3), 
        ("DOWN", 1, 3), 
        ("LEFT", -3, 1), 
        ("RIGHT", 3, -1)
    ]

    # Remove movimentos já falhados
    available_moves = [m for m in escape_moves if m[0] not in failed_moves]

    if not available_moves:
        print("⚠ Nenhuma opção de escape disponível! Resetando tentativas...")
        failed_moves.clear()
        available_moves = escape_moves  # Tenta novamente com todas as opções

    move_name, dx, dy = random.choice(available_moves)
    
    print(f"🚀 Tentando escapar com movimento longo: {move_name}")
    for _ in range(random.randint(3, 15)):  
        controlador.press_and_release(controlador.get_movements()[move_name], delay_ini=0.2)


def move_to_target_smart_v2(uo_assist, target_x, target_y, step_delay_fn,
                            tolerance=2,
                            stuck_threshold=5,   # Quantas posições no histórico para detectar "travado"
                            on_move_callback=None,
                            on_stuck_callback=None,
                            max_attempts=5,
                            max_dist_xy=50):
    """
    Move o personagem até (target_x, target_y) com tolerância e detecção de bloqueios.
    - 'stuck_threshold': quantas posições consecutivas iguais antes de considerar "preso".
    - 'max_attempts': se ficar 'n' tentativas sem avançar, também é considerado "preso".
    - 'max_dist_xy': distância máxima (em X ou Y) em relação ao destino; se exceder, o passo é ignorado,
      e também se for maior que isso, não consideramos que o personagem esteja "preso".
    """

    global pause_flag
    pause_flag = False  # Reseta a flag de pausa ao iniciar

    # Verifica se conseguiu anexar ao UOAssist
    if not uo_assist.attach_to_assistant():
        print("Erro: Não foi possível anexar ao UOAssist.")
        return
    
    coords = uo_assist.get_character_coords()
    if not coords:
        print("Erro: Não foi possível obter as coordenadas iniciais.")
        return
    
    current_x, current_y = coords
    print(f"Posição inicial: X={current_x}, Y={current_y}")
    print(f"Movendo para: X={target_x}, Y={target_y} (tolerância = {tolerance}).")
    print(f"Detectando travamento caso {stuck_threshold} leituras sejam iguais ou {max_attempts} tentativas sem progresso.")
    print(f"Usando max_dist_xy = {max_dist_xy} para ignorar passos e travamentos se estiver muito longe.")

    # Histórico das últimas posições para detectar se está "parado" no mesmo lugar
    last_positions = []
    # Contador de tentativas sem progresso
    no_progress_count = 0
    # Movimentos que falharam recentemente
    failed_moves = set()

    # Direções ajustadas para passos consistentes (menos "pulinhos")
    directions = [
        ("DIAGONAL_BAIXO_DIREITA", 1, 1),
        ("DIAGONAL_BAIXO_ESQUERDA", -1, 1),
        ("DIAGONAL_CIMA_DIREITA", 1, -1),
        ("DIAGONAL_CIMA_ESQUERDA", -1, -1),
        ("RIGHT", 1, 0),
        ("LEFT", -1, 0),
        ("DOWN", 0, 1),
        ("UP", 0, -1)
    ]

    # Loop principal: continua enquanto estiver fora da "tolerância" do destino
    while abs(current_x - target_x) > tolerance or abs(current_y - target_y) > tolerance:
        # Sempre atualiza a posição
        coords = uo_assist.get_character_coords()
        if not coords:
            print("Erro: Não foi possível obter a posição atual.")
            return
        updated_x, updated_y = coords

        # Se a flag de pausa estiver marcada, pausar 40s
        if pause_flag:
            print("Pausando por 40 segundos...")
            time.sleep(40)
            pause_flag = False

        # Adiciona a posição atual ao histórico
        last_positions.append((updated_x, updated_y))
        if len(last_positions) > stuck_threshold:
            last_positions.pop(0)  # Mantém só as últimas 'stuck_threshold'

        # Atualiza current_x, current_y
        current_x, current_y = updated_x, updated_y

        # ----------------------------------------------------------------------------------
        # 1) Aqui é onde checamos travamento:
        #    Só consideramos "preso" se estivermos dentro do max_dist_xy do destino.
        # ----------------------------------------------------------------------------------
        dist_x = abs(current_x - target_x)
        dist_y = abs(current_y - target_y)
        is_near_enough = (dist_x <= max_dist_xy and dist_y <= max_dist_xy)

        # Se estiver perto o suficiente, então fazer detecção de "preso"
        if is_near_enough:
            # --- DETECÇÃO 1: Mesmo ponto por 'stuck_threshold' leituras ---
            if len(last_positions) == stuck_threshold and len(set(last_positions)) == 1:
                print(f"🚨 Personagem preso na posição {last_positions[0]} (repetido {stuck_threshold} vezes). Tentando escapar...")
                # Chama callback ou movimentação de desbloqueio
                if on_stuck_callback:
                    on_stuck_callback(current_x, current_y, failed_moves)
                else:
                    move_away_from_wall(failed_moves)  # Implemente a seu critério

                last_positions.clear()
                no_progress_count = 0
                failed_moves.clear()
                continue

            # --- DETECÇÃO 2: Várias tentativas sem progresso ---
            if len(last_positions) >= 2 and last_positions[-1] == last_positions[-2]:
                no_progress_count += 1
            else:
                no_progress_count = 0

            if no_progress_count >= max_attempts:
                print(f"⚠ O personagem não está avançando na posição ({current_x}, {current_y}). Tentando desbloquear...")
                if on_stuck_callback:
                    on_stuck_callback(current_x, current_y, failed_moves)
                else:
                    move_away_from_wall(failed_moves)

                last_positions.clear()
                no_progress_count = 0
                failed_moves.clear()
                continue
        else:
            # Se estamos longe demais, não tratamos como "preso",
            # mas ainda podemos contar se estamos sem progresso, se você quiser
            # Caso queira IGNORAR completamente, pode comentar essa parte.
            if len(last_positions) >= 2 and last_positions[-1] == last_positions[-2]:
                no_progress_count += 1
            else:
                no_progress_count = 0

        # ----------------------------------------------------------------------------------
        # 2) Tenta mover em direção ao alvo, priorizando direções que aproximam mais
        # ----------------------------------------------------------------------------------
        directions.sort(key=lambda d: abs((current_x + d[1]) - target_x) + abs((current_y + d[2]) - target_y))

        moved = False
        for move_name, dx, dy in directions:
            new_x = current_x + dx
            new_y = current_y + dy

            # Se a distância em X ou Y excede max_dist_xy, pula este movimento
            if abs(new_x - target_x) > max_dist_xy or abs(new_y - target_y) > max_dist_xy:
                continue

            # Evita tentativas que falharam
            if (new_x, new_y) in failed_moves:
                continue

            # Verifica se pausou
            if pause_flag:
                print("Pausando por 40 segundos...")
                time.sleep(40)
                pause_flag = False

            controlador.press_and_release(controlador.get_movements()[move_name], delay_ini=step_delay_fn())

            coords = uo_assist.get_character_coords()
            if not coords:
                print("Erro ao atualizar posição.")
                return
            updated_x, updated_y = coords

            if (updated_x, updated_y) != (current_x, current_y):
                moved = True
                current_x, current_y = updated_x, updated_y
                break
            else:
                # Se não se mexeu, marca esse movimento como falho
                failed_moves.add((new_x, new_y))

        # Se nenhuma direção funcionou, "moved" continua False
        # Você pode inserir alguma lógica extra, caso precise

    # Se chegou até aqui, está dentro da tolerância
    if on_move_callback:
        on_move_callback()

    print(f"🏁 Destino alcançado! Posição final: X={current_x}, Y={current_y} (tolerância = {tolerance})")


def move_to_target_smart(uo_assist, target_x, target_y, step_delay_fn,
                         tolerance=2,
                         stuck_threshold=5,   # Quantas posições no histórico para detectar "travado"
                         on_move_callback=None,
                         on_stuck_callback=None,
                         max_attempts=5,
                         max_dist_xy=50):
    """
    Move o personagem até (target_x, target_y) com tolerância e detecção de bloqueios.
    - 'stuck_threshold': quantas posições consecutivas iguais antes de considerar "preso".
    - 'max_attempts': se ficar 'n' tentativas sem avançar, também é considerado "preso".
    - 'max_dist_xy': distância máxima em X ou Y em relação ao destino. Movimentos fora disso serão ignorados,
      e o sistema de 'preso' também não é disparado quando o personagem ainda está longe (maior que max_dist_xy).
    """

    global pause_flag
    pause_flag = False  # Reseta a flag de pausa ao iniciar

    # Verifica se conseguiu anexar ao UOAssist
    if not uo_assist.attach_to_assistant():
        print("Erro: Não foi possível anexar ao UOAssist.")
        return
    
    coords = uo_assist.get_character_coords()
    if not coords:
        print("Erro: Não foi possível obter as coordenadas iniciais.")
        return
    
    current_x, current_y = coords
    print(f"Posição inicial: X={current_x}, Y={current_y}")
    print(f"Movendo para: X={target_x}, Y={target_y} (tolerância={tolerance}).")
    print(f"Detectando travamento caso {stuck_threshold} leituras sejam iguais ou {max_attempts} tentativas sem progresso.")
    print(f"Usando max_dist_xy={max_dist_xy} para ignorar passos se estiver muito longe.")

    # Histórico das últimas posições para detectar se está "parado" no mesmo lugar
    last_positions = []
    # Contador de tentativas sem progresso
    no_progress_count = 0
    # Movimentos que falharam recentemente
    failed_moves = set()

    # Lista de direções (ajustes conforme seu jogo)
    directions = [
        ("DIAGONAL_BAIXO_DIREITA", 2, 1),
        ("DIAGONAL_BAIXO_ESQUERDA", -1, 2),
        ("DIAGONAL_CIMA_DIREITA", 1, -2),
        ("DIAGONAL_CIMA_ESQUERDA", -2, -1),
        ("RIGHT", 1, -1),
        ("LEFT", -1, 1),
        ("DOWN", 1, 1),
        ("UP", -1, -1)
    ]

    # Loop principal: continua enquanto estiver fora da "tolerância" do destino
    while abs(current_x - target_x) > tolerance or abs(current_y - target_y) > tolerance:
        # Sempre atualiza a posição
        coords = uo_assist.get_character_coords()
        if not coords:
            print("Erro: Não foi possível obter a posição atual.")
            return
        updated_x, updated_y = coords

        # Se a flag de pausa estiver marcada, pausar 40s
        if pause_flag:
            print("Pausando por 40 segundos...")
            time.sleep(40)
            pause_flag = False

        # Adiciona a posição atual ao histórico
        last_positions.append((updated_x, updated_y))
        if len(last_positions) > stuck_threshold:
            last_positions.pop(0)  # Mantém só as últimas 'stuck_threshold'

        # Atualiza current_x, current_y
        current_x, current_y = updated_x, updated_y

        # --- Verificação da distância ao alvo ---
        dist_x = abs(current_x - target_x)
        dist_y = abs(current_y - target_y)
        # Considera que só podemos estar "presos" se estivermos dentro de max_dist_xy
        is_near_enough = (dist_x <= max_dist_xy and dist_y <= max_dist_xy)

        # --- Se está perto do alvo, faz a detecção normal de 'preso' ---
        if is_near_enough:
            # DETECÇÃO 1: Mesmo ponto por 'stuck_threshold' leituras
            if len(last_positions) == stuck_threshold and len(set(last_positions)) == 1:
                print(f"🚨 Personagem preso na posição {last_positions[0]} (repetido {stuck_threshold} vezes). Tentando escapar...")
                # Chama callback ou movimentação de desbloqueio
                if on_stuck_callback:
                    on_stuck_callback(current_x, current_y, failed_moves)
                else:
                    move_away_from_wall(failed_moves)  # Implemente a seu critério

                last_positions.clear()
                no_progress_count = 0
                failed_moves.clear()
                continue

            # DETECÇÃO 2: Várias tentativas sem progresso
            if len(last_positions) >= 2 and last_positions[-1] == last_positions[-2]:
                no_progress_count += 1
            else:
                no_progress_count = 0

            if no_progress_count >= max_attempts:
                print(f"⚠ O personagem não está avançando na posição ({current_x}, {current_y}). Tentando desbloquear...")
                if on_stuck_callback:
                    on_stuck_callback(current_x, current_y, failed_moves)
                else:
                    move_away_from_wall(failed_moves)

                last_positions.clear()
                no_progress_count = 0
                failed_moves.clear()
                continue
        else:
            # Se está longe demais (fora de max_dist_xy),
            # não consideramos "preso" (mas ainda podemos contar tentativas sem movimento).
            if len(last_positions) >= 2 and last_positions[-1] == last_positions[-2]:
                no_progress_count += 1
            else:
                no_progress_count = 0
            # (Opcional) Se quiser, você pode disparar alguma lógica caso fique muito tempo longe sem avançar.

        # --- Ordena direções para tentar chegar mais perto do alvo ---
        directions.sort(key=lambda d: abs((current_x + d[1]) - target_x) + abs((current_y + d[2]) - target_y))

        moved = False
        for move_name, dx, dy in directions:
            new_x = current_x + dx
            new_y = current_y + dy

            # Se a distância em X ou Y excede max_dist_xy, ignoramos este movimento
            if abs(new_x - target_x) > max_dist_xy or abs(new_y - target_y) > max_dist_xy:
                print(f"Pulando posição .. ({current_x}, {current_y})")
                if on_move_callback:
                    on_move_callback()
                return

            # Evita tentativas que falharam
            if (new_x, new_y) in failed_moves:
                continue

            # Checa pausa
            if pause_flag:
                print("Pausando por 40 segundos...")
                time.sleep(40)
                pause_flag = False

            # Aperta a tecla/função de movimento (ajuste para seu jogo)
            controlador.press_and_release(controlador.get_movements()[move_name], delay_ini=step_delay_fn())

            # Lê a posição depois do movimento
            coords = uo_assist.get_character_coords()
            if not coords:
                print("Erro ao atualizar posição.")
                return
            updated_x, updated_y = coords

            # Se mudou efetivamente, sai do loop de direções
            if (updated_x, updated_y) != (current_x, current_y):
                moved = True
                current_x, current_y = updated_x, updated_y
                break
            else:
                # Se não se mexeu, marca esse movimento como falho
                failed_moves.add((new_x, new_y))

        # Se for necessário, você pode adicionar algo caso 'moved' ainda seja False

    # Se chegou até aqui, significa que estamos dentro da tolerância
    if on_move_callback:
        on_move_callback()  # ou chame com parâmetros se preferir

    print(f"🏁 Destino alcançado! Posição final: X={current_x}, Y={current_y} (tolerância={tolerance})")




def load_movement_path_with_selection(save_folder="gravados", default_min_delay=0.2, default_max_delay=0.5, move_callback_after=None, move_callback_before=None):
    """
    Lista todos os arquivos de movimentos gravados e permite ao usuário escolher um para carregar.
    Carrega os delays gravados ou usa os delays padrões.

    Args:
        save_folder (str): Pasta onde os arquivos de coordenadas estão armazenados.
        default_min_delay (float): Delay mínimo padrão caso o arquivo não tenha um delay salvo.
        default_max_delay (float): Delay máximo padrão caso o arquivo não tenha um delay salvo.
        move_callback (function): Função a ser chamada em cada movimento.

    Returns:
        list: Lista de tuplas no formato [(x, y, step_delay_fn, move_callback), ...]
    """
    if not os.path.exists(save_folder):
        print(f"❌ A pasta '{save_folder}' não existe!")
        return []

    files = [f for f in os.listdir(save_folder) if f.endswith(".json")]
    
    if not files:
        print("❌ Nenhum arquivo de movimento encontrado!")
        return []

    # Exibir lista de arquivos disponíveis
    print("\n📂 Arquivos disponíveis:")
    for i, file in enumerate(files):
        print(f"[{i+1}] {file}")

    # Solicitar escolha do usuário
    while True:
        try:
            choice = int(input("Digite o número do arquivo que deseja carregar: ")) - 1
            if 0 <= choice < len(files):
                filename = os.path.join(save_folder, files[choice])
                break
            else:
                print("❌ Escolha inválida! Tente novamente.")
        except ValueError:
            print("❌ Entrada inválida! Digite um número.")

    # Carregar o arquivo escolhido
    with open(filename, "r") as f:
        data = json.load(f)

    path = []
    for entry in data:
        min_delay = entry.get("min_delay", default_min_delay)
        max_delay = entry.get("max_delay", default_max_delay)
        tolerance = entry.get("tolerance", 1)
        exec_callback_after = entry.get("exec_callback_after", None)
        exec_callback_before = entry.get("exec_callback_before", None)
        moves_after = entry.get("moves_after", [])

        # Criar uma função de delay dinâmico para cada movimento
        def step_delay_fn(min_d=min_delay, max_d=max_delay):
            return random.uniform(min_d, max_d)

        path.append((entry["x"], entry["y"], step_delay_fn, move_callback_before,move_callback_after,tolerance,moves_after,exec_callback_after,exec_callback_before))

    print(f"📄 {len(path)} coordenadas carregadas do arquivo '{files[choice]}'")
    
    return path


import os
import keyboard
import json
import random
from datetime import datetime

def record_position_xy(uo_assist, save_folder="gravados", filename=None):
    """
    Grava coordenadas do personagem ao pressionar ESC ou F1 e salva em um arquivo.

    - `ESC`: Usa o delay padrão definido pelo usuário.
    - `F1`: Usa um delay fixo de 0.1 segundos.
    - `CTRL+C`: Encerra a gravação corretamente.
    - Se o arquivo já existir, ele continua de onde parou.

    Args:
        uo_assist (UOAssistConnector): Instância do UOAssist para obter coordenadas.
        save_folder (str): Pasta onde os arquivos de coordenadas serão salvos.
        filename (str, optional): Nome do arquivo para salvar. Se None, pede um nome ao usuário.
    """
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)  # Cria a pasta se não existir

    # Solicita um nome de arquivo ao usuário se não for fornecido
    if not filename:
        filename_base = input("📁 Digite o nome do arquivo para salvar os movimentos: ").strip()
        filename = os.path.join(save_folder, f"{filename_base}.json")

    # Se o arquivo já existir, carrega os dados para continuar gravando
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                recorded_positions = json.load(f)
                print(f"🔄 Continuando gravação no arquivo '{filename}' ({len(recorded_positions)} coordenadas existentes).")
            except json.JSONDecodeError:
                print(f"⚠️ Erro ao carregar '{filename}'. Criando um novo arquivo.")
                recorded_positions = []
    else:
        recorded_positions = []

    # Pergunta o range de delay
    while True:
        try:
            min_delay = float(input("⏳ Digite o delay mínimo (segundos): "))
            max_delay = float(input("⏳ Digite o delay máximo (segundos): "))
            if min_delay > 0 and max_delay >= min_delay:
                break
            else:
                print("❌ O delay máximo deve ser maior ou igual ao mínimo, e ambos devem ser positivos.")
        except ValueError:
            print("❌ Entrada inválida! Digite valores numéricos.")

    print(f"🎬 Pressione F1 para gravar com delay padrão ({min_delay}-{max_delay}s)")
    print(f"🎬 Pressione F2 para gravar com delay fixo de 0.1s")
    print(f"🛑 Pressione CTRL+C para sair.")

    try:
        while True:
            event = keyboard.read_event(suppress=True)  # Captura qualquer tecla pressionada

            if event.event_type == keyboard.KEY_DOWN:  # Apenas quando a tecla for pressionada
                coords = uo_assist.get_character_coords()
                if not coords:
                    print("Erro ao obter coordenadas.")
                    continue

                current_x, current_y = coords

                if event.name == "f1":
                    delay_min = min_delay
                    delay_max = max_delay
                    print(f"🔴 Coordenada gravada com delay padrão: ({current_x}, {current_y})")

                elif event.name == "f2":
                    delay_min = 0.1
                    delay_max = 0.1
                    print(f"🔴 Coordenada gravada com delay fixo de 0.1s: ({current_x}, {current_y})")

                else:
                    continue  # Ignora outras teclas

                recorded_positions.append({
                    "x": current_x,
                    "y": current_y,
                    "min_delay": delay_min,
                    "max_delay": delay_max
                })

                # Salva no arquivo em tempo real, preservando as coordenadas antigas
                with open(filename, "w") as f:
                    json.dump(recorded_positions, f, indent=4)

                print(f"📁 Coordenadas salvas em {filename}")

    except KeyboardInterrupt:
        print("\n🛑 Gravação interrompida pelo usuário. Coordenadas salvas com sucesso!")

def execute_movement_path(uo_assist, path, tolerance=2, stuck_threshold=3, step_delay=0.2):
    """
    Percorre um caminho baseado em um mapa de coordenadas, movendo-se de ponto a ponto.

    Args:
        uo_assist (UOAssistConnector): Instância do UOAssist para obter coordenadas.
        path (list of tuples): Lista de pontos no formato (x, y, step_delay_fn, move_callback).
        tolerance (int): Distância aceitável do destino para considerar como "chegou".
        stuck_threshold (int): Quantidade de vezes que o personagem precisa repetir a mesma posição para ser considerado preso.
    """
    global pause_flag
    pause_flag = False
    if not uo_assist.attach_to_assistant():
        print("Erro: Não foi possível anexar ao UOAssist.")
        return
    
    coords = uo_assist.get_character_coords()
    if not coords:
        print("Erro: Não foi possível obter as coordenadas iniciais.")
        return
    
    current_x, current_y = coords
    print(f"Posição inicial: X={current_x}, Y={current_y}")
    print(f"Iniciando percurso... {len(path)} pontos no total")

    for target_x, target_y, step_delay_fn, move_callback_before, move_callback_after,tolerance_local,moves_after,exec_callback_after,exec_callback_before in path:
        if not exec_callback_before or exec_callback_before == 1:
            if move_callback_before:
                move_callback_before()
        if tolerance_local:
            tolerance = tolerance_local
        if pause_flag:  # Checa novamente no “meio” do timeout
            print("Pausando por 40 segundos durante a espera...")
            time.sleep(40)
            pause_flag = False
        print(f"📍 Movendo para o próximo ponto: ({target_x}, {target_y})")
        def delay_fn():
            return step_delay
        move_to_target_smart(
            uo_assist,
            target_x=target_x,
            target_y=target_y,
            step_delay_fn=delay_fn,
            tolerance=tolerance,
            stuck_threshold=stuck_threshold,
            on_move_callback=None
        )
        if moves_after:
            for move in moves_after:
                controlador.press_and_release(controlador.get_movements()[move], delay_ini=0.3)
        if not exec_callback_after or exec_callback_after == 1:
            if move_callback_after:
                move_callback_after()
        if step_delay_fn:
            time.sleep(step_delay_fn())
    print("✅ Percurso completo!")
    #keyboard.unhook_all()


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
        print("Clicando loot ... ")
        controlador.press_and_release(controlador.get_movements()["CLICKY"],delay_ini=delay_ini)

def pressiona_solta(btn,delay=0.3):
    controlador.press_and_release(btn,delay_end=delay)