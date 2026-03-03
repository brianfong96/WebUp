FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json ./
COPY apps/pwa-interface/package.json ./apps/pwa-interface/package.json
COPY packages/shared-lib/package.json ./packages/shared-lib/package.json
RUN npm install

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm --workspace apps/pwa-interface run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/apps/pwa-interface/.next ./apps/pwa-interface/.next
COPY --from=build /app/apps/pwa-interface/public ./apps/pwa-interface/public
COPY --from=build /app/apps/pwa-interface/package.json ./apps/pwa-interface/package.json
COPY --from=build /app/node_modules ./node_modules
EXPOSE 3000
CMD ["sh", "-c", "cd /app/apps/pwa-interface && npm run start"]
