# Microsoft 365 MCP Server (Softeria/ms-365-mcp-server)
# Build from source so we can run with --http for backend connectivity.
FROM node:24-alpine AS builder
WORKDIR /app
RUN apk add --no-cache git
RUN git clone --depth 1 https://github.com/Softeria/ms-365-mcp-server.git .
RUN npm i
RUN npm run generate && npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/package*.json /app/
ENV NODE_ENV=production
# Use npm install so lock file sync issues (e.g. upstream) don't break the build
RUN npm i --ignore-scripts --omit=dev
# Default: run with HTTP transport on port 3000 so backend can connect.
EXPOSE 3000
ENTRYPOINT ["node", "dist/index.js", "--http", "3000"]
