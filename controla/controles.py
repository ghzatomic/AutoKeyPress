import random
import time
import os
import json
import keyboard
from datetime import datetime

class MovementHelper:
    def __init__(self, controlador):
        """
        :param controlador: Instância de controlador (KeyboardController, KeyboardControllerWindow, GamepadController, etc.)
        """
        self.controlador = controlador
        self.pause_flag = False

        # Ao inicializar, registramos a tecla ESC para pausar
        keyboard.on_press_key("esc", self.on_esc_key)

    def on_esc_key(self, event):
        """
        Callback chamada toda vez que a tecla 'esc' for pressionada.
        Define a flag de pausa.
        """
        self.pause_flag = True
        print("Tecla ESC pressionada! Sinalizando pausa...")

    def move_randomly_to_unstuck(self, failed_moves):
        """
        Realiza um movimento aleatório para tentar destravar o personagem.
        Evita movimentos já tentados anteriormente.

        Args:
            failed_moves (set): Conjunto de movimentos que já falharam.
        """
        available_moves = [m for m in self.controlador.get_movements().keys() if m not in failed_moves]

        if not available_moves:
            print("Nenhum movimento disponível para destravar! Resetando tentativas...")
            failed_moves.clear()
            available_moves = list(self.controlador.get_movements().keys())

        move_name = random.choice(available_moves)
        print(f"Tentando destravar com o movimento: {move_name}")
        self.controlador.press_and_release(move_name, delay_ini=0.5)

    def move_away_from_wall(self, failed_moves):
        """
        Quando o personagem fica preso entre dois obstáculos laterais e uma parede,
        ele tenta se mover para cima ou diagonalmente para sair do canto.
        """
        escape_moves = ["UP", "DIAGONAL_CIMA_ESQUERDA", "DIAGONAL_CIMA_DIREITA",
                        "DIAGONAL_BAIXO_DIREITA", "DIAGONAL_BAIXO_ESQUERDA",
                        "DOWN", "LEFT", "RIGHT"]
        
        # Remove movimentos que já falharam para não repetir erros
        available_moves = [m for m in escape_moves if m not in failed_moves]

        if not available_moves:
            print("⚠ Nenhuma opção de saída disponível! Resetando tentativas...")
            failed_moves.clear()
            available_moves = escape_moves

        move_name = random.choice(available_moves)
        print(f"🚀 Tentando escapar com: {move_name}")
        self.controlador.press_and_release(move_name,
                                           delay_ini=random.uniform(0.5, 1))

    def move_away_from_wall_long(self, failed_moves):
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
            available_moves = escape_moves

        move_name, dx, dy = random.choice(available_moves)
        print(f"🚀 Tentando escapar com movimento longo: {move_name}")

        for _ in range(random.randint(3, 15)):
            self.controlador.press_and_release(move_name, delay_ini=0.2)

    def calibrate_directions(self, uo_assist, directions_to_test, pause=1):
        """
        directions_to_test: lista de strings (nomes das direções), ex. ['RIGHT','UP',...]
        Faz cada movimento, mede a diferença (dx,dy) e retorna um dicionário:
           { "DIRECTION_NAME": (dx, dy), ... }

        :param uo_assist: instância de UOAssist (ou classe similar) que controla e lê o UO.
        :param directions_to_test: lista de nomes de direções que você quer calibrar.
        :param pause: tempo (segundos) para esperar o char efetivamente se mover.
        """
        calibration = {}

        for direction_name in directions_to_test:
            old_coords = uo_assist.get_character_coords()
            if not old_coords:
                print("[Calibração] Erro ao obter coords antes de mover.")
                continue

            old_x, old_y = old_coords
            print(f"[Calibração] Movendo: {direction_name}... (Posição inicial: {old_x}, {old_y})")

            # Envia o comando para andar nessa direção
            self.controlador.press_and_release(direction_name,
                                               delay_ini=0.15)

            time.sleep(pause)

            new_coords = uo_assist.get_character_coords()
            if not new_coords:
                print("[Calibração] Erro ao obter coords depois de mover.")
                continue

            new_x, new_y = new_coords
            dx = new_x - old_x
            dy = new_y - old_y
            calibration[direction_name] = (dx, dy)

            print(f"   -> dx={dx}, dy={dy} (nova posição: {new_x}, {new_y})")

        return calibration

    def test_calibration(self, uo_assist, pause=0.1):
        """
        Função que executa todo o processo de calibração:
          - Conecta ao assistente.
          - Calibra as direções.
          - Salva o resultado em JSON.
        """
        DIRECTIONS_TO_TEST = [
            "RIGHT", "LEFT", "UP", "DOWN",
            "DIAGONAL_BAIXO_DIREITA",
            "DIAGONAL_BAIXO_ESQUERDA",
            "DIAGONAL_CIMA_DIREITA",
            "DIAGONAL_CIMA_ESQUERDA"
        ]

        directions_map = self.calibrate_directions(uo_assist, DIRECTIONS_TO_TEST, pause=pause)

        print("\n=== Resultado da calibração ===")
        for dname, (dx, dy) in directions_map.items():
            print(f"{dname} -> dx={dx}, dy={dy}")

        filename = "directions_map.json"
        with open(filename, "w") as f:
            json.dump(directions_map, f, indent=2)

        print(f"\nMapa de direções salvo em '{filename}'!")
        print("Use esse arquivo para o seu 'move_to_target_smart', carregando (dx, dy) automaticamente.")


    def move_to_target_smart_v2(self, uo_assist, target_x, target_y, step_delay_fn,
                                tolerance=0,
                                stuck_threshold=8,   # Quantas posições no histórico para detectar "travado"
                                on_move_callback=None,
                                on_stuck_callback=None,
                                max_attempts=3,
                                max_dist_xy=50,
                                simulate_human=False,    # Novo: ativa variação para simular comportamento humano
                                jitter=0.2):             # Novo: jitter a ser adicionado na ordenação das direções
        """
        Move o personagem até (target_x, target_y) com tolerância e detecção de bloqueios.
        
        Parâmetros adicionais para "humanizar" os movimentos:
        - simulate_human: se True, ativa variações aleatórias.
        - jitter: valor que será adicionado de forma aleatória na avaliação das direções.
        """
        self.pause_flag = False

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
        
        last_positions = []
        no_progress_count = 0
        failed_moves = set()

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

        while abs(current_x - target_x) > tolerance or abs(current_y - target_y) > tolerance:
            coords = uo_assist.get_character_coords()
            if not coords:
                print("Erro: Não foi possível obter a posição atual.")
                return
            updated_x, updated_y = coords

            if self.pause_flag:
                print("Pausando por 40 segundos...")
                time.sleep(40)
                self.pause_flag = False

            last_positions.append((updated_x, updated_y))
            if len(last_positions) > stuck_threshold:
                last_positions.pop(0)

            current_x, current_y = updated_x, updated_y

            # Verifica a distância atual ao alvo
            dist_x = abs(current_x - target_x)
            dist_y = abs(current_y - target_y)
            is_near_enough = (dist_x <= max_dist_xy and dist_y <= max_dist_xy)

            # Detecção de "preso" somente se estiver perto
            if is_near_enough:
                if len(last_positions) == stuck_threshold and len(set(last_positions)) == 1:
                    print(f"🚨 Personagem preso na posição {last_positions[0]} (repetido {stuck_threshold} vezes).")
                    if on_stuck_callback:
                        on_stuck_callback(current_x, current_y, failed_moves)
                    else:
                        self.move_away_from_wall(failed_moves)
                    last_positions.clear()
                    no_progress_count = 0
                    failed_moves.clear()
                    continue

                if len(last_positions) >= 2 and last_positions[-1] == last_positions[-2]:
                    no_progress_count += 1
                else:
                    no_progress_count = 0

                if no_progress_count >= max_attempts:
                    print(f"⚠ O personagem não está avançando na posição ({current_x}, {current_y}).")
                    if on_stuck_callback:
                        on_stuck_callback(current_x, current_y, failed_moves)
                    else:
                        self.move_away_from_wall(failed_moves)
                    last_positions.clear()
                    no_progress_count = 0
                    failed_moves.clear()
                    continue
            else:
                # Quando está longe, não aciona a lógica de "preso", mas ainda conta no_progress se desejar.
                if len(last_positions) >= 2 and last_positions[-1] == last_positions[-2]:
                    no_progress_count += 1
                else:
                    no_progress_count = 0

            # Ordena as direções: se simulate_human estiver ativo, adiciona jitter aleatório à avaliação.
            directions.sort(key=lambda d: (abs((current_x + d[1]) - target_x) + abs((current_y + d[2]) - target_y)
                                        + (random.uniform(-jitter, jitter) if simulate_human else 0)))

            moved = False
            for move_name, dx, dy in directions:
                new_x = current_x + dx
                new_y = current_y + dy

                # Ignora movimentos que fiquem fora do max_dist_xy
                if abs(new_x - target_x) > max_dist_xy or abs(new_y - target_y) > max_dist_xy:
                    continue

                if (new_x, new_y) in failed_moves:
                    continue

                if self.pause_flag:
                    print("Pausando por 40 segundos...")
                    time.sleep(40)
                    self.pause_flag = False

                # Se simulate_human, utiliza um delay aleatório; senão, usa o valor retornado pela função step_delay_fn.
                delay = step_delay_fn()

                self.controlador.press_and_release(move_name, delay_ini=delay)

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
                    failed_moves.add((new_x, new_y))

            # Se nenhum movimento funcionou, pode-se inserir uma lógica extra (por exemplo, um delay maior ou uma tentativa de recuperação).

        if on_move_callback:
            on_move_callback()

        print(f"🏁 Destino alcançado! Posição final: X={current_x}, Y={current_y} (tolerância = {tolerance})")


    def move_to_target_smart(self,
                             uo_assist, target_x, target_y, step_delay_fn,
                             tolerance=0,
                             stuck_threshold=5,
                             on_move_callback=None,
                             on_stuck_callback=None,
                             max_attempts=5,
                             max_dist_xy=50):
        """
        Versão parecida com move_to_target_smart_v2, porém com outro set de direções.
        """
        self.pause_flag = False

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

        last_positions = []
        no_progress_count = 0
        failed_moves = set()

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

        while abs(current_x - target_x) > tolerance or abs(current_y - target_y) > tolerance:
            coords = uo_assist.get_character_coords()
            if not coords:
                print("Erro: Não foi possível obter a posição atual.")
                return
            updated_x, updated_y = coords

            if self.pause_flag:
                print("Pausando por 40 segundos...")
                time.sleep(40)
                self.pause_flag = False

            last_positions.append((updated_x, updated_y))
            if len(last_positions) > stuck_threshold:
                last_positions.pop(0)

            current_x, current_y = updated_x, updated_y

            dist_x = abs(current_x - target_x)
            dist_y = abs(current_y - target_y)
            is_near_enough = (dist_x <= max_dist_xy and dist_y <= max_dist_xy)

            if is_near_enough:
                # DETECÇÃO 1
                if len(last_positions) == stuck_threshold and len(set(last_positions)) == 1:
                    print(f"🚨 Personagem preso na posição {last_positions[0]} (repetido {stuck_threshold} vezes).")
                    if on_stuck_callback:
                        on_stuck_callback(current_x, current_y, failed_moves)
                    else:
                        self.move_away_from_wall(failed_moves)

                    last_positions.clear()
                    no_progress_count = 0
                    failed_moves.clear()
                    continue

                # DETECÇÃO 2
                if len(last_positions) >= 2 and last_positions[-1] == last_positions[-2]:
                    no_progress_count += 1
                else:
                    no_progress_count = 0

                if no_progress_count >= max_attempts:
                    print(f"⚠ O personagem não está avançando na posição ({current_x}, {current_y}).")
                    if on_stuck_callback:
                        on_stuck_callback(current_x, current_y, failed_moves)
                    else:
                        self.move_away_from_wall(failed_moves)

                    last_positions.clear()
                    no_progress_count = 0
                    failed_moves.clear()
                    continue
            else:
                if len(last_positions) >= 2 and last_positions[-1] == last_positions[-2]:
                    no_progress_count += 1
                else:
                    no_progress_count = 0

            directions.sort(key=lambda d: abs((current_x + d[1]) - target_x) + abs((current_y + d[2]) - target_y))

            moved = False
            for move_name, dx, dy in directions:
                new_x = current_x + dx
                new_y = current_y + dy

                if abs(new_x - target_x) > max_dist_xy or abs(new_y - target_y) > max_dist_xy:
                    print(f"Pulando posição .. ({current_x}, {current_y})")
                    if on_move_callback:
                        on_move_callback()
                    return

                if (new_x, new_y) in failed_moves:
                    continue

                if self.pause_flag:
                    print("Pausando por 40 segundos...")
                    time.sleep(40)
                    self.pause_flag = False

                self.controlador.press_and_release(
                    move_name,
                    delay_ini=step_delay_fn()
                )

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
                    failed_moves.add((new_x, new_y))

        if on_move_callback:
            on_move_callback()

        print(f"🏁 Destino alcançado! Posição final: X={current_x}, Y={current_y} (tolerância={tolerance})")


    def load_movement_path_with_selection(self, uo_assist, selection_callback=None,
                                            save_folder="gravados",
                                            default_min_delay=0.2,
                                            default_max_delay=0.5,
                                            move_callback_after=None,
                                            move_callback_before=None):
        """
        Carrega o caminho de movimentos de um arquivo JSON contido em save_folder.
        Se selection_callback for fornecido, ele será chamado com a lista de arquivos disponíveis
        e deverá retornar o nome do arquivo escolhido.
        Caso contrário, usa interação via console.
        Retorna uma lista de tuplas com os dados do caminho.
        """
        if not os.path.exists(save_folder):
            print(f"❌ A pasta '{save_folder}' não existe!")
            return []

        files = [f for f in os.listdir(save_folder) if f.endswith(".json")]
        if not files:
            print("❌ Nenhum arquivo de movimento encontrado!")
            return []

        if selection_callback:
            chosen_file = selection_callback(files)
            if not chosen_file:
                print("Nenhum arquivo selecionado via callback.")
                return []
            filename = os.path.join(save_folder, chosen_file)
        else:
            print("\n📂 Arquivos disponíveis:")
            for i, file in enumerate(files):
                print(f"[{i+1}] {file}")
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

        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar o arquivo: {e}")
            return []

        path = []
        for entry in data:
            min_delay = entry.get("min_delay", default_min_delay)
            max_delay = entry.get("max_delay", default_max_delay)
            tolerance = entry.get("tolerance", 1)
            exec_callback_after = entry.get("exec_callback_after", True)
            exec_callback_before = entry.get("exec_callback_before", True)
            moves_after = entry.get("moves_after", [])
            wait_between_moves_after = entry.get("wait_between_moves_after", None)
            exec_scripts_after = entry.get("exec_scripts_after", [])

            def step_delay_fn(min_d=min_delay, max_d=max_delay):
                return random.uniform(min_d, max_d)

            path.append((
                entry["x"],
                entry["y"],
                step_delay_fn,
                move_callback_before,
                move_callback_after,
                tolerance,
                moves_after,
                exec_callback_after,
                exec_callback_before,
                wait_between_moves_after,
                exec_scripts_after
            ))
        print(f"📄 {len(path)} coordenadas carregadas do arquivo '{os.path.basename(filename)}'")
        return path

    def load_movement_path_with_selection_old(self,
                                          uo_assist,
                                          save_folder="gravados",
                                          default_min_delay=0.2,
                                          default_max_delay=0.5,
                                          move_callback_after=None,
                                          move_callback_before=None):
        """
        Lista todos os arquivos de movimentos gravados e permite ao usuário escolher um para carregar.
        Carrega os delays gravados ou usa os delays padrões.
        """
        if not os.path.exists(save_folder):
            print(f"❌ A pasta '{save_folder}' não existe!")
            return []

        files = [f for f in os.listdir(save_folder) if f.endswith(".json")]
        
        if not files:
            print("❌ Nenhum arquivo de movimento encontrado!")
            return []

        print("\n📂 Arquivos disponíveis:")
        for i, file in enumerate(files):
            print(f"[{i+1}] {file}")

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

        with open(filename, "r") as f:
            data = json.load(f)

        path = []
        for entry in data:
            min_delay = entry.get("min_delay", default_min_delay)
            max_delay = entry.get("max_delay", default_max_delay)
            tolerance = entry.get("tolerance", 1)
            exec_callback_after = entry.get("exec_callback_after", True)
            exec_callback_before = entry.get("exec_callback_before", True)
            moves_after = entry.get("moves_after", [])
            wait_between_moves_after = entry.get("wait_between_moves_after", None)
            exec_scripts_after = entry.get("exec_scripts_after", [])
            

            def step_delay_fn(min_d=min_delay, max_d=max_delay):
                return random.uniform(min_d, max_d)

            path.append(
                (
                    entry["x"],
                    entry["y"],
                    step_delay_fn,
                    move_callback_before,
                    move_callback_after,
                    tolerance,
                    moves_after,
                    exec_callback_after,
                    exec_callback_before,
                    wait_between_moves_after,
                    exec_scripts_after
                )
            )

        print(f"📄 {len(path)} coordenadas carregadas do arquivo '{files[choice]}'")
        return path

    def record_position_xy(self, uo_assist, save_folder="gravados", filename=None, 
                           default_min_delay=None, default_max_delay=None):
        """
        Grava coordenadas do personagem ao pressionar F1, F2, F3 e F4 e salva em um arquivo.
        Se os delays forem passados (default_min_delay e default_max_delay), eles serão usados
        sem solicitar input adicional.
        """
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        if not filename:
            filename_base = input("📁 Digite o nome do arquivo para salvar os movimentos: ").strip()
            filename = os.path.join(save_folder, f"{filename_base}.json")

        if os.path.exists(filename):
            with open(filename, "r") as f:
                try:
                    recorded_positions = json.load(f)
                    print(f"🔄 Continuando gravação no arquivo '{filename}' ({len(recorded_positions)} coordenadas).")
                except json.JSONDecodeError:
                    print(f"⚠️ Erro ao carregar '{filename}'. Criando um novo arquivo.")
                    recorded_positions = []
        else:
            recorded_positions = []

        if default_min_delay is not None and default_max_delay is not None:
            min_delay = default_min_delay
            max_delay = default_max_delay
        else:
            while True:
                try:
                    min_delay = float(input("⏳ Digite o delay mínimo (segundos): "))
                    max_delay = float(input("⏳ Digite o delay máximo (segundos): "))
                    if min_delay > 0 and max_delay >= min_delay:
                        break
                    else:
                        print("❌ O delay máximo deve ser >= mínimo, e ambos positivos.")
                except ValueError:
                    print("❌ Entrada inválida! Digite valores numéricos.")

        print(f"🎬 Pressione F1 para gravar com delay padrão ({min_delay}-{max_delay}s)")
        print("🎬 Pressione F2 para gravar com delay fixo de 0.1s")
        print("🎬 Pressione F3 para iniciar a contagem de tempo")
        print("🎬 Pressione F4 para gravar com o tempo decorrido entre F3 e F4")
        print("🛑 Pressione CTRL+C para sair.")

        start_time = None

        try:
            while True:
                event = keyboard.read_event(suppress=False)
                if event.event_type == keyboard.KEY_DOWN:
                    coords = uo_assist.get_character_coords()
                    if not coords:
                        print("Erro ao obter coordenadas.")
                        continue

                    current_x, current_y = coords

                    if event.name == "f1":
                        delay_min = min_delay
                        delay_max = max_delay
                        exec_callback_after = True
                        exec_callback_before = True
                        tolerance = 0
                        print(f"🔴 Coordenada gravada (delay padrão): ({current_x}, {current_y})")
                    elif event.name == "f2":
                        delay_min = 0.1
                        delay_max = 0.1
                        exec_callback_after = False
                        exec_callback_before = False
                        tolerance = 1
                        print(f"🔴 Coordenada gravada (delay fixo de 0.1s): ({current_x}, {current_y})")
                    elif event.name == "f3":
                        start_time = time.time()
                        print("⏱️ Contagem de tempo iniciada.")
                        continue
                    elif event.name == "f4" and start_time is not None:
                        elapsed_time = time.time() - start_time
                        delay_min = elapsed_time
                        delay_max = elapsed_time
                        exec_callback_after = True
                        exec_callback_before = True
                        tolerance = 0
                        print(f"🔴 Coordenada gravada (delay baseado no tempo: {elapsed_time:.2f}s): ({current_x}, {current_y})")
                        start_time = None
                    else:
                        continue

                    recorded_positions.append({
                        "x": current_x,
                        "y": current_y,
                        "min_delay": delay_min,
                        "max_delay": delay_max,
                        "exec_callback_after": exec_callback_after,
                        "exec_callback_before": exec_callback_before,
                        "tolerance": tolerance
                    })

                    with open(filename, "w") as f:
                        json.dump(recorded_positions, f, indent=4)

                    print(f"📁 Coordenadas salvas em {filename}")

        except KeyboardInterrupt:
            print("\n🛑 Gravação interrompida pelo usuário. Coordenadas salvas com sucesso!")

    def execute_movement_path(self, uo_assist, path, tolerance=1, stuck_threshold=3, step_delay=0.26):
        """
        Percorre um caminho baseado em um mapa de coordenadas, movendo-se de ponto a ponto.
        (Implementação similar à versão console.)
        """
        self.pause_flag = False

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

        for (target_x, target_y, step_delay_fn, move_callback_before, move_callback_after, tolerance_local,
             moves_after, exec_callback_after, exec_callback_before, wait_between_moves_after, exec_scripts_after) in path:

            if exec_callback_before is None or exec_callback_before == True:
                if move_callback_before:
                    move_callback_before()

            if tolerance_local:
                tolerance = tolerance_local

            if self.pause_flag:
                print("Pausando por 40 segundos (durante a espera)...")
                time.sleep(40)
                self.pause_flag = False

            print(f"📍 Movendo para o próximo ponto: ({target_x}, {target_y})")

            def delay_fn():
                return step_delay

            self.move_to_target_smart_v2(uo_assist, target_x, target_y, step_delay_fn,
                                         tolerance=tolerance, stuck_threshold=stuck_threshold)

            if moves_after:
                for move in moves_after:
                    self.controlador.press_and_release(move, delay_ini=0.3)
                    if wait_between_moves_after:
                        time.sleep(wait_between_moves_after)
            if exec_scripts_after:
                for script in exec_scripts_after:
                    self.controlador.send_text(script, delay=0.3)
                    if wait_between_moves_after:
                        time.sleep(wait_between_moves_after)
            if exec_callback_after is None or exec_callback_after == True:
                if move_callback_after:
                    move_callback_after()
            if step_delay_fn:
                time.sleep(step_delay_fn())

        print("✅ Percurso completo!")

    def random_sleep(self, min_seconds, max_seconds):
        """
        Faz um sleep com uma duração aleatória entre min_seconds e max_seconds.
        """
        duration = random.uniform(min_seconds, max_seconds)
        #print(f"Dormindo por {duration:.2f} segundos...")
        time.sleep(duration)

    def clica_loot(self, qtde=1, delay_ini=0.3):
        for i in range(qtde):
            print("Clicando loot ... ")
            self.controlador.press_and_release("MOUSE_CLICK_LEFT", delay_ini=delay_ini)
            time.sleep(0.2)


    def random_walk_neighbors(self, x_ini, y_ini, x_fim, y_fim, uo_assist,
                            step_size=1,
                            min_pause=5, max_pause=5,
                            num_moves=100,
                            stuck_threshold=3,
                            visited_tolerance=1,
                            move_fn=None):
        """
        Faz o personagem andar aleatoriamente usando apenas os pontos vizinhos.

        Em cada ponto, gera candidatos (definidos por step_size) e filtra:
        - Posições fora dos limites;
        - Posições muito próximas aos pontos visitados (definido por visited_tolerance);
        - Posições que já foram marcadas como bloqueadas (movimentos que falharam).

        As posições bloqueadas são salvas no arquivo 'blocked_positions.txt' e carregadas
        na inicialização, para que o bot já saiba quais locais são inacessíveis.

        Se após um movimento a posição atual ficar fora dos limites, o algoritmo reseta para a posição inicial.

        Parâmetros:
        - x_ini, y_ini, x_fim, y_fim: limites da área.
        - step_size: deslocamento máximo para pontos vizinhos.
        - min_pause, max_pause: intervalo (em segundos) para pausa entre os movimentos.
        - num_moves: número total de movimentos a executar.
        - stuck_threshold: número de leituras repetidas para considerar que o personagem está "stuck".
        - visited_tolerance: define a região (usando a distância de Chebyshev) ao redor de um ponto visitado que deve ser evitada.
        - move_fn: função que executa o movimento para uma posição (x, y). Se None, utiliza move_to_target_smart_v2.
        """
        import random, time, os

        blocked_file = "blocked_positions.txt"
        # Carrega as posições bloqueadas do arquivo, se existir.
        blocked = set()
        if os.path.exists(blocked_file):
            with open(blocked_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            bx, by = map(int, line.split(','))
                            blocked.add((bx, by))
                        except Exception:
                            pass

        # Se move_fn não for fornecida, define uma função padrão
        if move_fn is None:
            def step_delay_fn():
                return random.uniform(0.2, 0.3)
            
            def on_stuck_callback(current_x, current_y, failed_moves):
                neighbors = []
                for dx in range(-step_size, step_size + 1):
                    for dy in range(-step_size, step_size + 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx = current_x + dx
                        ny = current_y + dy
                        if nx < x_ini or nx > x_fim or ny < y_ini or ny > y_fim:
                            continue
                        if (nx, ny) in failed_moves:
                            continue
                        neighbors.append((nx, ny))
                if neighbors:
                    new_target = random.choice(neighbors)
                    print(f"Stuck detectado em ({current_x},{current_y}). Tentando novo vizinho: {new_target}")
                    return new_target
                else:
                    print("Nenhum vizinho disponível para sair do stuck.")
                    return None

            def move_fn(x, y):
                print(f"Movendo para ({x}, {y})")
                self.move_to_target_smart_v2(uo_assist, x, y, step_delay_fn,
                                            tolerance=0,
                                            stuck_threshold=stuck_threshold,
                                            on_move_callback=None,
                                            on_stuck_callback=on_stuck_callback,
                                            max_attempts=3,
                                            max_dist_xy=50,  # Considera a vizinhança
                                            simulate_human=False,
                                            jitter=0.2)

        # Obtém a posição atual via uo_assist; se falhar, usa (x_ini, y_ini)
        coords = uo_assist.get_character_coords()
        if coords:
            current_x, current_y = coords
        else:
            current_x, current_y = x_ini, y_ini
        print(f"Iniciando random walk a partir de ({current_x}, {current_y})")

        # Lista de pontos visitados (para evitar repetir áreas)
        visited = [(current_x, current_y)]

        for i in range(num_moves):
            # Gera a lista de candidatos (pontos vizinhos) filtrando:
            #   - Posições fora dos limites;
            #   - Posições muito próximas aos pontos visitados (definido por visited_tolerance);
            #   - Posições marcadas como bloqueadas.
            candidates = []
            for dx in range(-step_size, step_size + 1):
                for dy in range(-step_size, step_size + 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx = current_x + dx
                    ny = current_y + dy
                    if nx < x_ini or nx > x_fim or ny < y_ini or ny > y_fim:
                        continue
                    if (nx, ny) in blocked:
                        continue
                    too_close = False
                    for (vx, vy) in visited:
                        if max(abs(nx - vx), abs(ny - vy)) < visited_tolerance:
                            too_close = True
                            break
                    if too_close:
                        continue
                    candidates.append((nx, ny))
            if not candidates:
                print("Nenhum vizinho válido disponível. Encerrando random walk.")
                break

            # Escolhe aleatoriamente um dos candidatos
            next_x, next_y = random.choice(candidates)
            
            # Tenta mover para o candidato escolhido
            move_fn(next_x, next_y)
            
            # Após o movimento, obtém a posição atual
            coords = uo_assist.get_character_coords()
            if coords:
                new_x, new_y = coords
            else:
                new_x, new_y = next_x, next_y

            # Se a posição não mudou, o movimento falhou.
            if (new_x, new_y) == (current_x, current_y):
                print(f"Falha ao mover para ({next_x}, {next_y}). Marcando como bloqueado.")
                blocked.add((next_x, next_y))
                with open(blocked_file, "a") as f:
                    f.write(f"{next_x},{next_y}\n")
                continue

            # Verifica se a nova posição está fora dos limites. Se estiver, reseta para a posição inicial.
            if new_x < x_ini or new_x > x_fim or new_y < y_ini or new_y > y_fim:
                print(f"Posição ({new_x}, {new_y}) fora dos limites. Resetando para posição inicial ({x_ini}, {y_ini}).")
                current_x, current_y = x_ini, y_ini
                visited.append((current_x, current_y))
                continue

            # Movimento bem-sucedido: atualiza a posição e registra o local visitado.
            current_x, current_y = new_x, new_y
            visited.append((current_x, current_y))
            print(f"Posição atual atualizada para ({current_x}, {current_y})")

            # Pausa entre os movimentos para simular a decisão.
            duracao = random.uniform(min_pause, max_pause)
            print(f"Aguardando {duracao:.2f} segundos")
            time.sleep(duracao)






