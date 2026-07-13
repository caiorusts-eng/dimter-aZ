import math

def calcular_alma(perfil, fy, xg2, Aef2):
    """Calcula as propriedades efetivas da alma no método ESC."""

    D = perfil["D"]
    bf = perfil["bf"]
    bw = perfil["bw"]
    t = perfil["t"]

    # 📌 Cálculo das propriedades iniciais da seção
    d = D - 2 * t
    bf = bf - 4 * t
    bw = bw - 4 * t
    xg0 = xg2  # 🔹 Agora usamos `xg2` vindo do enrijecedor

    # 📌 Verificar se `Aef2` é None antes de continuar
    if Aef2 is None:
        raise ValueError("Erro: Aef2 está indefinido (None). Verifique o cálculo da mesa.")

    # 📌 Cálculo da alma efetiva
    xg0_inicial = (bf + 4 * t) - (t / 2)

    if xg0 == xg0_inicial:
        sigma_a = t * fy / (4*xg0_inicial)
    else:
        sigma_a = fy * (xg0 - xg0_inicial) / xg0

    # 📌 Cálculo do coeficiente de esbeltez
    k = 4
    lambda_val = bw / t
    lambda_p = lambda_val / (0.95 * math.sqrt(k * 20000 / sigma_a))  # 🔹 Corrigido

    # 📌 Cálculo da largura efetiva `bc_ef`
    if lambda_p < 0.673:
        bc_ef = bw
    else:
        bc_ef = bw * (1 - (0.22 / lambda_p)) * (1 / lambda_p)

    # 📌 Cálculo das áreas reduzidas e centróides
    lret3 = bw - bc_ef
    Aret3 = t * lret3
    Aef3 = Aef2 - Aret3
    d3 = xg2 - (bf + 3.5 * t)

    # 📌 Cálculo de x3 e do novo centróide xg3
    x3 = (d3 * Aret3) / Aef3 if Aef3 != 0 else 0
    xg3 = xg2 + x3

    # 📌 Cálculo do momento de inércia da alma efetiva
    iyret3 = ((lret3 * t**3) / 12) + (Aret3 * (d3**2))

    return {
        "sigma" : sigma_a,
        "lambda" : lambda_p,
        "xg0": xg0,
        "lret3": lret3,
        "Aret3": Aret3,
        "Aef3": Aef3,
        "d3": d3,
        "x3": x3,
        "xg3": xg3,
        "iyret3": iyret3
    }
