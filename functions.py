import pickle
import tempfile
import os
import time
from tqdm import tqdm

def create_txt():
    """
    Cria um arquivo temporário.

    Returns:
        Nome do arquivo temporário.
    """
    temp_dir = tempfile.gettempdir()
    txt_file = os.path.join(temp_dir, 'temp_file_name.txt')
    try:
        with open(txt_file, 'r+') as file:
            arquivo = file.readline()
            return txt_file
    except FileNotFoundError:
        print(f"- Arquivo {txt_file} não encontrado. Criando...")
        with open(txt_file, 'w+') as file:
            arquivo = file.write("")
            return txt_file

def save_cookies(cookies: list):
    """
    Salva os cookies em um arquivo temporário.

    Args:
        Lista de cookies.
    Returns:
        Nome do arquivo temporário.
    """
    with tempfile.NamedTemporaryFile(delete=False) as arquivo:
        pickle.dump(cookies, arquivo)
        return arquivo.name
    
def save_file_name(page, arquivo, user):
    nome_arquivo = save_cookies(page.context.cookies())
    print(f"- Cookies salvo em: {nome_arquivo}")
    with open(arquivo, 'w') as file:
        try:
            lines = file.readlines()
            if lines:
                last_num = lines[-1].strip('-')[0]
                num = int(last_num) + 1
            else:
                num = 1
        except:
            num = 1
        file.writelines(f"{num} - {nome_arquivo} - {user}")

def load_cookies(nome_arquivo: str):
    """
    Carrega os cookies do arquivo temporário.

    Args:
        Nome do arquivo temporário.
    """
    with open(nome_arquivo, 'rb') as arquivo:
        return pickle.load(arquivo)
    
def login(page, email: str, password: str):
    """
    Realiza o login no perfil estrategia.com.

    Args:
        page: Classe Página do Playwright.
        email: Email do perfil estrategia.
        password: Senha do perfil estrategia.

    """
    try:
        page.goto("https://perfil.estrategia.com/login")
        page.wait_for_selector('//input[@type="email"]')
        page.type('//input[@type="email"]', email)

        page.wait_for_selector('//input[@type="password"]')
        page.type('//input[@type="password"]', password)

        page.wait_for_selector('//button[@type="submit"]')
        page.click('//button[@type="submit"]')

        page.wait_for_url('https://perfil.estrategia.com/meu-perfil/')
        username = page.wait_for_selector('//span[contains(text(), "Ol")]/following-sibling::div/span').inner_text()
        return username
    except Exception as e:
        print(e)
        return False

def return_courses(page) -> list:
    """
    Obtém a lista de cursos disponíveis.

    Returns:
        Lista de cursos disponíveis.
    """
    print("+ Obtendo lista de cursos disponíveis")
    page.goto("https://www.estrategiaconcursos.com.br/app/dashboard/cursos")
    page.wait_for_selector('//section[@id]')
    elementos = page.query_selector_all('//section[@id]')
    print(f"Quantidade de cursos: {len(elementos)}")
    return elementos

def get_course_data(page, curso: dict) -> list:
    """
    Obtém os dados de um curso.

    Args:
        page: Classe Página do Playwright.
        curso: Dicionário com os dados do curso.

    Returns:
       Lista de dicionários com os dados do curso.
    """

    lista_aulas = []
    page.goto(curso['url'])
    page.wait_for_selector('//*[@class="LessonList"]')
    lesson_list = page.query_selector_all('//*[@class="LessonList"]//section')
    for lesson in tqdm(lesson_list, desc="Processando aulas"):
        aula = {}
        aula_num = lesson.wait_for_selector('xpath=.//a//h2')                        
        aula_nome = lesson.wait_for_selector('xpath=.//a//p')
        lesson.click()
        time.sleep(1)
        aula['id'] = aula_num.inner_text()
        aula['nome'] = aula_nome.inner_text()
        videos_list = []

        page.wait_for_selector('xpath=//*[@class="LessonList"]//section//div[@class="ListVideos-items-video"]')
        videos = lesson.query_selector_all('xpath=.//div[@class="ListVideos-items-video"]')
        for video in videos:
            v = {}
            url = video.wait_for_selector('xpath=./a')
            video_num =  video.wait_for_selector('xpath=.//span[contains(@class, "index")]')
            video_nome = video.wait_for_selector('xpath=.//span[contains(@class, "title")]')
            url.click()
            time.sleep(0.5)
            video_link = lesson.wait_for_selector('xpath=.//video').get_attribute('src')
            v['id'] = video_num.inner_text()
            v['nome'] = video_nome.inner_text()
            v['link'] = video_link
            videos_list.append(v)
        aula['videos'] = videos_list
        lista_aulas.append(aula)
    return lista_aulas

def return_total_videos(dict) -> int:
    """Retorna o valor total de videos."""

    total_videos = 0
    for aula in dict:
        total_videos += len(aula['videos'])
    return total_videos