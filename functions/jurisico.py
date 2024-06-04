import requests
import wget
import sys
import os

from functions.general import unzip_file

def ju_return_courses(token) -> list:
    """
    Obtém a lista de cursos disponíveis.

    Returns:
        Lista de cursos disponíveis.
    """

    global headers
    print("+ Obtendo lista de cursos disponíveis")
    url = 'https://api.estrategia.com/v3/mci/my-courses/catalog?page=1&perPage=200&includeFavorites=true'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Bearer {token}',
        'Referer': 'https://cj.estrategia.com/',
        'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'X-Requester-Id': 'front-student',
        'X-Vertical': 'carreiras-juridicas'
    }

    response = requests.get(url, headers=headers)
    dados = response.json()
    if response.status_code == 200:
        return dados
    else:
        print("x Falha na requisição dos cursos: ", response.status_code, dados['error']['message'])
        if 'token' in dados['error']['message'].lower():
            print('x Token expirado.. Favor acessar com a conta novamente.')
            sys.exit(0)
    
def get_documents_data(curso:dict):
    """
    Obtém a lista de documentos do curso.
    """
    global headers
    
    url = f'https://api.estrategia.com/v3/mci/my-courses/slug/{curso['slug']}/chapters'
    response = requests.get(url, headers=headers)
    dados = response.json()
    files = []

    if response.status_code == 200:
        for toc in dados['data']['toc_data']['toc']:
            scoupe = {}
            scoupe["scope_type"] = "course_document"
            scoupe["scope_id"] = toc['toc_id']
            scoupe["scope_course"] = curso['id']
            files.append(scoupe)
        url_list = 'https://api.estrategia.com/v3/mci/print/documents/list'
        headers_list = headers.copy()
        headers_list['Content-Type'] = 'application/json'
        payload = {"files": files}
        try:
            response = requests.post(url_list, headers=headers_list, json=payload)
            dados = response.json()['data']
            for dado, file in zip(dados, files):
                file['updated_at'] = dado['updated_at']
            return files
        except requests.exceptions.HTTPError as e:
            print("x Falha na requisição dos cursos: ", e)
            sys.exit(0)

    else:
        print("x Falha na requisição dos cursos: ", response.status_code, dados['error']['message'])

def download_zip(files: list):
    """Faz o download dos arquivos."""

    global headers
    url = "https://api.estrategia.com/v3/mci/print/documents/list/zip"
    payload = {"files": files}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        url_zipfile = response.json()['data']['url']
        return url_zipfile
    except requests.exceptions.HTTPError as e:
        print("x Falha na requisição dos cursos: ", e)
        sys.exit(0)

def ju_download_simulado(curso: dict):
    """Faz o download dos arquivos do curso."""

    path = os.path.join(os.getcwd(), curso['slug'])
    temp_file = 'temp.zip'
    files = get_documents_data(curso)

    # Fazer download
    url_zipfile = download_zip(files)
    filename = os.path.join(path, temp_file)

    try:
        os.makedirs(path, exist_ok=True)
        wget.download(url_zipfile, filename)
    except Exception as e:
        print("x Falha no Download do curso: ", e)
        sys.exit(0)
    
    try:
        unzip_file(filename, path)
    except Exception as e:
        print("x Falha na descompactação do arquivo do curso: ", e)
        sys.exit(0)
    finally:
        os.remove(filename)
    print(f"\n+ Curso {curso['title']} baixado com sucesso!")

def ju_download_course():
    ...

def ju_download_por_lista(resolucao, token):

    cursos = ju_return_courses(token)
    lista_cursos = []
    os.system('cls' if os.name == 'nt' else 'clear')
    print("+ Selecione o que deseja baixar: \n")
    index = 1
    for curso in cursos['data']:
        if not 'conheça a plataforma' in curso['title'].lower():

            course = {}
            curso['index'] = index
            print(f"{index} - {curso['title']}\n")
            if not curso['title'] in lista_cursos:
                lista_cursos.append(course)
            index += 1
        else:
            curso['index'] = 0

    escolha = input("> Digite a sua escolha: ")
    print("\n")
    sair = True
    
    for curso in cursos['data']:
        if escolha == str(curso['index']):
            sair = False
            if 'simulado' in curso['title'].lower():
                ju_download_simulado(curso)
            else:
                ju_download_course()
            