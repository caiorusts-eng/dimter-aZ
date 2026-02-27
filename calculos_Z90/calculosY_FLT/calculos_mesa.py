import math

def calcular_mesa(perfil, fy_y_flt, xg1):
    """Calcula as propriedades efetivas da mesa no método FLT."""

    D = perfil["D"]
    bf = perfil["bf"]
    bw = perfil["bw"]
    t = perfil["t"]

    # 📌 Inicializando variáveis para evitar erros
    xg2 = xg1  # ✅ Garante que `xg2` tenha um valor inicial
    iyret1 = 0  # ✅ Inicializa `iyret1` para evitar problemas de None
    iyret2 = 0  # ✅ Inicializa `iyret2` para evitar problemas de None

    # 📌 Cálculo das propriedades iniciais da seção
    d = D - 2 * t
    bf = bf - 4 * t
    bw = bw - 4 * t
    xg0 = xg1  # 🔹 Agora usamos `xg1` vindo do enrijecedor

    # 📌 Cálculo de lambda
    sigma_1 = (xg0 - 2 * t) * fy_y_flt / xg0 if xg0 != 0 else 0  # ✅ Evita divisão por zero
    lambda_val = bf / t
    lambda_p0 = lambda_val / (0.623 * math.sqrt(20000 / sigma_1)) if sigma_1 > 0 else 0  # ✅ Evita raiz negativa

    # 📌 Definir variáveis para evitar erros
    Is, Ia, lambda_p, bef, def_efetiva,razao_ii,n,k = None, None, None, None, None, None, None, None  
    Aef2 = perfil["A"]  

    if lambda_p0 < 0.673:
        bef = bf
        def_efetiva = d
    else:
        # 📌 Cálculo de Ia e Is
        Ia = min((399 * (t ** 4) * (((0.487 * lambda_p0) - 0.328) ** 3)), (t ** 4 * (56 * lambda_p0 + 5)))
        Is = (t * (d ** 3)) / 12

        # 📌 Cálculo de n e razão i/i
        n = max((0.582 - 0.122 * lambda_p0), (1 / 3))
        razao_ii = min((Is / Ia), 1) if Ia and Is else 0  # ✅ Evita erro se `Ia` ou `Is` forem `None`

        # 📌 Cálculo do fator k
        D_bf_ratio = D / bf
        if D_bf_ratio <= 0.25:
            k = min((3.57 * (razao_ii ** n) + 0.43), 4)
        elif 0.25 < D_bf_ratio < 0.8:
            k = min(((4.82 - 5 * D_bf_ratio) * (razao_ii ** n) + 0.43), 4)
        else:
            k = 4  

        lambda_p = lambda_val / (0.95 * math.sqrt(k * 20000 / sigma_1)) if sigma_1 > 0 else 0  # ✅ Evita raiz negativa

        if lambda_p < 0.673:
            bef = bf
            # 📌 Cálculo do enrijecedor efetivo
            def_efetiva = razao_ii * d
            lret1 = d - def_efetiva
            Aret1 = t * lret1
            Aef1 = perfil["A"] - Aret1
            d1 = xg0 - (t / 2)
            x1 = (d1 * Aret1) / Aef1 if Aef1 != 0 else 0
            xg1 = xg0 + x1  # ✅ `xg2` recebe valor aqui
            iyret2 = ((lret1 * (t ** 3)) / 12) + (Aret1 * (d1 ** 2))
            xg2=xg1
        else:
            # 📌 Cálculo do enrijecedor efetivo
            def_efetiva = (d * (1 - (0.22 / lambda_p)) * (1 / lambda_p)) * razao_ii
            lret1 = d - def_efetiva
            Aret1 = t * lret1
            Aef1 = perfil["A"] - Aret1
            d1 = xg0 - (t / 2)
            x1 = (d1 * Aret1) / Aef1 if Aef1 != 0 else 0
            xg1 = xg0 + x1  # ✅ `xg2` recebe valor aqui
            iyret1 = ((lret1 * (t ** 3)) / 12) + (Aret1 * (d1 ** 2))

            # 📌 Cálculo da mesa efetiva
            bef = bf * (1 - (0.22 / lambda_p)) * (1 / lambda_p)
            bef1 = razao_ii * (bef / 2)
            bef2 = bef - bef1
            lret2 = bf - bef
            Aret2 = t * lret2
            Aef2 = Aef1 - Aret2  
            d2 = xg1 - (lret2 / 2) - bef1 - (2 * t)
            x2 = (d2 * Aret2) / Aef2 if Aef2 != 0 else 0
            xg2 = xg1 + x2  # ✅ `xg2` atualizado novamente
            iyret2 = iyret1 + ((t * (lret2 ** 3)) / 12) + (Aret2 * (d2 ** 2))

    return {
        "Is/Ia": razao_ii,
        "n": n,
        "lambdap0": lambda_p0,
        "sigma": sigma_1,
        "lambda": lambda_val,
        "Is": Is,
        "Ia": Ia,
        "k": k,
        "lambda_p": lambda_p,
        "bef": bef,
        "def_efetiva": def_efetiva,
        "xg2": xg2,  # ✅ Agora `xg2` sempre terá um valor
        "Aef2": Aef2,
        "iyret1": iyret1,  # ✅ Nome corrigido para clareza
        "iyret2": iyret2  # ✅ Agora sempre terá um valor válido
    }
