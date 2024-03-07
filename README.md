# API de Integração

## Descrição

API de Integração entre o sistema Futurai e o PI Server.

## Estrutura do Projeto

- `config/`: Esta pasta é responsável por configurar o ID da empresa na plataforma Futurai, configurar o nome do servidor Py System e configurar quais tags do PI System serão extraídas.
- `app.py`: Este é o arquivo principal onde o código é executado.
- `libs.py`: Este arquivo contém funções auxiliares usadas pelo `app.py`.
- `app.sh`: Este é o acionador da regra que ficará vinculado ao agendador de tarefas.

## Implantação

Para implantar o projeto, o ambiente deve ser preparado usando o arquivo `requirements.txt`. Para fazer isso, execute o seguinte comando no terminal:

```bash
pip install -r requirements.txt
