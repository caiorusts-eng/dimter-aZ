import math

def calcular_alma(perfil, fy, yg2, Aef2):
    """Calcula as propriedades efetivas da alma no método ESC."""
    
    D = perfil["D"]
    bf = perfil["bf"]
    bw = perfil["bw"]
    t = perfil["t"]

    # 📌 Cálculo das propriedades iniciais
    d = D - (2 * t * math.tan(math.radians(45/2)))
    bf = bf - 2 * t - 2*t*math.tan(math.radians(45/2))
    bw = bw - 4 * t
    yg0 = yg2  # 🔹 Agora usamos `yg2` vindo da mesa

    # 📌 Verificar se `Aef2` é None antes de continuar
    if Aef2 is None:
        raise ValueError("Erro: Aef2 está indefinido (None). Verifique o cálculo da mesa.")

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
        lret3 = bc - Σbc_efetiva
        Aret3 = t * lret3
        Aef3 = Aef2 - Aret3  # 🔹 Agora Aef2 nunca será None, pois verificamos antes

        d3 = bc2_efetiva + (lret3 / 2)  # 🔹 Agora `bc2_efetiva` sempre tem um valor
        y3 = (d3 * Aret3) / Aef3 if Aef3 != 0 else 0
        yg3 = yg2 + y3

        # 📌 Verificar critério de parada
        diferenca_yg = abs(yg3 - yg_anterior)
        yg_anterior = yg3  # Atualizar yg para próxima iteração

    # 📌 Cálculo de ixret3 após convergência ou no máximo de iterações
    ixret3 = ((t * (lret3 ** 3)) / 12) + (Aret3 * (d3 ** 2))

    return {
        "Aef3": Aef3,
        "ixret3": ixret3,
        "yg3": yg3,
        "Nº de interações necessárias": iteracoes,
    }
