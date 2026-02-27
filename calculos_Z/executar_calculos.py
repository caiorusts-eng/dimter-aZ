import math
from .z_prop import calcular_zprop as calcular_zprop
from .calculos_ESC.calculos_mesa import calcular_mesa as calcular_mesa_esc
from .calculos_ESC.calculos_alma import calcular_alma as calcular_alma_esc
from .calculos_FLT.calculos_mesa import calcular_mesa as calcular_mesa_flt
from .calculos_FLT.calculos_alma import calcular_alma as calcular_alma_flt
from .calculos_FLT.calculo_fy_flt import calcular_fy_flt
from .calculosY_FLT.calculo_fy_y_flt import calcular_fy_y_flt
from .calculosY_ESC.calculos_mesa import calcular_mesa as calcular_mesa_y_esc
from .calculosY_ESC.calculos_alma import calcular_alma as calcular_alma_y_esc
from .calculosY_FLT.calculos_mesa import calcular_mesa as calcular_mesa_y_flt
from .calculosY_FLT.calculos_alma import calcular_alma as calcular_alma_y_flt
from .calculos_comp.calculos_sigma import calcular_sigma  
from .calculos_comp.calculos_mesa import calcular_c_mesa  
from .calculos_comp.calculos_alma import calcular_c_alma  


def executar_calculos(bf, bw, t, fy, Lx, Ly, Lz, Cb, c, debug=False):

    Cb = Cb
    c=c

    # Cálculo ESC eixo X
    perfil_z = calcular_zprop(t, bf, bw)
    mesa_esc = calcular_mesa_esc(fy, t, perfil_z)
    alma_esc = calcular_alma_esc(mesa_esc.get("yg1", 0), mesa_esc.get("Aef1", 0), fy, t , perfil_z)
    ixret_esc = mesa_esc.get("ixret1", 0) + alma_esc.get("ixret2", 0)
    ixef_esc = perfil_z["Ix"] - ixret_esc
    Wxef_esc = ixef_esc / alma_esc.get("yg2", 1)
    Mrd_x_esc = (Wxef_esc * fy) / 1.1

    # FLT eixo X
    fy_flt = calcular_fy_flt(perfil_z, fy, Ly, Lz, Cb)
    mesa_flt = calcular_mesa_flt(fy_flt, t, perfil_z)
    alma_flt = calcular_alma_flt(mesa_flt.get("yg1", 0), mesa_flt.get("Aef1", 0), fy_flt, t, perfil_z )
    ixret_flt = mesa_flt.get("ixret1", 0) + alma_flt.get("ixret2", 0)
    ixef_flt = perfil_z["Ix"] - ixret_flt
    Wxef_flt = ixef_flt / alma_flt.get("yg2", 1)
    Mrd_x_flt = (Wxef_flt * fy_flt) / 1.1

    # Cálculo ESC eixo Y
    mesa_y_esc = calcular_mesa_y_esc(perfil_z, t, fy)
    alma_y_esc = calcular_alma_y_esc(perfil_z, fy, t, mesa_y_esc.get("xg1", 0), mesa_y_esc.get("bef", 0), mesa_y_esc.get("Aef1", 0), mesa_y_esc.get("x1", 0))
    iyret_esc = mesa_y_esc.get("iyret1", 0) + alma_y_esc.get("iyret2", 0)
    Iyef_esc = perfil_z["Iy"] - iyret_esc
    Wyef_esc = Iyef_esc / alma_y_esc.get("xg2", 1)
    Mrd_y_esc = (Wyef_esc * fy) / 1.1

    # Cálculo FLT eixo Y
    mesa_y_flt = calcular_mesa_y_flt(perfil_z, t, fy)
    alma_y_flt = calcular_alma_y_flt(perfil_z, fy, t, mesa_y_flt.get("xg1", 0), mesa_y_flt.get("bef", 0), mesa_y_flt.get("Aef1", 0), mesa_y_flt.get("x1", 0))
    iyret_flt = mesa_y_flt.get("iyret1", 0) + alma_y_flt.get("iyret2", 0)
    Iyef_flt = perfil_z["Iy"] - iyret_flt
    Wyef_flt = Iyef_flt / alma_y_flt.get("xg2", 1)
    Mrd_y_flt = (Wyef_flt * fy) / 1.1

    # Web crippling
    try:
        bw = perfil_z["bw"]
        t = perfil_z["t"]
        ri = 2*t
        h = bw - 4 * t

        # Requisitos
        cond1 = h / t < 200
        cond2 = c / t < 210
        cond3 = c / h < 20
        cond4 = ri / t < 9

        if all([cond1, cond2, cond3, cond4]): #GPT, SOFREU ALTERAÇÃO
            Fwrd_ext = (4.6* (t**2)* fy * (1 - 0.14 * math.sqrt(ri / t))* (1 + 0.35 * math.sqrt(c / t)) * (1 - 0.02 * math.sqrt(h / t)))/1.35
            Fwrd_int = (15.8* (t**2)* fy * (1 - 0.23 * math.sqrt(ri / t))* (1 + 0.14 * math.sqrt(c / t)) * (1 - 0.01 * math.sqrt(h / t)))/1.35
        else:
            Fwrd_ext, Fwrd_int = None, None  # Condições não atendidas; #GPT, SOFREU ALTERAÇÃO

    except Exception as e:
        print(f"Erro no cálculo de Web Crippling: {e}")
        Fwrd_ext = None

    # Compressão 
    sigma = calcular_sigma(perfil_z, fy, Lx, Ly, Lz)["sigma"]
    mesa_comp = calcular_c_mesa(perfil_z, sigma)
    alma_comp = calcular_c_alma(perfil_z, sigma, mesa_comp["Aef1"])
    Nc_rd = (sigma * alma_comp["Aef2"]) / 1.200

    # --- Força Cortante --- 
    
    try:
        # Kv
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
        Vrd = None
        regime = None

    # --- Tração ---

    A= perfil_z["A"] #GPT, COLHER "A" DE perfil_z CORRETAMENTE
    Ntrd = A * fy / 1.1 #Escoamento da seção bruta


# 🔹 Debug opcional
    if debug:
        print("\n=== DEBUG ESC eixo Y ===")
        print("xg1:", mesa_y_esc.get("xg1"))
        print("bef:", mesa_y_esc.get("bef"))
        print("Aef1:", mesa_y_esc.get("Aef1"))
        print("iyret1:", mesa_y_esc.get("iyret1"))
        print("iyret2:", alma_y_esc.get("iyret2"))
        print("Iyef_esc:", Iyef_esc)
        print("xg2:", alma_y_esc.get("xg2"))
        print("Wyef_esc:", Wyef_esc)
        print("Mrd_y_esc:", Mrd_y_esc)

    # --- Retorno geral ---
    return {
        "Mrd_x_esc": Mrd_x_esc,
        "Mrd_y_esc": Mrd_y_esc,
        "Mrd_x_flt": Mrd_x_flt,
        "Mrd_y_flt": Mrd_y_flt,
        "Ncrd": Nc_rd,
        "Fwrd_ext": Fwrd_ext,
        "Fwrd_int": Fwrd_int,
        "Vrd": Vrd,
        "Ntrd" : Ntrd
    }
