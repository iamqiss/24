# gRPC Guidelines

- All `.proto` definitions live in `/proto/`
- Generated code lives in `packages/proto-gen/` — never edit it by hand
- Never call the DB directly from a gRPC handler — go through `handlers/`
- Streaming RPCs for: messages, notifications, feed updates, ops metrics
- Auth interceptor runs on every RPC — JWT required except Register/Login
