"""Visita o app no Streamlit Cloud para evitar hibernação.

Abre a página com um navegador real (necessário, pois o Streamlit
conta atividade via WebSocket) e, se o app estiver dormindo, clica
no botão de religar.
"""
from playwright.sync_api import sync_playwright

URL = "https://dimtercaz.streamlit.app/"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle", timeout=120_000)

    # Se o app estiver hibernando, aparece o botão de religar
    botao = page.get_by_text("Yes, get this app back up", exact=False)
    if botao.count() > 0:
        print("App dormindo — religando...")
        botao.first.click()
        page.wait_for_timeout(60_000)  # espera o app subir
    else:
        print("App já estava no ar.")

    # Mantém a sessão aberta um pouco para registrar atividade
    page.wait_for_timeout(15_000)
    print("Visita concluída:", page.title())
    browser.close()
