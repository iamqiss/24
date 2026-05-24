FROM rust:1.78-slim AS builder
WORKDIR /app
COPY . .
RUN cargo build --release -p ops

FROM debian:bookworm-slim
COPY --from=builder /app/target/release/ops /usr/local/bin/ops
CMD ["ops"]
