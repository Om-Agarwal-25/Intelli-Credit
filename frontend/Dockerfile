# Intelli-Credit — Frontend Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ENV VITE_API_URL=http://localhost:8000
ENV VITE_WS_URL=ws://localhost:8000
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "--port", "3000"]
