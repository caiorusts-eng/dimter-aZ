import math

def calcular_alma(yg1, Aef1, fy, t, perfil_z):

    bw = perfil_z["bw"]
    yg0 = perfil_z["yg0"]

    
    yg0 = yg1  # 🔹 Agora usamos `yg1` vindo da mesa

    # 📌 Verificar se `Aef1` é None antes de continuar
    if Aef1 is None:
        raise ValueError("Erro: Aef1 está indefinido (None). Verifique o cálculo da mesa.")

    # 📌 Inicializando variáveis para o loop iterativo
    iteracoes = 0
    diferenca_yg = 1  # Valor alto inicial para garantir que o loop rode ao menos uma vez
    precisao = 0.01  # Critério de convergência
    yg_anterior = yg0
    max_iteracoes = 10  # 🔹 Limite máximo de iterações

    while diferenca_yg > precisao and iteracoes < max_iteracoes:
        iteracoes += 1  # Contador de iterações

        # 📌 Atualização de `bc` a cada iteração
        bc = yg_anterior - 2 * t  # 🔹 Agora `bc` depende do `yg_anterior`

        # 📌 Cálculo da largura efetiva da alma (iteração)
        lambda_h = bw / t
        sigma_e1 = bc * fy / yg_anterior
        sigma_e2 = (bw - bc) * fy / yg_anterior
        psi = -sigma_e2 / sigma_e1 if sigma_e1 != 0 else 0
        k = 4 + 2 * (1 - psi) + 2 * ((1 - psi) ** 3)

        # 📌 🔹 Garantimos que k * 20000 / sigma_e1 nunca seja negativo
        denominador = k * 20000 / sigma_e1 if sigma_e1 > 0 else 1e-6  # Evita divisão por zero
        lambda_ph = lambda_h / (0.95 * math.sqrt(denominador)) if denominador > 0 else 0

        # 📌 🔹 Inicializamos `Σbc_efetiva` e `bc2_efetiva` como `bc`, garantindo que sempre tenham valores
        Σbc_efetiva = bc  
        bc2_efetiva = bc  # 🔹 Garantir que `bc2_efetiva` tenha um valor padrão antes da condicional

        if lambda_ph < 0.673:
            bc_efetiva = bc
        else:
            bc_efetiva = bc * (1 - (0.22 / lambda_ph)) * (1 / lambda_ph)
            bc1_efetiva = bc_efetiva / (3 - psi)
            bc2_efetiva = bc_efetiva / 2  # 🔹 Agora sempre será definido
            Σbc_efetiva = bc1_efetiva + bc2_efetiva if (bc1_efetiva + bc2_efetiva) < bc else bc

        # 📌 Cálculo do centroide yg3
        lret2 = bc - Σbc_efetiva
        Aret2 = t * lret2
        Aef2 = Aef1 - Aret2  # 🔹 Agora Aef2 nunca será None, pois verificamos antes

        d2 = bc2_efetiva + (lret2 / 2)  # 🔹 Agora `bc2_efetiva` sempre tem um valor
        y2 = (d2 * Aret2) / Aef2 if Aef2 != 0 else 0
        yg2 = yg1 + y2

        # 📌 Verificar critério de parada
        diferenca_yg = abs(yg2 - yg_anterior)
        yg_anterior = yg2  # Atualizar yg para próxima iteração

    # 📌 Cálculo de ixret3 após convergência ou no máximo de iterações
    ixret2 = ((t * (lret2 ** 3)) / 12) + (Aret2 * (d2 ** 2))

    return {
        "Aef2": Aef2,
        "ixret2": ixret2,
        "yg2": yg2,
        "Nº de interações necessárias": iteracoes,
    }
