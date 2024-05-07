import pickle
import tempfile
import os
import re
import time
from tqdm import tqdm
from unidecode import unidecode
import sys
import wget
import requests

def create_txt(curso: str):
    """
    Cria um arquivo temporário.

    Args:
        curso: Nome do curso.
    Returns:
        Nome do arquivo temporário.
    """
    temp_dir = tempfile.gettempdir()
    txt_file = os.path.join(temp_dir, f'temp_{curso}.txt')
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
    try:
        page.wait_for_selector('//section[@id]')
    except Exception as e:
        if 'login' in page.url:
            print('x Login expirado.. Favor acessar com a conta novamente.')
            sys.exit(0)
        else:
            print(e)
            sys.exit(0)
            
    elementos = page.query_selector_all('//section[@id]')
    print(f"+ Quantidade de cursos: {len(elementos)}")
    return elementos

def get_course_data(page, curso: dict, resolucao:str) -> list:
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
        link_pdf = page.wait_for_selector('xpath=//div[@class="Lesson-contentTop"]//a').get_attribute('href')


        aula['id'] = aula_num.inner_text()
        aula['nome'] = aula_nome.inner_text()
        aula['link_pdf'] = link_pdf
        videos_list = []

        videos = lesson.query_selector_all('xpath=.//div[@class="ListVideos-items-video"]')
        for i, video in enumerate(videos):
            v = {}
            url = video.wait_for_selector('xpath=./a')
            video_num =  video.wait_for_selector('xpath=.//span[contains(@class, "index")]')
            video_nome = video.wait_for_selector('xpath=.//span[contains(@class, "title")]')
            url.click()
            time.sleep(0.5)
            if i == 0:
                download_options = page.wait_for_selector('xpath=//*[contains(text(), "download")]/../..')
                download_options.click()
                time.sleep(0.5)
            video_link = page.wait_for_selector(f'xpath=//*[contains(text(), "veis:")]/following-sibling::div/a[contains(text(), "{resolucao}")]').get_attribute('href')
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
    if len(dict) > 0:
        for aula in dict:
            total_videos += len(aula['videos'])
    return total_videos

def clear_name(name: str) -> str:
    """
    Limpa o nome do curso.
    """
    return unidecode(re.sub(r'[^\w\s-]', '', name))

def remove_ultima_linha():
    """Remove a última linha do terminal."""

    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")

def remove_tmp_files(directory:str) -> bool:
    """
    Remove arquivos temporários.

    Args:
        directory: Diretório dos arquivos temporários.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".tmp"):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)

def download_por_lista(page, resolucao):
    cursos = return_courses(page)
    lista_cursos = []
    os.system('cls' if os.name == 'nt' else 'clear')
    print("+ Selecione o que deseja baixar: \n")
    for i, curso in enumerate(cursos):
        course = {}
        nome_curso = curso.wait_for_selector('xpath=.//h1').inner_text()
        qualificacao = curso.wait_for_selector('xpath=./../../h2').inner_text()
        url = curso.wait_for_selector('xpath=./a').get_attribute('href')
        if 'aula' in url:
            url = "https://www.estrategiaconcursos.com.br" + url
            print(f"{i+1}.\nNome: {nome_curso}\nQualificação: {qualificacao}\nURL: {url}\n")
            course['id'] = i+1
            course['nome'] = nome_curso
            course['qualificacao'] = qualificacao
            course['url'] = url
            lista_cursos.append(course)
        else:
            i -= 1

    escolha = input("> Digite a sua escolha: ")
    print('\n')
    sair = True
    for curso in lista_cursos:
        if escolha == str(curso['id']):
            sair = False
            if 'pacote' in curso['url']:

                page.goto(curso['url'])
                page.wait_for_selector('xpath=//div[@class="containerCursos"]')
                pacote = page.wait_for_selector('xpath=//h2').inner_text()
                pacote_name = ' '.join(pacote.split(' ')[:4]).split('(')[0]
                path_pacote = os.path.join(os.getcwd(), clear_name(pacote_name.strip()))
                os.makedirs(path_pacote, exist_ok=True)
                time.sleep(1)
                courses_list = page.query_selector_all('xpath=//div[@class="containerCursos"]/a')
                print(f"- Pacote identificado: {pacote_name} com {len(courses_list)} cursos para baixar.")
                links = []
                for cur in courses_list:
                    link = 'https://www.estrategiaconcursos.com.br' + cur.get_attribute('href')
                    links.append(link)
                for link in links:
                    print("+ Obtendo dados do curso...")
                    time.sleep(1)

                    curso['url'] = link
                    filename = os.path.join(os.getcwd(), clear_name(curso['nome']))
                    os.makedirs(filename, exist_ok=True)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    data = get_course_data(page, curso, resolucao)
                    total = return_total_videos(data)
                    if total == 0 and sum(1 for d in data if 'link_pdf' in d) > 0:
                        print('- Curso não há videos, somente PDF.')
                        time.sleep(3)
                    indice = 0
                    os.system('cls' if os.name == 'nt' else 'clear')

                    for item in tqdm(data, desc=f"Baixando Aulas"):

                        nome_aula = f"{item['nome']}"
                        dir_aula = os.path.join(filename, f'Aula {indice+1} - ' + clear_name(' '.join(nome_aula.split(' ')[:4])).strip())
                        os.makedirs(dir_aula, exist_ok=True)
                        file_pdf = f'Aula {indice+1}.pdf'
                        download_pdf(data[indice]['link_pdf'], os.path.join(dir_aula, file_pdf))
                        
                        if len(item['videos']) > 0:
                            for video in item['videos']:
                                nome_video = f"{clear_name(video['id'])} - {clear_name(' '.join(video['nome'].split(' ')[:4]))}.mp4"
                                path = os.path.join(dir_aula, nome_video)
                                print('\n')
                                wget.download(video['link'], path)
                                os.system('cls')
                        indice += 1

                    print('\n')
                    print("> Curso baixado com sucesso")
                    remove_tmp_files(os.getcwd())
            else:

                print("+ Obtendo dados do curso...")
                time.sleep(1)
                filename = os.path.join(os.getcwd(), clear_name(curso['nome']))
                os.makedirs(filename, exist_ok=True)
                os.system('cls' if os.name == 'nt' else 'clear')
                data = get_course_data(page, curso, resolucao)
                total = return_total_videos(data)
                if total == 0 and sum(1 for d in data if 'link_pdf' in d) > 0:
                    print('- Curso não há videos, somente PDF.')
                    time.sleep(3)
                indice = 0
                os.system('cls' if os.name == 'nt' else 'clear')

                for item in tqdm(data, desc=f"Baixando Aulas"):

                    nome_aula = f"{item['nome']}"
                    dir_aula = os.path.join(filename, f'Aula {indice+1} - ' + clear_name(' '.join(nome_aula.split(' ')[:4])).strip())
                    os.makedirs(dir_aula, exist_ok=True)
                    file_pdf = f'Aula {indice+1}.pdf'
                    download_pdf(data[indice]['link_pdf'], os.path.join(dir_aula, file_pdf))
                    
                    if len(item['videos']) > 0:
                        for video in item['videos']:
                            nome_video = f"{clear_name(video['id'])} - {clear_name(' '.join(video['nome'].split(' ')[:4]))}.mp4"
                            path = os.path.join(dir_aula, nome_video)
                            print('\n')
                            wget.download(video['link'], path)
                            os.system('cls')
                    indice += 1

                print('\n')
                print("> Curso baixado com sucesso")
                remove_tmp_files(os.getcwd())
    if sair:
        print("x Opção Inválida")
        exit(0)

def download_por_url(page, url: str, resolucao: str, pacote_path:str):
    """
    Faz Download do Curso através do link.

    Args:
        page: Classe Página do Playwright.
        url: Link do Curso.
    """

    lista_aulas = []
    page.goto(url)
    print("+ Obtendo dados do curso...")

    try:
        page.wait_for_selector('//*[@class="LessonList"]')
    except Exception as e:
        if 'login' in page.url:
            print('x Login expirado.. Favor acessar com a conta novamente.')
            sys.exit(0)
        else:
            print(e)
            sys.exit(0)

    lesson_list = page.query_selector_all('//*[@class="LessonList"]//section')
    course_title = page.wait_for_selector('h2[class*="title"]').inner_text()
    for lesson in tqdm(lesson_list, desc="Processando aulas"):
        aula = {}
        aula_num = lesson.wait_for_selector('xpath=.//a//h2')                        
        aula_nome = lesson.wait_for_selector('xpath=.//a//p')
        lesson.click()
        link_pdf = page.wait_for_selector('xpath=//div[@class="Lesson-contentTop"]//a').get_attribute('href')

        aula['id'] = aula_num.inner_text()
        aula['nome'] = aula_nome.inner_text()
        aula['link_pdf'] = link_pdf
        videos_list = []

        videos = lesson.query_selector_all('xpath=.//div[@class="ListVideos-items-video"]')
        for i, video in enumerate(videos):
            v = {}
            url = video.wait_for_selector('xpath=./a')
            video_num =  video.wait_for_selector('xpath=.//span[contains(@class, "index")]')
            video_nome = video.wait_for_selector('xpath=.//span[contains(@class, "title")]')
            url.click()
            time.sleep(0.5)
            if i == 0:
                download_options = page.wait_for_selector('xpath=//*[contains(text(), "download")]/../..')
                download_options.click()
                time.sleep(0.5)
            video_link = page.wait_for_selector(f'xpath=//*[contains(text(), "veis:")]/following-sibling::div/a[contains(text(), "{resolucao}")]').get_attribute('href')

            v['id'] = video_num.inner_text()
            v['nome'] = video_nome.inner_text()
            v['link'] = video_link
            videos_list.append(v)
        aula['videos'] = videos_list
        lista_aulas.append(aula)
    #______________
    total = return_total_videos(lista_aulas)
    if total == 0 and sum(1 for d in lista_aulas if 'link_pdf' in d) > 0:
        print('- Curso não há videos, somente PDF.')
        time.sleep(3)
    indice = 0
    if pacote_path:
        direname = os.path.join(pacote_path, clear_name(' '.join(course_title.split(' ')[:6]).split('-', -1)[0].strip()))
        os.makedirs(direname, exist_ok=True)
    else:
        direname = os.path.join(os.getcwd(), clear_name(' '.join(course_title.split(' ')[:6]).split('-', -1)[0].strip()))
        os.makedirs(direname, exist_ok=True)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    for item in tqdm(lista_aulas, desc=f"Baixando Aulas"):

        nome_aula = f"{item['nome']}"
        dir_aula = os.path.join(direname, f'Aula {indice+1} - ' + clear_name(' '.join(nome_aula.split(' ')[:4])).strip())
        os.makedirs(dir_aula, exist_ok=True)
        file_pdf = f'Aula {indice+1}.pdf'
        download_pdf(lista_aulas[indice]['link_pdf'], os.path.join(dir_aula, file_pdf))
        
        if len(item['videos']) > 0:
            for video in item['videos']:
                nome_video = f"{clear_name(video['id'])} - {clear_name(' '.join(video['nome'].split(' ')[:4]))}.mp4"
                path = os.path.join(dir_aula, nome_video)
                print('\n')
                wget.download(video['link'], path)
                os.system('cls')
        indice += 1

    print('\n')
    print("> Curso baixado com sucesso")
    remove_tmp_files(os.getcwd())

def download_pdf(link: str, filename: str):
    """
    Faz Download do PDF.

    Args:
        link: Link do PDF.
        filename: Nome do PDF.
    """
    response = requests.get(link)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
