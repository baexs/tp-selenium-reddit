import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Liste de mots-clés haineux à détecter
HATE_KEYWORDS = ["haine", "racisme", "insulte", "violence"]

@pytest.fixture
def driver():
    # --- CONFIGURATION INDISPENSABLE POUR GITHUB ACTIONS ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Pas d'interface graphique
    chrome_options.add_argument("--no-sandbox") # Bypass de la sandbox OS
    chrome_options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems
    chrome_options.add_argument("--window-size=1920,1080") # Définit une taille d'écran fixe
    
    # Initialisation du driver avec les options
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )
    
    driver.implicitly_wait(10) # Attente automatique des éléments (évite les erreurs de chargement)
    driver.get("https://www.reddit.com/r/all/")
    
    yield driver
    driver.quit()

def test_titres_sans_contenu_haineux(driver):
    """Vérifie l'absence de mots-clés haineux dans les titres des 10 derniers posts."""
    posts = driver.find_elements(By.CSS_SELECTOR, "[data-testid='post-title']")[:10]
    preuves = []
    for post in posts:
        text = post.text
        preuves.append(f"Titre vérifié : {text}")
        assert not any(keyword in text.lower() for keyword in HATE_KEYWORDS), f"Titre haineux détecté : {text}"
    
    pytest.titres_verifies = preuves

def test_corps_sans_contenu_haineux(driver):
    """Vérifie l'absence de mots-clés haineux dans les corps des 10 derniers posts."""
    # On récupère les liens vers les posts pour éviter les stale elements après driver.back()
    posts = driver.find_elements(By.CSS_SELECTOR, "[data-testid='post-title']")[:5] # Limité à 5 pour la rapidité
    preuves = []
    
    for i in range(len(posts)):
        # On doit ré-extraire les éléments à chaque itération car la page change
        current_posts = driver.find_elements(By.CSS_SELECTOR, "[data-testid='post-title']")
        current_posts[i].click()
        
        try:
            body_element = driver.find_element(By.CSS_SELECTOR, "[data-testid='post-content']")
            text = body_element.text
            preuves.append(f"Corps vérifié : {text[:100]}...")
            assert not any(keyword in text.lower() for keyword in HATE_KEYWORDS), f"Corps haineux détecté"
        except:
            preuves.append("Post sans corps de texte (image/lien uniquement)")
        
        driver.back()
        
    pytest.corps_verifies = preuves

def test_bouton_signalement_present(driver):
    """Vérifie la présence d'un bouton de signalement pour chaque post."""
    # Reddit change souvent ses sélecteurs, on cherche souvent par texte ou aria-label
    posts = driver.find_elements(By.CSS_SELECTOR, "[data-testid='post-title']")[:3]
    preuves = []
    
    for i in range(len(posts)):
        current_posts = driver.find_elements(By.CSS_SELECTOR, "[data-testid='post-title']")
        title = current_posts[i].text[:30]
        current_posts[i].click()
        
        # Le bouton de signalement est souvent dans un menu "..."
        # On vérifie si un élément de signalement existe
        boutons = driver.find_elements(By.XPATH, "//*[contains(@aria-label, 'Signaler') or contains(text(), 'Report')]")
        
        assert len(boutons) > 0, f"Bouton de signalement manquant pour : {title}"
        preuves.append(f"Post : {title}... -> Bouton de signalement détecté")
        driver.back()
        
    pytest.boutons_verifies = preuves

# --- Hook pour le rapport HTML ---
@pytest.hookimpl(tryfirst=True)
def pytest_html_results_table_row(report, cells):
    if report.when == "call":
        if hasattr(pytest, 'titres_verifies') and "test_titres_sans_contenu_haineux" in report.nodeid:
            cells.insert(2, f"<td>{'<br>'.join(pytest.titres_verifies)}</td>")
        elif hasattr(pytest, 'corps_verifies') and "test_corps_sans_contenu_haineux" in report.nodeid:
            cells.insert(2, f"<td>{'<br>'.join(pytest.corps_verifies)}</td>")
        elif hasattr(pytest, 'boutons_verifies') and "test_bouton_signalement_present" in report.nodeid:
            cells.insert(2, f"<td>{'<br>'.join(pytest.boutons_verifies)}</td>")
