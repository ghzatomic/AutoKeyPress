from controla.controles import *



def movimento_batedor_petran_lvl2_dragoes_arco():
    delay_cait = 0.7

    def clica_loot_timer():
        clica_loot()
        random_sleep(0.1,0.1)

    def andar():

        sequence_salinha_dragoes = [
            ('DIAGONAL_CIMA_DIREITA',delay_cait),('DIAGONAL_CIMA_DIREITA',delay_cait),('DIAGONAL_CIMA_DIREITA',delay_cait),('DIAGONAL_CIMA_DIREITA',delay_cait),
            ('DIAGONAL_CIMA_DIREITA',delay_cait),('DIAGONAL_CIMA_DIREITA',delay_cait),('DIAGONAL_CIMA_DIREITA',delay_cait),('DIAGONAL_CIMA_DIREITA',delay_cait),
            ('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),
            ('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),('DIAGONAL_CIMA_ESQUERDA',delay_cait),
            ('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),
            ('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),('DIAGONAL_BAIXO_ESQUERDA',delay_cait),
            ('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),
            ('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),('DIAGONAL_BAIXO_DIREITA',delay_cait),
        ]  # Sequência de movimentos

        sequence = [
            ('DOWN',delay_cait),('DOWN',delay_cait),('DOWN',delay_cait),('DOWN',delay_cait),
            ('DOWN',delay_cait),('DOWN',delay_cait),('DOWN',delay_cait),('DOWN',delay_cait),
            ('UP',delay_cait),('UP',delay_cait),('UP',delay_cait),('UP',delay_cait),
            ('UP',delay_cait),('UP',delay_cait),('UP',delay_cait),('UP',delay_cait),

        ]

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