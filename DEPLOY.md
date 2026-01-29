# 🚀 Guia de Deploy: Biblioteca Pessoal no Render + Supabase

Este guia vai te ajudar a hospedar sua aplicação **gratuitamente** usando:
- **Render** - Hospedagem da aplicação Flask
- **Supabase** - Banco de dados PostgreSQL gratuito

---

## 📋 Pré-requisitos

1. Conta no [GitHub](https://github.com) (para subir o código)
2. Conta no [Supabase](https://supabase.com) (gratuita)
3. Conta no [Render](https://render.com) (gratuita)

---

## Parte 1: Configurar o Banco de Dados no Supabase

### Passo 1.1 - Criar conta e projeto no Supabase

1. Acesse [https://supabase.com](https://supabase.com)
2. Clique em **"Start your project"** e faça login com GitHub
3. Clique em **"New project"**
4. Preencha:
   - **Name**: `biblioteca-pessoal`
   - **Database Password**: Crie uma senha forte e **ANOTE-A!** Você vai precisar dela.
   - **Region**: Escolha a mais próxima (ex: South America - São Paulo)
5. Clique em **"Create new project"**
6. Aguarde alguns minutos enquanto o projeto é criado

### Passo 1.2 - Obter a URL de conexão

1. No painel do Supabase, vá em **Settings** (ícone de engrenagem) → **Database**
2. Role até a seção **"Connection string"**
3. Selecione a opção **"URI"**
4. Copie a URL que aparece (começa com `postgres://postgres:...`)
5. **IMPORTANTE**: Substitua `[YOUR-PASSWORD]` pela senha que você criou no passo 1.1

Exemplo de URL final:
```
postgres://postgres:SuaSenhaAqui@db.xxxxxxxxxxxx.supabase.co:5432/postgres
```

> ⚠️ **Dica**: Use a conexão na porta **6543** (pooler) ao invés de **5432** (direto) para melhor performance:
> ```
> postgres://postgres:SuaSenhaAqui@db.xxxxxxxxxxxx.supabase.co:6543/postgres
> ```

---

## Parte 2: Subir o Código para o GitHub

### Passo 2.1 - Criar repositório no GitHub

1. Acesse [https://github.com/new](https://github.com/new)
2. Preencha:
   - **Repository name**: `biblioteca-pessoal`
   - Marque como **Private** (opcional, mas recomendado)
3. Clique em **"Create repository"**

### Passo 2.2 - Fazer upload do código

Na pasta do projeto, execute os comandos abaixo no terminal:

```bash
# Inicializar o repositório Git (se ainda não foi feito)
git init

# Adicionar todos os arquivos
git add .

# Fazer o primeiro commit
git commit -m "Primeiro commit - Biblioteca Pessoal"

# Conectar ao repositório remoto (substitua SEU_USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU_USUARIO/biblioteca-pessoal.git

# Enviar o código
git branch -M main
git push -u origin main
```

---

## Parte 3: Deploy no Render

### Passo 3.1 - Criar conta e conectar GitHub

1. Acesse [https://render.com](https://render.com)
2. Clique em **"Get Started for Free"**
3. Faça login com sua conta do **GitHub**
4. Autorize o Render a acessar seus repositórios

### Passo 3.2 - Criar o Web Service

1. No dashboard do Render, clique em **"New +"** → **"Web Service"**
2. Selecione **"Build and deploy from a Git repository"**
3. Clique em **"Connect"** ao lado do repositório `biblioteca-pessoal`
4. Preencha as configurações:

| Campo | Valor |
|-------|-------|
| **Name** | `biblioteca-pessoal` |
| **Region** | Escolha a mais próxima (ex: Oregon) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

5. Em **Instance Type**, selecione **"Free"**

### Passo 3.3 - Configurar variáveis de ambiente

1. Na mesma página, vá até a seção **"Environment Variables"**
2. Adicione as seguintes variáveis:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Cole a URL do Supabase que você copiou (com a senha substituída) |
| `SECRET_KEY` | Crie uma chave secreta (ex: `minha-chave-super-secreta-123`) |
| `PYTHON_VERSION` | `3.11.0` |

> 💡 **Dica para SECRET_KEY**: Você pode gerar uma chave segura executando no Python:
> ```python
> import secrets
> print(secrets.token_hex(32))
> ```

### Passo 3.4 - Fazer o deploy

1. Clique em **"Create Web Service"**
2. Aguarde o deploy (pode levar 2-5 minutos)
3. Quando aparecer **"Live"** em verde, sua aplicação está no ar! 🎉

---

## Parte 4: Acessar sua Aplicação

Após o deploy, sua aplicação estará disponível em:

```
https://biblioteca-pessoal.onrender.com
```

(O nome exato depende do nome que você escolheu no Render)

---

## 🔧 Solução de Problemas

### Erro: "Internal Server Error"
- Verifique os logs no Render (aba "Logs")
- Confira se a `DATABASE_URL` está correta e com a senha substituída

### Erro: "password authentication failed"
- Verifique se a senha do Supabase está correta na URL
- Não use caracteres especiais como `@`, `#`, `$` na senha

### Banco de dados vazio
- A aplicação cria as tabelas automaticamente no primeiro acesso
- Se não funcionar, verifique os logs do Render

### Aplicação muito lenta para iniciar
- O plano gratuito do Render "hiberna" após 15 minutos sem uso
- A primeira requisição pode levar até 30 segundos para acordar

---

## 📝 Notas Importantes

1. **Plano Gratuito do Render**:
   - A aplicação "dorme" após 15 min de inatividade
   - Limite de 750 horas/mês (suficiente para uso pessoal)

2. **Plano Gratuito do Supabase**:
   - 500MB de armazenamento
   - Pausa após 7 dias sem atividade (pode reativar manualmente)

3. **Atualizações**:
   - Sempre que fizer `git push` para o GitHub, o Render fará deploy automático

---

## ✅ Resumo dos Passos

1. ✅ Criar projeto no Supabase e copiar a URL de conexão
2. ✅ Criar repositório no GitHub e fazer push do código
3. ✅ Criar Web Service no Render conectado ao GitHub
4. ✅ Configurar DATABASE_URL com a URL do Supabase
5. ✅ Aguardar o deploy e acessar sua aplicação!

---

**Boa sorte! 🚀📚**

Se tiver dúvidas, me pergunte que eu te ajudo!
