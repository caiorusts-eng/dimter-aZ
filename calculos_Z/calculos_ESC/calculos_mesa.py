import math

def calcular_mesa(fy, t, perfil_z):
    bf = perfil_z["bf"]
    xg0 = perfil_z["yg0"]
    A = perfil_z["A"]

    # 📌 Inicialização
    iyret1 = 0
    Aef1 = A
    lret1 = 0
    Aret1 = 0

    # 📌 Cálculo de lambda    
    lambda_val = bf / t
    k = 0.43
    lambda_p = lambda_val / (0.95 * math.sqrt(k * 20000 / fy))

    if lambda_p < 0.673:
        bef = bf
        xg1 = xg0
    else:
        # 📌 Redução da mesa
        bef = bf * (1 - (0.22 / lambda_p)) * (1 / lambda_p)
        lret1 = bf - bef
        Aret1 = t * lret1
        Aef1 = A - Aret1
        d1 = xg0 - (t / 2)
        x1 = (d1 * Aret1) / Aef1 if Aef1 != 0 else 0
        xg1 = xg0 + x1
        iyret1 = ((lret1 * t**3) / 12) + (Aret1 * d1**2)

    return {
        "lambda_p": lambda_p,
        "bef": bef,
        "yg1": xg1,
        "Aef1": Aef1,
        "iyret1": iyret1,
        "lret1": lret1,
        "Aret1": Aret1
    }
