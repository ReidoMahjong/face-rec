# Reconhecimento Facial

Sistema de reconhecimento facial em tempo real via navegador, com cadastro de pessoas e identificação por câmera. O frontend se comunica com uma API Python (FastAPI) que usa `face-recognition` para gerar e comparar templates faciais armazenados no MongoDB. As imagens **não são salvas em disco** — apenas o encoding facial é persistido no banco.

---

## Estrutura do projeto

```
.
├── Main.py               # API FastAPI (endpoints /cadastrar e /reconhecer)
├── conexao_bd.py         # Conexão com MongoDB e geração de templates
├── reconhecer_rosto.py   # Detecção e identificação de rostos por frame
├── index.html            # Interface web (câmera, cadastro, reconhecimento)
├── requirements.txt      # Dependências Python
└── .env                  # Variáveis de ambiente (não versionar)
```

---

## Pré-requisitos

- Python 3.9+
- MongoDB (local ou Atlas)
- CMake e compilador C++ instalados (necessário para o `dlib`)

### Instalando dependências do sistema

**Ubuntu/Debian**
```bash
sudo apt install cmake build-essential libopenblas-dev liblapack-dev
```

**macOS**
```bash
brew install cmake
```

**Windows**
Baixe o wheel pré-compilado do dlib em https://github.com/sachadee/Dlib e instale antes de rodar `pip install -r requirements.txt`.

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## Configuração

Crie um arquivo `.env` na raiz do projeto com a string de conexão do MongoDB:

```env
mongo=mongodb+srv://usuario:senha@cluster.mongodb.net/
```

> **Atenção:** nunca suba o arquivo `.env` para o repositório. Adicione-o ao `.gitignore`.

---

## Executando

```bash
uvicorn Main:app --reload
```

A API ficará disponível em `http://localhost:8000`. O frontend (`index.html`) é servido automaticamente nessa URL.

Para expor a API externamente (ex: ngrok):
```bash
ngrok http 8000
```
Atualize a constante `API` no `index.html` com a URL gerada.

---

## Endpoints

### `GET /`
Serve o frontend (`index.html`).

---

### `POST /cadastrar`
Cadastra uma pessoa. A imagem é processada em memória — apenas o encoding facial é salvo no banco.

**Form data:**

| Campo | Tipo | Descrição |
|---|---|---|
| `nomePessoa` | string | Nome da pessoa |
| `nomeImagem` | string | Nome de referência do cadastro |
| `imagem` | file | Foto (JPG ou PNG, apenas 1 rosto) |

**Respostas:**

| Código | Descrição |
|---|---|
| `200` | Cadastro realizado com sucesso |
| `400` | Formato de arquivo inválido |
| `422` | Nenhum rosto detectado ou mais de um rosto na imagem |
| `500` | Erro interno |

---

### `POST /reconhecer`
Recebe um frame da câmera e retorna os rostos detectados com nome e posição.

**Form data:**

| Campo | Tipo | Descrição |
|---|---|---|
| `frame` | file | Frame JPEG capturado pelo browser |

**Resposta:**
```json
{
  "rostos": [
    {
      "nome": "João Silva",
      "x": 120,
      "y": 80,
      "w": 100,
      "h": 100,
      "conhecido": true
    }
  ]
}
```

---

## Como funciona

```
Browser (câmera)
    │
    │  frame JPEG  (POST /reconhecer)
    ▼
FastAPI (Main.py)
    │
    ▼
reconhecer_rosto.py
    ├── OpenCV detecta rostos no frame (Haar Cascade)
    ├── face-recognition gera encoding de cada rosto
    └── Compara com templates armazenados no MongoDB
            │
            └── Retorna nome + coordenadas x, y, w, h
```

No cadastro, a imagem é lida diretamente da memória (sem gravação em disco), o encoding facial é extraído e apenas os metadados são persistidos no MongoDB.

---

## Banco de dados

Coleção `pessoas` no banco `rf`:

| Campo | Tipo | Descrição |
|---|---|---|
| `NomePessoa` | string | Nome da pessoa |
| `nomeImagem` | string | Nome de referência do cadastro |
| `template` | array | Encoding facial (128 valores) |
| `dataInsercao` | date | Data e hora do cadastro |

---

## Observações

- A tolerância de comparação facial está definida em `0.5` (padrão). Valores menores tornam o reconhecimento mais restritivo.
- O detector Haar Cascade (`haarcascade_frontalface_default.xml`) funciona melhor com rostos frontais e boa iluminação.
- Em produção, substitua `allow_origins=["*"]` no CORS pelo domínio real da aplicação.
