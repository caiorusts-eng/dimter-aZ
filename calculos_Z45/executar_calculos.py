import math
from .calculos_ESC.calculos_enrijecedor import calcular_enrijecedor as calcular_enrijecedor_esc
from .calculos_ESC.calculos_mesa import calcular_mesa as calcular_mesa_esc
from .calculos_ESC.calculos_alma import calcular_alma as calcular_alma_esc
from .calculos_FLT.calculos_enrijecedor import calcular_enrijecedor as calcular_enrijecedor_flt
from .calculos_FLT.calculos_mesa import calcular_mesa as calcular_mesa_flt
from .calculos_FLT.calculos_alma import calcular_alma as calcular_alma_flt
from .calculos_FLT.calculo_fy_flt import calcular_fy_flt
from .calculosY_FLT.calculo_fy_y_flt import calcular_fy_y_flt
from .calculosY_ESC.calculos_enrijecedor import calcular_enrijecedor as calcular_enrijecedor_y_esc
from .calculosY_ESC.calculos_mesa import calcular_mesa as calcular_mesa_y_esc
from .calculosY_ESC.calculos_alma import calcular_alma as calcular_alma_y_esc
from .calculosY_FLT.calculos_enrijecedor import calcular_enrijecedor as calcular_enrijecedor_y_flt
from .calculosY_FLT.calculos_mesa import calcular_mesa as calcular_mesa_y_flt
from .calculosY_FLT.calculos_alma import calcular_alma as calcular_alma_y_flt
from .calculos_dist.calculos_dist import calcular_dist as calcular_dist_x
from .calculosY_dist.calculosY_dist import calcularY_dist as calcular_dist_Y
from .calculos_comp.calculos_sigma import calcular_sigma  
from .calculos_comp.calculos_enrijecedor import calcular_c_enrijecedor  
from .calculos_comp.calculos_mesa import calcular_c_mesa  
from .calculos_comp.calculos_alma import calcular_c_alma  


def executar_calculos(perfil, fy, Lx, Ly, Lz, Cb, c, debug=False):
    # --- ESC eixo X ---
    yg1_esc = calcular_enrijecedor_esc(perfil, fy)
    mesa_esc = calcular_mesa_esc(perfil, fy, yg1_esc)
    alma_esc = calcular_alma_esc(perfil, fy, mesa_esc.get("yg2", 0), mesa_esc.get("Aef2", 0))
    ixret_esc = mesa_esc.get("ixret2", 0) + alma_esc.get("ixret3", 0)
    ixef_esc = perfil["Ix"] - ixret_esc
    Wxef_esc = ixef_esc / alma_esc.get("yg3", 1)
    Mrd_x_esc = (Wxef_esc * fy) / 1.1

    # --- ESC eixo Y ---
    xg0_y_esc = calcular_enrijecedor_y_esc(perfil, fy)["xg0"]
    xg1_y_esc = calcular_enrijecedor_y_esc(perfil, fy)["xg1"]
    mesa_y_esc = calcular_mesa_y_esc(perfil, fy, xg1_y_esc)
    alma_y_esc = calcular_alma_y_esc(
        perfil, fy,
        mesa_y_esc.get("xg2", 0),
        mesa_y_esc.get("Aef2", 0),
        mesa_y_esc.get("lret1", 0),
        mesa_y_esc.get("def_efetiva", 0)
    )
    iyret_esc = mesa_y_esc.get("iyret2", 0) + alma_y_esc.get("iyret3", 0)
    Iyef_esc = perfil["Iy"] - iyret_esc
    Wyef_esc = Iyef_esc / alma_y_esc.get("xg3", 1)
    Mrd_y_esc = (Wyef_esc * fy) / 1.1

    # --- FLT eixo X ---
    fy_flt = calcular_fy_flt(perfil, fy, Ly, Lz, Cb)
    yg1_flt = calcular_enrijecedor_flt(perfil, fy_flt)
    mesa_flt = calcular_mesa_flt(perfil, fy_flt, yg1_flt)
    alma_flt = calcular_alma_flt(perfil, fy_flt, mesa_flt.get("yg2", 0), mesa_flt.get("Aef2", 0))
    ixret_flt = mesa_flt.get("ixret2", 0) + alma_flt.get("ixret3", 0)
    ixef_flt = perfil["Ix"] - ixret_flt
    Wxef_flt = ixef_flt / alma_flt.get("yg3", 1)
    Mrd_x_flt = (Wxef_flt * fy_flt) / 1.1

    # --- FLT eixo Y ---
    fy_y_flt = calcular_fy_y_flt(perfil, fy, Lx, Lz)["fy_y_flt"]
    xg1_y_flt = calcular_enrijecedor_y_flt(perfil, fy_y_flt)["xg1"]
    mesa_y_flt = calcular_mesa_y_flt(perfil, fy_y_flt, xg1_y_flt)
    alma_y_flt = calcular_alma_y_flt(
        perfil, fy_y_flt,
        mesa_y_flt.get("xg2", 0),
        mesa_y_flt.get("Aef2", 0),
        mesa_y_flt.get("lret1", 0),
        mesa_y_flt.get("def_efetiva", 0)
    )
    iyret_flt = mesa_y_flt.get("iyret2", 0) + alma_y_flt.get("iyret3", 0)
    Iyef_flt = perfil["Iy"] - iyret_flt
    Wyef_flt = Iyef_flt / alma_y_flt.get("xg3", 1)
    Mrd_y_flt = (Wyef_flt * fy_y_flt) / 1.1

    # --- DIST eixo X e Y ---
    Mrd_x_dist = calcular_dist_x(perfil, fy)
    Mrd_y_dist = calcular_dist_Y(perfil, fy)

    # --- Compressão ---
    sigma = calcular_sigma(perfil, fy, Lx, Ly, Lz)["sigma"]
    enrijecedor_comp = calcular_c_enrijecedor(perfil, sigma)
    mesa_comp = calcular_c_mesa(perfil, sigma)
    alma_comp = calcular_c_alma(perfil, sigma, mesa_comp["Aef2"])
    Nc_rd = (sigma * alma_comp["Aef3"]) / 1.2

    # --- Definições geométricas ---
    try:
        bw = perfil["bw"]
        t = perfil["t"]
        h = bw - 4 * t
    except KeyError as e:
        print(f"Erro: {e} não encontrado no dicionário 'perfil'.")
        bw, t, h = 0, 0, 0

    # --- Web Crippling ---
    Fwrd_ext, Fwrd_int = 0.0, 0.0
    try:
        ri = perfil.get("ri", 2 * t)
        cond1 = (h / t) < 200 if t > 0 else False
        cond2 = (c / t) < 210 if t > 0 else False
        cond3 = (c / h) < 20 if h > 0 else False
        cond4 = (ri / t) < 9 if t > 0 else False

        if all([cond1, cond2, cond3, cond4]):
            Fwrd_ext = (4.6 * (t**2) * fy *
                        (1 - 0.14 * math.sqrt(ri / t)) *
                        (1 + 0.35 * math.sqrt(c / t)) *
                        (1 - 0.02 * math.sqrt(h / t))) / 1.35
            Fwrd_int = (15.8 * (t**2) * fy *
                        (1 - 0.23 * math.sqrt(ri / t)) *
                        (1 + 0.14 * math.sqrt(c / t)) *
                        (1 - 0.01 * math.sqrt(h / t))) / 1.35
    except Exception as e:
        print(f"Erro no cálculo de Web Crippling: {e}")

    # --- Força cortante ---
    Vrd, regime, kv = 0.0, "N/A", 0.0
    try:
        if h > 0 and t > 0:
            kv=5

            λ = h / t
            lim_inf = 1.08 * math.sqrt(20000 * kv / fy)
            lim_sup = 1.4 * math.sqrt(20000 * kv / fy)

            if λ <= lim_inf:
                regime = "Compacta"
                Vrd = 0.6 * fy * h * t / 1.1
            elif lim_inf < λ <= lim_sup:
                regime = "Intermediária"
                Vrd = 0.65 * t**2 * math.sqrt(kv * fy * 20000) / 1.1
            else:
                regime = "Esbelta"
                Vrd = (0.905 * 20000 * kv * t**3 / h) / 1.1
    except Exception as e:
        print(f"Erro no cálculo de cortante: {e}")

    # --- Tração ---
    try:
        A = perfil["A"]
        Ntrd = A * fy / 1.1
    except Exception as e:
        print(f"Erro no cálculo de Tração: {e}")
        Ntrd = 0.0

    # --- Retorno geral ---
    return {
        "Mrd_x_esc": Mrd_x_esc,
        "Mrd_y_esc": Mrd_y_esc,
        "Mrd_x_flt": Mrd_x_flt,
        "Mrd_y_flt": Mrd_y_flt,
        "Mrd_x_dist": Mrd_x_dist,
        "Mrd_y_dist": Mrd_y_dist,
        "Ncrd": Nc_rd,
        "Vrd": Vrd,
        "Fwrd_ext": Fwrd_ext,
        "Fwrd_int": Fwrd_int,
        "Regime_cortante": regime,
        "kv": kv,
        "Ntrd": Ntrd
    }
