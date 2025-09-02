FROM node:20-alpine
WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy rest of the app
COPY frontend/ ./

EXPOSE 3000

# For preview we just need it to boot; adjust later for prod
CMD ["npm", "run", "dev"]