FROM python:3.10-slim

# 1. Instala as ferramentas básicas e certificados (Atualizado)
RUN apt-get update && apt-get install -y wget gnupg unzip curl ca-certificates

# 2. Instala a chave de segurança do Google usando o método NOVO (sem apt-key)
RUN curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# 3. Instala o Google Chrome Oficial
RUN apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configura a pasta do robô
WORKDIR /app

# Copia os arquivos e instala as bibliotecas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Comando para ligar o servidor
CMD ["python", "servidor_api.py"]
