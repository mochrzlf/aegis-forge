# ==============================================================================
# Aegis Forge — Go Backend Dockerfile (Multi-Stage Production Build)
# ==============================================================================

# Stage 1: Build binary
FROM golang:1.26-alpine AS builder

WORKDIR /app

RUN apk add --no-cache git ca-certificates

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-w -s" -o /app/server ./cmd/server
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-w -s" -o /app/seed ./cmd/seed

# Stage 2: Minimal runtime image
FROM alpine:3.20

WORKDIR /app

RUN apk add --no-cache ca-certificates tzdata

# Create non-root user
RUN addgroup -S aegis && adduser -S aegis -G aegis

COPY --from=builder /app/server /app/server
COPY --from=builder /app/seed /app/seed
COPY --from=builder /app/migrations /app/migrations

USER aegis

EXPOSE 8000

CMD ["/app/server"]
