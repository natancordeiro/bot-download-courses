import os

def ju_return_courses(page) -> list:
    """
    Obtém a lista de cursos disponíveis.

    Returns:
        Lista de cursos disponíveis.
    """
    print("+ Obtendo lista de cursos disponíveis")
    page.goto("https://cj.estrategia.com/meus-cursos/")
    try:
        page.wait_for_selector('//div[contains(text(), "Cursos")]')
    except Exception as e:
        print(e)
        return False
    elementos = page.query_selector_all('//div[contains(@class, "course-card")]')
    print(f"+ Quantidade de cursos: {len(elementos)}")
    return elementos

def ju_download_simulado():
    ...

def ju_download_course():
    ...


def ju_download_por_lista(page, resolucao):

    cursos = ju_return_courses(page)
    lista_cursos = []
    os.system('cls' if os.name == 'nt' else 'clear')
    print("+ Selecione o que deseja baixar: \n")
    for i, curso in enumerate(cursos):
        course = {}
        course['id'] = i+1
        course['nome'] = curso.wait_for_selector('xpath=.//div[contains(@class, "content")]').inner_text()
        course['element'] = curso.wait_for_selector('xpath=.//div[contains(@class, "content")]')
        print(f"{i+1} - {curso.inner_text()}")
        if not curso.inner_text() in lista_cursos:
            lista_cursos.append(course)

    escolha = input("> Digite a sua escolha: ")
    print("\n")
    sair = True
    for curso in lista_cursos:
        if escolha == str(curso['id']):
            sair = False
            if 'simulado' in curso['nome'].lower():
                ju_download_simulado()
            else:
                ju_download_course()
            