# Stage 1: Build the React application
FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy the custom Nginx configuration from the project root's nginx directory
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the built static assets from the node stage to Nginx's default public directory
COPY --from=build /app/dist /usr/share/nginx/html

# JMc - 2026-03-18 - Cloud Run dynamically assigns a PORT environment variable (default 8080).
# We must use envsubst to dynamically inject this into the nginx.conf at boot time.
# But first, create a template from the conf we just copied
RUN cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.template

EXPOSE 80
# JMc - [2026-04-03] - Use sh to run envsubst to inject both PORT and BACKEND_URL before starting nginx.
CMD ["sh", "-c", "envsubst '${PORT} ${BACKEND_URL}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]
