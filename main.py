import importlib
from perfis import buscar_perfil, perfis_z90, perfis_z45
from calculos_solicitante.calculos_solicitante import calcular_solicitante
from tabulate import tabulate
import math # Importado para math.isclose

def main():
    print("\n📌 Perfis disponíveis para seleção:")
    perfis_disponiveis = [
        "Z90 150x60x20x2.00", "Z90 150x60x20x4.75",
        "Z90 200x75x20x2.00", "Z90 200x75x30x6.30",
        "Z90 250x85x25x2.00", "Z90 250x85x25x4.75",
        "Z90 300x85x25x2.00", "Z90 300x85x30x6.30",
        "Z45 150x60x20x2.00", "Z45 150x60x20x4.75",
        "Z45 200x75x20x2.00", "Z45 200x75x30x6.30",
        "Z45 250x85x25x2.00", "Z45 250x85x25x4.75",
        "Z45 300x85x25x2.00", "Z45 300x85x30x6.30"
    ]

    for perfil in perfis_disponiveis:
        print(f"    - {perfil}")

    # --- Escolha de perfil customizado ou catálogo ---
    print("\nDeseja verificar um perfil Z customizado?")
    print(" [1] Sim")
    print(" [2] Não (Usar catálogo)")
    custom = input("Sua opção: ").strip()

    print("\nDeseja ativar o modo debug? (mostrar cálculos detalhados)")
    debug = input(" [1] Sim\n [2] Não\nSua opção: ").strip() == "1"

    is_custom = (custom == "1")

    # === PERFIL DO CATÁLOGO ===
    if not is_custom:
        nome_perfil_selecionado = input("\nDigite o nome exato do perfil desejado: ").strip()
        if nome_perfil_selecionado not in perfis_disponiveis:
            print(f"❌ Perfil '{nome_perfil_selecionado}' não encontrado.")
            return

        tipo, nome_perfil = nome_perfil_selecionado.split(" ", 1)
        lista_perfis = perfis_z90 if tipo == "Z90" else perfis_z45
        perfil = buscar_perfil(nome_perfil, lista_perfis)
        if not perfil:
             print(f"❌ Erro ao carregar dados do perfil '{nome_perfil}'.")
             return

    # === PERFIL Z CUSTOMIZADO ===
    else:
        try:
            bf = float(input("\nDigite a largura da mesa (bf) em cm: "))
            bw = float(input("Digite a altura da alma (d) em cm: "))
            t = float(input("Digite a espessura (t) em cm: "))
        except ValueError:
            print("❌ Entrada inválida! Digite números válidos.")
            return

        from calculos_Z.z_prop import calcular_zprop
        perfil = calcular_zprop(t, bf, bw)
        tipo = "Z" # Módulo "calculos_Z" será usado
        nome_perfil_selecionado = f"Z {bw}x{bf}x{t}"

        print("\n📐 Parâmetros geométricos do perfil Z customizado:")
        for chave, valor in perfil.items():
            if isinstance(valor, (int, float)):
                print(f" - {chave}: {valor:.4f}")
            else:
                print(f" - {chave}: {valor}")

    # --- Entrada de dados gerais ---
    fy = float(input("\nTensão de trabalho (fy) em kN/cm²: "))
    Lx = float(input("Distância entre tesouras (cm): "))
    dist_terças = float(input("Distância entre terças (cm): "))
    ang = float(input("Inclinação da cobertura (°): "))
    c = float(input("Largura de contato da tesoura (cm): "))
    metodo = input("\nAnálise: [viga bi-apoiada / viga contínua]: ").strip()

    tirantes = int(input("\nNúmero de tirantes (0–3): "))
    Ly = float(Lx / (tirantes + 1))
    Lz = Ly
    dim_tirante = float(input("Diâmetro dos tirantes (mm, 0 se não houver): ")) if tirantes > 0 else 0
    q_p_chapa = float(input("\nPeso próprio da chapa zincada (kg/m²): ")) / 100
    q_v = float(input("Carga de vento (kN/m²): "))
    print("\nEsforço axial: negativo para COMPRESSÃO, positivo para TRAÇÃO.")
    Ncsd = float(input("Esforço axial de cálculo (kN): ")) # Nome mantido, mas agora é Nsd

    travamento_telha_str = input("\nA telha funciona como travamento da mesa superior? (sim/nao): ").lower().strip()
    telha_trava = (travamento_telha_str == "sim")

    Cb = 1.136 if metodo.lower() == "viga bi-apoiada" else 1.433
    print(f"\nℹ️ Coeficiente Cb adotado: {Cb:.3f}")
    
    is_continua = "contínua" in metodo.lower()

    # --- Cálculo das solicitações ---
    print("\n🔹 Calculando combinações de carga e momentos solicitantes...")

    # Captura os 11 valores de retorno
    Msd_x, Msd_y, q_x, q_y, flecha_x, flecha_y, q_fx, q_fy, Vsd, Fwsd_ext, Fwsd_int = calcular_solicitante(
        metodo, tirantes, Lx, Ly, dist_terças, ang,
        perfil["m"] / 100, q_p_chapa, dim_tirante, q_v,
        perfil["Ix"], perfil["Iy"], debug=debug
    )
    
    if debug and not is_custom: # O debug de solicitante já é impresso dentro da função
        print("\n🧮 Detalhamento das combinações de carga (ELU):")
        print(f"    → q_x = {q_x:.3f} kN/m (longitudinal)")
        print(f"    → q_y = {q_y:.3f} kN/m (transversal)")
        print(f"    → Msd_x = {Msd_x:.3f} kN·cm")
        print(f"    → Msd_y = {Msd_y:.3f} kN·cm")
        print(f"    → Vsd = {Vsd:.3f} kN")
        print(f"    → Fwsd_ext = {Fwsd_ext:.3f} kN")
        print(f"    → Fwsd_int = {Fwsd_int:.3f} kN")


    # --- Cálculo estrutural ---
    print("\n🔹 Executando cálculos estruturais para o perfil...")
    if is_custom:
    # perfis Z simples → a função recebe bf, bw, t individualmente
        modulo = importlib.import_module("calculos_Z.executar_calculos")
        resultados = modulo.executar_calculos(
            perfil["bf"], perfil["bw"], perfil["t"], 
            fy, Lx, Ly, Lz, Cb, c, debug=debug
        )
    else:
    # perfis Z90 e Z45 → recebem o dicionário de propriedades completo
        modulo_nome = f"calculos_{tipo}.executar_calculos"
        modulo = importlib.import_module(modulo_nome)
        # Assumindo que o executar_calculos de Z90/Z45 também foi atualizado
        # para retornar Ntrd, Fwrd_ext, Fwrd_int, etc.
        resultados = modulo.executar_calculos(
            perfil, fy, Lx, Ly, Lz, Cb, c, debug=debug
        )

    # --- Verificação ELS (Flecha) ---
    limite_flecha_x = (Lx / 180) if q_fx < 0 else (Lx / 120)
    limite_flecha_y = (Ly / 180) if q_fy < 0 else (Ly / 120)
    passa_flecha_x = abs(flecha_x) <= limite_flecha_x
    passa_flecha_y = abs(flecha_y) <= limite_flecha_y
    passa_els = "✅" if (passa_flecha_x and passa_flecha_y) else "❌"

    if debug:
        print(f"\n🧩 Detalhes da verificação ELS (Flecha):")
        print(f"  Carga ELS q_fx = {q_fx:.3f} kN/m, Carga ELS q_fy = {q_fy:.3f} kN/m")
        print(f"  Flecha_x: {flecha_x:.3f} cm (Limite: {limite_flecha_x:.3f} cm) -> {'Passa' if passa_flecha_x else 'Falha'}")
        print(f"  Flecha_y: {flecha_y:.3f} cm (Limite: {limite_flecha_y:.3f} cm) -> {'Passa' if passa_flecha_y else 'Falha'}")

    # --- Verificações ELU (Resistência) ---
    
    # Momentos
    mrd_x_esc = resultados.get('Mrd_x_esc', 0)
    mrd_y_esc = resultados.get('Mrd_y_esc', 0)
    passa_x_esc = "✅" if abs(mrd_x_esc) >= abs(Msd_x) else "❌"
    passa_y_esc = "✅" if abs(mrd_y_esc) >= abs(Msd_y) else "❌"

    mrd_x_flt = resultados.get('Mrd_x_flt', 0)
    mrd_y_flt = resultados.get('Mrd_y_flt', 0)
    passa_x_flt = "✅" if abs(mrd_x_flt) >= abs(Msd_x) else "❌"
    passa_y_flt = "✅" if abs(mrd_y_flt) >= abs(Msd_y) else "❌"
    if telha_trava:
        passa_x_flt = "N/A"
        passa_y_flt = "N/A"
        mrd_x_flt = 0.0 # Zera para não poluir a tabela
        mrd_y_flt = 0.0

    mrd_x_dist = resultados.get('Mrd_x_dist', 0)
    mrd_y_dist = resultados.get('Mrd_y_dist', 0)
    passa_x_dist = "✅" if abs(mrd_x_dist) >= abs(Msd_x) else "❌"
    passa_y_dist = "✅" if abs(mrd_y_dist) >= abs(Msd_y) else "❌"
    if is_custom:
        passa_x_dist = "N/A"
        passa_y_dist = "N/A"
        mrd_x_dist = 0.0 # Zera para não poluir a tabela
        mrd_y_dist = 0.0

    # Axial (Compressão ou Tração)
    ncrd = resultados.get('Ncrd', 0)
    ntrd = resultados.get('Ntrd', 0)
    axial_rd = 0.0
    passa_axial = "N/A"
    if Ncsd < 0: # Compressão
        axial_rd = ncrd
        passa_axial = "✅" if abs(ncrd) >= abs(Ncsd) else "❌"
    elif Ncsd > 0: # Tração
        axial_rd = ntrd
        passa_axial = "✅" if abs(ntrd) >= abs(Ncsd) else "❌"
    else: # Esforço nulo
        axial_rd = 0.0
        passa_axial = "✅"

    # Cortante (Vsd vs Vrd)
    vrd = resultados.get('Vrd', 0)
    passa_vrd = "✅" if abs(vrd) >= abs(Vsd) else "❌"

    # Força Concentrada (Web Crippling)
    fwrd_ext = resultados.get('Fwrd_ext', 0)
    fwrd_int = resultados.get('Fwrd_int', 0)
    
    passa_fwrd_ext = "✅" if abs(fwrd_ext) >= abs(Fwsd_ext) else "❌"
    passa_fwrd_int = "N/A" # Padrão
    
    if is_continua:
        passa_fwrd_int = "✅" if abs(fwrd_int) >= abs(Fwsd_int) else "❌"


# --- Tabela de resultados ---
    print(f"\n📊 Resultados Finais para: {nome_perfil_selecionado}")

    # --- Tabela 1: Momentos ---
    linha_momentos = {
        "Verificação": "Momentos (kN·cm)",
        "Solicitante (Sd)": f"Mx: {Msd_x:.2f}\nMy: {Msd_y:.2f}",
        "ESC (Rd)": f"Mx: {mrd_x_esc:.2f} ({passa_x_esc})\nMy: {mrd_y_esc:.2f} ({passa_y_esc})",
    }
    # Adiciona FLT se a telha não trava
    if not telha_trava:
        linha_momentos["FLT (Rd)"] = f"Mx: {mrd_x_flt:.2f} ({passa_x_flt})\nMy: {mrd_y_flt:.2f} ({passa_y_flt})"
    # Adiciona DIST apenas se não for customizado
    if not is_custom:
        linha_momentos["DIST (Rd)"] = f"Mx: {mrd_x_dist:.2f} ({passa_x_dist})\nMy: {mrd_y_dist:.2f} ({passa_y_dist})"
    
    # Imprime a primeira tabela
    print(tabulate([linha_momentos], headers="keys", tablefmt="fancy_grid"))

    # --- Tabela 2: Forças ---
    linha_forcas = {
        "Verificação": "Forças (kN)",
        "Axial (Nsd/Nrd)": f"{Ncsd:.2f} / {axial_rd:.2f} ({passa_axial})",
        "Cortante (Vsd/Vrd)": f"{Vsd:.2f} / {vrd:.2f} ({passa_vrd})",
        "Apoio Ext (Fw_sd/Fw_rd)": f"{Fwsd_ext:.2f} / {fwrd_ext:.2f} ({passa_fwrd_ext})",
    }
    # Adiciona Apoio Interno apenas se for viga contínua
    if is_continua:
        linha_forcas["Apoio Int (Fw_sd/Fw_rd)"] = f"{Fwsd_int:.2f} / {fwrd_int:.2f} ({passa_fwrd_int})"

    # Imprime a segunda tabela
    print(tabulate([linha_forcas], headers="keys", tablefmt="fancy_grid"))

    # --- Tabela 3: ELS (Flecha) ---
    linha_els = {
        "Verificação": "Flecha (cm)",
        "FLECHA X (calc/lim)": f"{flecha_x:.3f} / {limite_flecha_x:.3f}",
        "FLECHA Y (calc/lim)": f"{flecha_y:.3f} / {limite_flecha_y:.3f}",
        "Resultado ELS": f"{passa_els}",
    }

    # Imprime a terceira tabela
    print(tabulate([linha_els], headers="keys", tablefmt="fancy_grid"))


    # --- Detalhes adicionais se debug ativo ---
    if debug:
        print("\n🧩 Detalhes da verificação à cortante:")
        print(f"    kv = {resultados.get('kv', 0):.3f}") 
        print(f"    Regime = {resultados.get('Regime_cortante', 'N/A')}") 
        print(f"    Vrd = {vrd:.3f} kN")
        print("\n🧩 Detalhes de Web Crippling:")
        print(f"    Fwrd_ext (resistente) = {fwrd_ext:.3f} kN")
        print(f"    Fwrd_int (resistente) = {fwrd_int:.3f} kN")


    print("\n✅ Cálculo concluído com sucesso!")


if __name__ == "__main__":
    main()