import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # Pas d'interface graphique
options.add_argument("--no-sandbox") # Indispensable sur Linux/Docker
options.add_argument("--disable-dev-shm-usage") # Évite les problèmes de mémoire partagée
driver = webdriver.Chrome(options=options)

# Liste de mots-clés haineux à détecter
HATE_KEYWORDS = ["haine", "racisme", "insulte", "violence"]

@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.reddit.com/r/all/")
    yield driver
    driver.quit()

def test_titres_sans_contenu_haineux(driver):
    """Vérifie l'absence de mots-clés haineux dans les titres des 10 derniers posts."""
    posts = driver.find_elements(By.CSS_SELECTOR, "[data-testid='post-title']")[:10]
    preuves = []
    for post in posts:
        preuves.append(f"Titre vérifié : {post.text}")
        title = post.text.lower()
        assert not any(keyword in title for keyword in HATE_KEYWORDS), f"Titre haineux détecté : {title}"
    # Ajoute les preuves au rapport via un attribut pytest
    pytest.titres_verifies = preuves

def test_corps_sans_contenu_haineux(driver):
    """Vérifie l'absence de mots-clés haineux dans les corps des 10 derniers posts."""
    posts = driver.find_elements(By.CSS_SELECTOR, "[data-testid='post-title']")[:10]
    preuves = []
    for post in posts:
        post.click()
        body_element = driver.find_element(By.CSS_SELECTOR, "[data-testid='post-content']")
        preuves.append(f"Corps vérifié : {body_element.text[:100]}...")  # On troncature pour éviter les logs trop longs
        body = body_element.text.lower()
        assert not any(keyword in body for keyword in HATE_KEYWORDS), f"Corps haineux détecté : {body}"
        driver.back()
    # Ajoute les preuves au rapport via un attribut pytest
    pytest.corps_verifies = preuves

def test_bouton_signalement_present(driver):
    """Vérifie la présence d'un bouton de signalement pour chaque post."""
    posts = driver.find_elements(By.CSS_SELECTOR, "[data-testid='post-title']")[:10]
    preuves = []
    for post in posts:
        post.click()
        bouton = driver.find_elements(By.CSS_SELECTOR, "[aria-label='Signaler']")
        preuves.append(f"Post : {post.text[:50]}... -> Bouton {bouton.text!r} présent")
        assert len(bouton) > 0, f"Bouton de signalement manquant pour : {post.text}"
        driver.back()
    # Ajoute les preuves au rapport via un attribut pytest
    pytest.boutons_verifies = preuves

# Hook pytest pour ajouter les preuves au rapport HTML
def pytest_html_results_table_row(report, cells):
    if report.when == "call":
        if hasattr(pytest, 'titres_verifies') and report.nodeid.endswith("test_titres_sans_contenu_haineux"):
            cellules_preuves = "<br>".join(pytest.titres_verifies)
            cells.insert(2, f"<td>{cellules_preuves}</td>")
            cells[1] = "<th>Preuves (titres)</th>"
        elif hasattr(pytest, 'corps_verifies') and report.nodeid.endswith("test_corps_sans_contenu_haineux"):
            cellules_preuves = "<br>".join(pytest.corps_verifies)
            cells.insert(2, f"<td>{cellules_preuves}</td>")
            cells[1] = "<th>Preuves (corps)</th>"
        elif hasattr(pytest, 'boutons_verifies') and report.nodeid.endswith("test_bouton_signalement_present"):
            cellules_preuves = "<br>".join(pytest.boutons_verifies)
            cells.insert(2, f"<td>{cellules_preuves}</td>")
            cells[1] = "<th>Preuves (boutons)</th>"
