## Objetivo
Criar um MCP REST API que conecta a uma API REST de vendas e retorna informações de vendas para análise dos dados.

## Contexto
* O arquivo `docs/data-sales.md` contém informações sobre a API REST de vendas e insights que podem ser usadas para o projeto.
* O arquivo `docs/swagger.json` contém a documentação Swagger da API REST de vendas.
* O Projeto ou repositório é Python e foi criado utilizando o comando `uv`.
* O MCP será usado em stdio em desenvolvimento e sse via container.

## Ação

* Crie o MCP REST API que conecta a uma API REST de vendas e retorna informações de vendas para análise dos dados.
* Utilize as informações dos arquivos `docs/data-sales.md` e `docs/swagger.json` para criar o MCP.
* Crie prompts, resources e tools em arquivos separados organizados em um diretório `server`.
* Utilize um arquivo `.env` e para isto crie um de exemplo para as informações de conexão com a API REST de vendas.
* Utilize o MCP Inspector para que eu possa testar o MCP com o comando `uv run mcp dev main.py`.
* As descriptions dos recursos precisam estar em Português do Brasil para alinhar os prompts dos usuários com as descrições. Os prompts vão estar em Português do Brasil também.
* Crie um diretório `.container` e adicione Dockerfile e arquivos YAML para o kubernetes (deployment e service). Arquivo `docker-compose.yaml` vai ser criado na raíz do projeto. Crie o `.dockerignore`.
* Documente o projeto no arquivo README.md.
* Crie o arquivo CLAUDE.md ao final como feito pelo comando `/init`.

