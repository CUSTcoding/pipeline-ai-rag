FROM node:22-slim

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

# Copia todo o projeto do frontend (incluindo node_modules se existir)
COPY apps/frontend ./

# Executa o install apenas se a pasta node_modules não estiver presente
RUN if [ ! -d "node_modules/next" ]; then \
      echo "Next.js não encontrado em node_modules. Executando pnpm install..." && \
      pnpm install --no-frozen-lockfile; \
    else \
      echo "Usando node_modules locais (modo offline)."; \
    fi

RUN npx --no-install next build

EXPOSE 3000

CMD ["npx", "--no-install", "next", "start"]