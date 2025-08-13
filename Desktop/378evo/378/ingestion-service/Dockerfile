# build stage
FROM golang:1.19-alpine AS builder
WORKDIR /app
COPY . .
RUN go mod download
RUN go build -o /ingestion-service

# final stage
FROM alpine:latest
WORKDIR /
COPY --from=builder /ingestion-service /ingestion-service
EXPOSE 8080
ENTRYPOINT [ "/ingestion-service" ]