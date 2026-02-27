import math

def calcular_c_mesa(perfil, sigma):
    """Calcula as propriedades da mesa para compressão."""

    D = perfil["D"]
    bf = perfil["bf"]
    bw = perfil["bw"]
    t = perfil["t"]
    A = perfil["A"]

    # 📌 Cálculo das dimensões da seção
    d = D - (2 * t * math.tan(math.radians(45/2)))
    bf = bf - 2 * t - 2*t*math.tan(math.radians(45/2))
    bw = bw - 4 * t
    lambda_val = bf/t

    # 📌 Cálculo de lambda_p0
    lambda_p0 = lambda_val / (0.623*math.sqrt(20000/sigma))
    
    # 📌 Definir variáveis para evitar erros
    Is, Ia, lambda_p, bef, razao_ii,n,k = None, None, None, None, None, None, None
   
    if lambda_p0 < 0.673:
        bef = bf
        def_efetiva = d
    else:
        # 📌 Cálculo de Ia e Is
        Ia = min((399 * (t ** 4) * (((0.487 * lambda_p0) - 0.328) ** 3)), (t ** 4 * (56 * lambda_p0 + 5)))
        Is = (t * (d ** 3)*(math.sin(math.radians(45))**2)) / 12

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

        lambda_p = lambda_val / (0.95 * math.sqrt(k * 20000 / sigma)) if sigma > 0 else 0  # ✅ Evita raiz negativa
        if lambda_p < 0.673:
            bef = bf
            def_efetiva = d
        else:
         bef = bf * (1 - (0.22 / lambda_p)) * (1 / lambda_p)
         def_efetiva = (d * (1 - (0.22 / lambda_p)) * (1 / lambda_p)) * razao_ii

    Lret2 = float((bf-bef) + (d-def_efetiva))
    Aret2 = Lret2 * t
    Aef2 = A - Aret2

    return{
    "Aef2": Aef2
    }


