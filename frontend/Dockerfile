# syntax=docker/dockerfile:1

# ---- Builder: install deps and build the Next.js app ----
FROM node:20-alpine AS builder

# allow npm to write to /app
WORKDIR /app
ENV NODE_ENV=development

# Copy dependency manifests first to leverage Docker layer caching
COPY package*.json ./

# Install all deps (including dev deps) required for building
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build


# ---- Runner: lean runtime image with production deps ----
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Create non-root user for better security
RUN addgroup -S app && adduser -S app -G app

# Copy only package manifests and install production deps
COPY package*.json ./
RUN npm ci --omit=dev

# Copy Next build output and static assets from the builder
COPY --from=builder /app/.next .next
COPY --from=builder /app/public ./public

# Copy any other runtime files that might be needed (e.g. start script)
# package.json is already present; npm start should run `next start` per package scripts.

# Ensure correct permissions for non-root user
RUN chown -R app:app /app
USER app

EXPOSE 3000

# Run the built Next.js app. The project should define "start" (npm start) which runs `next start`.
CMD ["npm", "start"]
