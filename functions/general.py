import requests
import tempfile
import zipfile
import pickle
import sys
import os
import re

from unidecode import unidecode

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
    
def save_file_name(page, arquivo, user, token):
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
        file.writelines(f"{num} - {nome_arquivo} - {user} - {token}")

def unzip_file(zip_path, extract_to):
    """
    Descompacta um arquivo ZIP em um diretório especificado.

    :param zip_path: Caminho para o arquivo ZIP.
    :param extract_to: Diretório onde os arquivos serão extraídos.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    except zipfile.BadZipFile:
        print(f"x O arquivo {zip_path} não é um arquivo ZIP válido.")
    except FileNotFoundError:
        print(f"x O arquivo {zip_path} não foi encontrado.")
    except Exception as e:
        print(f"x Ocorreu um erro ao descompactar o arquivo: {e}")

def load_cookies(nome_arquivo: str):
    """
    Carrega os cookies do arquivo temporário.

    Args:
        Nome do arquivo temporário.
    """
    with open(nome_arquivo, 'rb') as arquivo:
        return pickle.load(arquivo)
    
def login_estrategia(page, email: str, password: str):
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
        token = page.context.storage_state()['origins'][0]['localStorage'][1]['value']
        return username, token
    except Exception as e:
        print(e)
        return False
    
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