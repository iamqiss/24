<div align="center">

```
╔══════════════════════════════════════╗
║                                      ║
║        2  4                          ║
║                                      ║
║   say it. mean it. watch it burn.   ║
║                                      ║
╚══════════════════════════════════════╝
```

**Every post lives for 24 hours. Then it's gone.**

*Built for people who have something to say — not something to archive.*

<br/>

![Status](https://img.shields.io/badge/status-in%20development-black?style=flat-square)
![Rust](https://img.shields.io/badge/rust-1.78+-orange?style=flat-square&logo=rust)
![Blinc](https://img.shields.io/badge/blinc-fork-7a2bff?style=flat-square)
![SurrealDB](https://img.shields.io/badge/surrealdb-3.0-pink?style=flat-square)
![License](https://img.shields.io/badge/license-proprietary-red?style=flat-square)
![Platform](https://img.shields.io/badge/platform-iOS%20%7C%20Android-blue?style=flat-square)

</div>

---

## What is 24?

24 is a social platform where posts expire. Not archived. Not hidden behind a toggle. **Gone.**

You get 24 hours. Say what you mean. Then let it go.

No permanent record. No engagement archaeology. No doomscrolling through someone's timeline from three years ago. Just people, in the present, saying things that matter *right now.*

This is the monorepo for the 24 platform — mobile app (iOS + Android), backend API, real-time infrastructure, and background workers. **The entire stack is Rust.** No JavaScript frameworks. No web runtime overhead. One language, end to end.

---

## The philosophy

> Most social platforms are built around permanence. Your posts stack up. Your history follows you. The pressure to be consistent, curated, and correct compounds over time.
>
> 24 is built around the opposite idea: **presence over permanence.** Speak freely. Connect genuinely. Move on.

---

## Core features

### Free tier
- Post text, images, and media — live for **24 hours**
- Join and participate in **Circles** (interest communities)
- Follow people, get followed, build a real network
- DMs and group messages
- Discover trending topics and people

### 24+ (subscription)
- **Set your own post lifetime** — 48h, 7 days, 30 days, or indefinitely
- **Verified badge** — the blue tick that means something
- **Ghost replies** 👻 — comment on posts without your profile showing
- **Post Vault** — your expired posts live in a private archive only you can see
- **Hearth Themes** — 4+ beautiful app themes beyond the default monochrome
  - `Ember` — warm amber and terracotta
  - `Aurora` — cool teal and deep navy
  - `Dusk` — purple and gold hour
  - `Obsidian` — deep dark, no compromises
- **Custom app icons**
- **Post analytics** — views, reach, saves
- **Scheduled posts**
- **Boosted visibility** — more eyes before the clock runs out
- **Extended character limit**

---

## Tech stack

| Layer | Technology |
|---|---|
| **Mobile UI (iOS + Android)** | [Blinc](https://github.com/project-blinc/Blinc) (forked) — GPU-accelerated reactive UI in Rust |
| **Rendering** | wgpu · Metal (iOS) · Vulkan (Android) |
| **Backend API** | Rust · Axum |
| **Database** | SurrealDB 3.0 |
| **Background jobs** | Rust worker binary |
| **Payments** | RevenueCat |
| **Monorepo** | Cargo workspace |
| **Infra** | Docker · Kubernetes · Terraform |

### Pure Rust, all the way down

There are no web frameworks here. No JavaScript. No React Native. No Expo.

The mobile app is built on a fork of [Blinc](https://blinc.rs) — a GPU-accelerated, reactive UI framework for Rust with fine-grained signals, declarative views, and a wgpu renderer that compiles natively to iOS (Metal/UIKit) and Android (NDK/Vulkan) from a single source tree. Same codebase, same language, two platforms.

The backend is Axum on Rust. The database is SurrealDB 3.0. The worker is a Rust binary. The shared types are Rust crates. The whole thing is one Cargo workspace.

### On the Blinc fork

24 uses a fork of [project-blinc/Blinc](https://github.com/project-blinc/Blinc). The upstream project's current roadmap priorities don't align with what 24 needs right now — specifically around widget completeness and the direction of the Zyntax DSL. Our fork patches directly where needed and stays lean. See [`services/blinc/UPSTREAM_DIFF.md`](./services/blinc/UPSTREAM_DIFF.md) for a running diff of divergences from upstream.

### On SurrealDB 3.0

The social graph (follows, circle membership, relationships between users and content) maps naturally to SurrealDB's multi-model architecture. Graph queries for feed ranking and circle discovery are written in SurrealQL and live in [`services/api/src/db/queries/`](./services/api/src/db/queries/).

---

## Repository structure

```
24/
├── apps/
│   └── mobile/          # Blinc app — iOS + Android from one source tree
├── services/
│   ├── api/             # Core Rust API (Axum)
│   ├── blinc/           # Forked Blinc UI framework
│   └── worker/          # Background jobs (post reaper, feed ranker…)
├── packages/
│   └── core/            # Shared Rust crate — models, utils
├── infra/               # Docker, Kubernetes, Terraform
└── docs/                # Architecture, ADRs, API spec
```

---

## Getting started (contributors)

> **Note:** 24 is not open source. Access to this repository is granted explicitly. If you're reading this, you already know what you're doing here.

### Prerequisites

- Rust 1.78+
- Docker + Docker Compose
- SurrealDB CLI (`surreal` in your PATH)
- Xcode (for iOS builds)
- Android NDK (for Android builds)

### Local development

```bash
# Clone
git clone https://github.com/neoqiss/24.git
cd 24

# Start local infrastructure (SurrealDB, etc.)
docker-compose -f infra/docker/docker-compose.yml up -d

# Run DB migrations
surreal import --conn ws://localhost:8000 \
  --user root --pass root --ns dev --db twentyfour \
  services/api/src/db/migrations/001_init_schema.surql

# Start the API
cargo run -p api

# Build + run mobile (iOS simulator)
cargo run -p mobile --target aarch64-apple-ios-sim

# Build + run mobile (Android emulator)
cargo run -p mobile --target aarch64-linux-android
```

Copy `.env.example` to `.env` and fill in your secrets before running anything.

---

## Architecture decisions

Key decisions are documented as ADRs in [`docs/ADRs/`](./docs/ADRs/):

- [`001-surreal-over-postgres.md`](./docs/ADRs/001-surreal-over-postgres.md)
- [`002-rust-axum-api.md`](./docs/ADRs/002-rust-axum-api.md)
- [`003-24h-expiry-strategy.md`](./docs/ADRs/003-24h-expiry-strategy.md)
- [`004-blinc-over-react-native.md`](./docs/ADRs/004-blinc-over-react-native.md)

---

## The 24h expiry system

Posts are not deleted on a cron schedule. The expiry system works in two parts:

1. **`expiry_worker.rs`** — a background job that runs continuously, querying for posts past their TTL and hard-deleting or vaulting them based on the user's subscription entitlements
2. **`CountdownRing`** — a Blinc component driven by fine-grained signals, reflecting remaining post life in real time via a WebSocket event stream. Posts render differently as they approach expiry. Under 2 hours: the ring turns red.

Paid users with the Vault entitlement have their expired posts moved to a private archive, not deleted. The vault is never surfaced publicly.

---

## Roadmap

- [x] Monorepo scaffold
- [x] SurrealDB schema (v1)
- [ ] Auth (JWT + OAuth)
- [ ] Core feed + post creation
- [ ] 24h expiry worker
- [ ] Real-time WebSocket events
- [ ] Circles
- [ ] DMs + group messaging
- [ ] Subscription + entitlements (RevenueCat)
- [ ] Ghost replies
- [ ] Post Vault
- [ ] Themes + app icons (paid)
- [ ] Verified badge flow
- [ ] App Store + Play Store submission
- [ ] `v1.0.0` 🎯

---

## Contributing

This is a private project. Contributions are by invitation only.

If you've been granted access and want to contribute:

1. Branch off `main` — `feature/your-thing` or `fix/your-thing`
2. Write tests for anything in `services/`
3. Keep Rust code `clippy`-clean (`cargo clippy -- -D warnings`)
4. Open a PR with a clear description of what and why
5. One approval required to merge

---

## License

**Proprietary. All rights reserved.**

Copyright © 2026 Neo Qiss. This software and its source code are the exclusive property of the author. No part of this codebase may be copied, modified, distributed, sublicensed, or used in any form without explicit written permission.

This is not open source. This is not MIT. This is not "feel free to fork."

*If you're here, you were invited. Act accordingly.*

---

<div align="center">

*Built in Johannesburg.*

`"say it. mean it. watch it burn."`

</div>
