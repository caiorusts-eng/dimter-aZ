resultados = {
    "ESC": {},
    "FLT": {},
    "DIST": {},
    "WEB": {}
}


def salvar_resultados(metodo, nome_perfil, valores):
    """Salva os resultados de um método (ESC, FLT, DIST ou WEB)"""
    if metodo in resultados:
        resultados[metodo][nome_perfil] = valores
    else:
        print("Método inválido! Use 'ESC', 'FLT', 'DIST' ou 'WEB'.")


def exibir_resultados():
    """Exibe todos os resultados armazenados"""
    print("\n🔹 🔹 🔹 RESULTADOS FINAIS 🔹 🔹 🔹")

    for metodo, perfis in resultados.items():
        print(f"\n🔹 Método: {metodo}")
        for perfil, valores in perfis.items():
            print(f"\n🔸 Perfil: {perfil}")
            for chave, valor in valores.items():
                print(f"   {chave}: {valor:.4f}")
