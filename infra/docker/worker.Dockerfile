FROM rust:1.78-slim AS builder
WORKDIR /app
COPY . .
RUN cargo build --release -p worker

FROM debian:bookworm-slim
COPY --from=builder /app/target/release/worker /usr/local/bin/worker
CMD ["worker"]
