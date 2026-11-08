FROM node:20-alpine

WORKDIR /app

# Копируем зависимости
COPY package*.json ./
RUN npm install

# Копируем исходники
COPY . .

# Открываем порт Vite
EXPOSE 5174

# Запускаем в режиме разработки с доступом извне
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]