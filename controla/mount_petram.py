from controla.controles import *



def movimento_batedor_petran_lvl2_dragoes_arco():
    delay_cait = 0.7

    def clica_loot_timer():
        clica_loot()
        random_sleep(0.1,0.1)

    def andar():

        sequence_salinha_dragoes = [
            ('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),
            ('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),
            ('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),
            ('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),
            ('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),
            ('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),
            ('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),
            ('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),
        ]  # Sequência de movimentos

        for move,delay in sequence_salinha_dragoes:
            print(f"Aqui : {move},{delay}")
            pressiona_botao(movements[move], delay_ini=delay)
            time.sleep(delay_cait)
            #clica_loot_timer()
            #for x in range(2):
            #    clica_loot()

    while True:
        #RESETAR
        andar()

def movimento_batedor_petran_lvl1_harpia():
    delay_cait = 0.7

    def clica_loot_timer():
        clica_loot()
        random_sleep(0.1,0.1)

    def andar():

        sequence_salinha_dragoes = [
            ('DIAGONAL_CIMA_DIREITA',delay_cait),('CLICK',0.1),('DIAGONAL_CIMA_DIREITA',delay_cait),('CLICK',0.1),('DIAGONAL_CIMA_DIREITA',delay_cait),('DIAGONAL_CIMA_DIREITA',delay_cait),('CLICK',0.1),
            ('DIAGONAL_CIMA_DIREITA',delay_cait),('DIAGONAL_CIMA_DIREITA',delay_cait),('DIAGONAL_CIMA_DIREITA',delay_cait),('DIAGONAL_CIMA_DIREITA',delay_cait),('CLICK',0.1),
            ('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('CLICK',0.1),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('CLICK',0.1),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('CLICK',0.1),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('CLICK',0.1),
            ('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('CLICK',0.1),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('CLICK',0.1),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('CLICK',0.1),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('CLICK',0.1),
            ('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),
            ('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),
            
        ]  # Sequência de movimentos


        for move,delay in sequence_salinha_dragoes:
            pressiona_botao(movements[move], delay_ini=delay)
            #time.sleep(delay_cait)
            clica_loot_timer()
            random_sleep(0.7,1)

    while True:
        #RESETAR

        andar()
        for x in range(6):
            clica_loot_timer()
        #random_sleep(1*60, 2*60)
        for x in range(6):
            clica_loot_timer()
        perform_random_movements_with_breaks(
            num_movements=3, 
            delay=0.3, 
            pause_duration=0, 
            pause_interval=0.6
        )
        
def movimento_batedor_petran_lvl1_earths():
    delay_cait = 0.7

    def clica_loot_timer():
        clica_loot()
        random_sleep(0.1,0.1)

    def andar():

        sequence_salinha_dragoes = [
            ('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),('CLICK',0.1),
            ('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),('CLICK',0.1),('RIGHT',delay_cait),('CLICK',0.1),
            ('LEFT',delay_cait),('CLICK',0.1),('LEFT',delay_cait),('CLICK',0.1),('LEFT',delay_cait),('CLICK',0.1),('LEFT',delay_cait),('CLICK',0.1),
            ('LEFT',delay_cait),('CLICK',0.1),('LEFT',delay_cait),('CLICK',0.1),('LEFT',delay_cait),('CLICK',0.1),('LEFT',delay_cait),('CLICK',0.1),
        ]  # Sequência de movimentos


        for move,delay in sequence_salinha_dragoes:
            pressiona_botao(movements[move], delay_ini=delay)
            #time.sleep(delay_cait)
            clica_loot_timer()
            random_sleep(0.7,1)

    while True:
        #RESETAR

        andar()
        for x in range(6):
            clica_loot_timer()
        #random_sleep(1*60, 2*60)
        for x in range(6):
            clica_loot_timer()
        perform_random_movements_with_breaks(
            num_movements=3, 
            delay=0.3, 
            pause_duration=0, 
            pause_interval=0.6
        )
        