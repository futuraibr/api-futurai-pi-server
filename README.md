# **API de Integração - Futurai & PI Server**

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=futuraibr_api-futurai-pi-server&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=futuraibr_api-futurai-pi-server)  
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=futuraibr_api-futurai-pi-server&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=futuraibr_api-futurai-pi-server)  
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=futuraibr_api-futurai-pi-server&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=futuraibr_api-futurai-pi-server)  
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=futuraibr_api-futurai-pi-server&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=futuraibr_api-futurai-pi-server)

## 📌 **Descrição**

Esta API facilita a integração entre a **plataforma Futurai** e o **PI Server**, permitindo a extração, processamento e envio de dados históricos e em tempo real.

---

## 📁 **Estrutura do Projeto**

A estrutura do projeto está organizada da seguinte forma:

```bash
├── config/            # Configuração do ambiente e parâmetros do sistema
│   ├── config.yaml    # ID da empresa, nome do servidor PI e tags a serem extraídas
│   ├── tags.yaml      # Mapeamento de tags do PI System
│   ├── historico.yaml # Período histórico de dados a serem processados
├── app.py             # Arquivo principal que executa a integração
├── libs.py            # Biblioteca com funções auxiliares para a API
├── app.sh             # Script de inicialização vinculado ao agendador de tarefas
├── requirements.txt   # Dependências do projeto
├── README.md          # Documentação do projeto
```

### **📌 Explicação dos Principais Arquivos**

- **`config/`** → Contém os arquivos de configuração essenciais para a comunicação com o **PI Server** e o **Futurai**.
- **`app.py`** → Código principal que orquestra a coleta e envio de dados.
- **`libs.py`** → Funções auxiliares como autenticação, processamento de dados e logs.
- **`app.sh`** → Arquivo de script para automatizar a execução via **cron jobs** ou outro agendador.
- **`requirements.txt`** → Lista de dependências necessárias para rodar o projeto.

---

## 🚀 **Implantação**

### **1⃣ Configurar o ambiente virtual (opcional, mas recomendado)**

Antes de instalar as dependências, recomenda-se criar e ativar um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Para Linux/macOS
venv\Scripts\activate      # Para Windows
```

### **2⃣ Instalar as dependências**

Execute o seguinte comando para instalar todas as dependências necessárias:

```bash
pip install -r requirements.txt
```

### **3⃣ Configurar os parâmetros do sistema**

- **Edite o arquivo `config/config.yaml`** para definir:
  - ID da empresa na Futurai
  - Nome do servidor PI
  - Tags do PI System a serem extraídas

---

## 🛠️ **Execução do Projeto**

Para executar a API manualmente, use o seguinte comando:

```bash
python app.py
```

Caso esteja utilizando um **agendador de tarefas**, assegure-se de que o script `app.sh` está configurado corretamente.

### **Windows (Agendador de Tarefas):**

1. Abra o **Agendador de Tarefas** do Windows.
2. Clique em **Criar Tarefa...**.
3. Na guia **Geral**, defina um nome para a tarefa.
4. Na guia **Disparadores**, configure a frequência de execução.
5. Na guia **Ações**, selecione **Iniciar um programa** e insira o caminho para `app.sh`.
6. Salve e ative a tarefa.

---

## 📊 **Monitoramento e Qualidade do Código**

Esta API passa por verificações automatizadas de qualidade de código via **SonarCloud**:

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=futuraibr_api-futurai-pi-server&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=futuraibr_api-futurai-pi-server)  
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=futuraibr_api-futurai-pi-server&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=futuraibr_api-futurai-pi-server)  
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=futuraibr_api-futurai-pi-server&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=futuraibr_api-futurai-pi-server)  
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=futuraibr_api-futurai-pi-server&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=futuraibr_api-futurai-pi-server)

---

## 📄 **Licença**

Este projeto segue a licença **MIT**. Consulte o arquivo `LICENSE` para mais detalhes.

---
