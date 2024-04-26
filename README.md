Robô de Download de Cursos do Estratégia Concursos 📖
==================================================

Este projeto é um robô que automatiza o processo de download de cursos da plataforma Estratégia Concursos. Com ele, você pode baixar seus cursos favoritos diretamente para o seu computador.

Pré-requisitos
--------------

Antes de começar, você precisa ter o Python instalado em sua máquina. Se você ainda não tem o Python instalado, siga as instruções abaixo:

1.  Baixando e Instalando o Python:

    -   Acesse o [site oficial do Python](https://www.python.org/downloads/) e clique no link de download adequado para o seu sistema operacional (32 ou 64 bits).
    -   Execute o instalador e marque a opção "Add Python to PATH".
    -   Clique em "Install Now" e aguarde a conclusão da instalação.
    -   Verifique se a instalação foi bem-sucedida digitando o seguinte comando no prompt de comando:

        ```
        python --version

        ```

        Isso deve exibir a versão do Python instalada em sua máquina.
2.  Clonando o Repositório:

    -   Clone este repositório para o seu computador usando o comando:

        ```
        git clone https://github.com/seu-usuario/nome-do-repositorio.git

        ```

    -   Ou, se preferir, faça o download do código em formato .zip diretamente do repositório no GitHub.
3.  Instalando as Bibliotecas Necessárias:

    -   Navegue até o diretório do projeto no prompt de comando:

        ```
        cd caminho/para/o/diretorio-do-projeto

        ```

    -   Instale as bibliotecas listadas no arquivo `requirements.txt` usando o seguinte comando:

        ```
        pip install -r requirements.txt

        ```
   -   Instale a biblioteca de automação separadamente usando o seguinte comando:

        ```
        playwright install chromium

        ```

Executando o Robô
-----------------

Agora que você tem tudo configurado, execute o programa com o seguinte comando:

```
python main.py

```

O robô irá acessar a plataforma Estratégia Concursos, fazer o login (você precisará fornecer suas credenciais) e iniciar o processo de download dos cursos especificados.

Lembre-se de que este projeto é apenas para fins educacionais e de aprendizado. Certifique-se de respeitar os termos de uso da plataforma Estratégia Concursos.

Divirta-se e bons estudos! 🚀
