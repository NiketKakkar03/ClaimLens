FROM node:22.14-alpine AS build
WORKDIR /app
ARG VITE_OIDC_URL=http://localhost:8180
ARG VITE_OIDC_REALM=claims-local
ARG VITE_OIDC_CLIENT_ID=claims-reviewer
ENV VITE_OIDC_URL=$VITE_OIDC_URL
ENV VITE_OIDC_REALM=$VITE_OIDC_REALM
ENV VITE_OIDC_CLIENT_ID=$VITE_OIDC_CLIENT_ID
RUN corepack enable && corepack prepare pnpm@10.20.0 --activate
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
