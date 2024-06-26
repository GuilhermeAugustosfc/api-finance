# Use uma imagem de Python como base
FROM --platform=linux/amd64 python:3.9-slim AS api

# Instale o ffmpeg
RUN apt-get update && apt-get install -y ffmpeg flac

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de requisitos para o contêiner
COPY requirements.txt requirements.txt

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o conteúdo do diretório atual para o contêiner
COPY . .

# Exponha a porta em que sua aplicação FastAPI estará rodando
EXPOSE 8000

# Defina a variável de ambiente para a conexão com o MongoDB
ENV MONGO_URI="mongodb+srv://guilhermeaugustosfc1:aIVlKXsQV0FNC3Pu@cluster0.yiwrufx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true"
ENV MYSQL_ROOT_PASSWORD="SO9yvDX5GwQfF1EWEM5u"
ENV MYSQL_DATABASE="teste"
ENV MYSQL_USER="admin"
ENV MYSQL_PASSWORD="SO9yvDX5GwQfF1EWEM5u"

# Comando para executar a sua aplicação FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]
