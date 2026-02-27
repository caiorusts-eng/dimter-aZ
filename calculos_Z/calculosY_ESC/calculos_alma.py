import math

def calcular_alma(perfil_z, fy, t, xg1, bef, Aef1, x1):
    """Calcula as propriedades efetivas da alma no método ESC."""

    bf = perfil_z["bf"]
    bw = perfil_z["bw"]
    xg0 = xg1  # 🔹 Agora usamos xg1 vindo do enrijecedor

    # 📌 Verificar se `Aef2` é None antes de continuar
    if Aef1 is None:
        raise ValueError("Erro: Aef2 está indefinido (None). Verifique o cálculo da mesa.")

    # 📌 Cálculo da alma efetiva
    xg0_inicial = (bf + 2 * t) - (t / 2)

    if xg0 == xg0_inicial:
        sigma_a = t * fy / (4*xg0_inicial)
    else:
        sigma_a = fy * (xg0 - (bef+2*t)) / xg0

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
    lret2 = bw - bc_ef
    Aret2 = t * lret2
    Aef2 = Aef1 - Aret2
    d2 = x1 

    # 📌 Cálculo de x3 e do novo centróide xg3
    x2 = (d2 * Aret2) / Aef2 if Aef2 != 0 else 0
    xg2 = xg0 + x2

    # 📌 Cálculo do momento de inércia da alma efetiva
    iyret2 = ((lret2 * t**3) / 12) + (Aret2 * (d2**2))

    return {
        "sigma" : sigma_a,
        "lambda" : lambda_p,
        "xg0": xg0,
        "lret2": lret2,
        "Aret2": Aret2,
        "Aef2": Aef2,
        "d2": d2,
        "x2": x2,
        "xg2": xg2,
        "iyret2": iyret2
    }
