# --- Build stage ---
FROM node:20-alpine AS build

# Set INSECURE_TLS=1 at build time if you are behind a TLS-inspecting proxy
# (corporate firewall / antivirus SSL scanning) whose root CA the container
# does not trust. It disables strict SSL for the npm registry only.
ARG INSECURE_TLS=0

WORKDIR /app
COPY package.json package-lock.json* ./
RUN if [ "$INSECURE_TLS" = "1" ]; then npm config set strict-ssl false; fi && \
    npm install
COPY . .
RUN npm run build

# --- Serve stage ---
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
