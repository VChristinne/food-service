# Food Service API

Aplicação RESTful desenvolvida com FastAPI para gerenciar operações de um serviço de alimentação, incluindo gestão de funcionários, clientes, catálogo de produtos, inventário, pedidos, autenticação e lojas.

## 📋 Quick Start

### Requisitos

- Python 3.13+
- uv (package manager)
- SQLite 3.51.0+

### Instalação

```bash
# Clonar repositório
git clone <repository-url>
cd Food-Service

# Instalar dependências
uv sync
```

### Configuração

```bash
# Copiar arquivo de exemplo e gerar seu token
cp .env.example .env
```

### Iniciar API

```bash
uv run uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`

## 📚 Documentação

| Recurso        | URL                                |
| -------------- | ---------------------------------- |
| Swagger UI     | http://localhost:8000/docs         |
| OpenAPI Schema | http://localhost:8000/openapi.json |

## 🔐 Autenticação

A API utiliza JWT para autenticação. A maioria dos endpoints requer um token válido.

Caso haja dúvidas sobre quais tokens utilizar, consulte os arquivos `*_routers.py` ou o Relatório do Trabalho Multidisciplinar.

## 🧪 Testes

Não há testes automatizados. Para testar os endpoints:

**Insomnia**

- Importe `Food_Service_4668871.yaml`
- Endpoints pré-configurados em ordem de execução
- As váriaveis da coleção estão configuradas para facilitar o teste, como `{{bearerToken}}` para o token JWT então basta fazer login para mudar automaticamente o token para os próximos testes

## 🗄️ Banco de Dados

As tabelas são criadas automaticamente na primeira execução:

```python
db.create_tables()  # main.py
```

Localização: `Database/food_service.db` (SQLite)

## ⚙️ Configuração do Ambiente

Veja `.env.example` para variáveis disponíveis:

```env
# Banco de Dados
DATABASE_URL=sqlite:///Database/food_service.db

# Autenticação
SECRET_KEY=sua-chave-secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📖 Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [uvicorn](https://www.uvicorn.org/)
- [uv Package Manager](https://docs.astral.sh/uv/)

## 📝 Licença

Projeto desenvolvido como trabalho multidisciplinar do curso de Análise e Desenvolvimento de Sistemas.
