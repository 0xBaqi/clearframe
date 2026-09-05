FROM node:22-alpine AS build

WORKDIR /app
COPY apps/web/package.json ./package.json
RUN npm install
COPY apps/web ./
ARG NEXT_PUBLIC_CLEARFRAME_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_CLEARFRAME_API_URL=$NEXT_PUBLIC_CLEARFRAME_API_URL
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app ./
EXPOSE 3000
CMD ["node", "node_modules/next/dist/bin/next", "start", "-p", "3000"]
