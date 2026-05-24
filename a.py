#!/usr/bin/env python3
"""
24 (codename: Hearth) — Project Scaffold
=========================================
Run this from the root of your repo (where README.md lives).
It will create the full monorepo structure with stub files.

    python3 scaffold.py

Nothing is overwritten — existing files are left untouched.
"""

import os
import sys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def mkdir(path):
    os.makedirs(path, exist_ok=True)

def write(path, content=""):
    if os.path.exists(path):
        return  # never overwrite
    mkdir(os.path.dirname(path))
    with open(path, "w") as f:
        f.write(content)

def touch(path):
    write(path, "")

def gitkeep(path):
    mkdir(path)
    touch(os.path.join(path, ".gitkeep"))


# ---------------------------------------------------------------------------
# Stub generators
# ---------------------------------------------------------------------------

def rs(comment):
    return f"// {comment}\n"

def rs_mod(*modules):
    lines = ["// Module declarations\n"]
    for m in modules:
        lines.append(f"pub mod {m};\n")
    return "".join(lines)

def proto(service, rpcs):
    lines = [
        'syntax = "proto3";\n\n',
        f'package twentyfour.{service.lower()};\n\n',
        'option java_package = "app.twentyfour.proto";\n\n',
        f'service {service}Service {{\n',
    ]
    for rpc, req, res in rpcs:
        lines.append(f'  rpc {rpc} ({req}) returns ({res});\n')
    lines.append('}\n\n')
    lines.append('// TODO: define request / response messages\n')
    return "".join(lines)

def surql(comment):
    return f"-- {comment}\n"

def cargo_workspace(members):
    lines = [
        '[workspace]\n',
        'resolver = "2"\n\n',
        'members = [\n',
    ]
    for m in members:
        lines.append(f'    "{m}",\n')
    lines += [
        ']\n\n',
        '[workspace.dependencies]\n',
        'tokio              = { version = "1", features = ["full"] }\n',
        'tonic              = "0.12"\n',
        'prost              = "0.13"\n',
        'tonic-build        = "0.12"\n',
        'axum               = "0.7"\n',
        'surrealdb          = "3"\n',
        'serde              = { version = "1", features = ["derive"] }\n',
        'serde_json         = "1"\n',
        'anyhow             = "1"\n',
        'thiserror          = "1"\n',
        'tracing            = "0.1"\n',
        'tracing-subscriber = "0.3"\n',
        'uuid               = { version = "1", features = ["v4", "serde"] }\n',
        'chrono             = { version = "0.4", features = ["serde"] }\n',
        'blinc_app          = "0.5"\n',
        'blinc_layout       = "0.5"\n',
        'blinc_animation    = "0.5"\n',
        'blinc_gpu          = "0.5"\n',
        'blinc_theme        = "0.5"\n',
        'blinc_cn           = "0.5"\n',
        'blinc_platform     = "0.5"\n',
    ]
    return "".join(lines)

def cargo_pkg(name, deps=None, bin_name=None):
    lines = [
        '[package]\n',
        f'name    = "{name}"\n',
        'version = "0.1.0"\n',
        'edition = "2021"\n\n',
    ]
    if bin_name:
        lines += ['[[bin]]\n', f'name = "{bin_name}"\n', 'path = "src/main.rs"\n\n']
    lines.append('[dependencies]\n')
    if deps:
        for d in deps:
            lines.append(f'{d}\n')
    return "".join(lines)

def dockerfile(binary):
    return (
        'FROM rust:1.78-slim AS builder\n'
        'WORKDIR /app\nCOPY . .\n'
        f'RUN cargo build --release -p {binary}\n\n'
        'FROM debian:bookworm-slim\n'
        f'COPY --from=builder /app/target/release/{binary} /usr/local/bin/{binary}\n'
        f'CMD ["{binary}"]\n'
    )

def docker_compose():
    return """\
version: "3.9"

services:
  surrealdb:
    image: surrealdb/surrealdb:latest
    command: start --log trace --user root --pass root memory
    ports:
      - "8000:8000"

  api:
    build:
      context: .
      dockerfile: infra/docker/api.Dockerfile
    env_file: .env
    ports:
      - "50051:50051"   # gRPC
      - "8080:8080"     # HTTP  (health + webhooks)
    depends_on:
      - surrealdb

  worker:
    build:
      context: .
      dockerfile: infra/docker/worker.Dockerfile
    env_file: .env
    depends_on:
      - surrealdb
      - api

  ops:
    build:
      context: .
      dockerfile: infra/docker/ops.Dockerfile
    env_file: .env
    ports:
      - "9000:9000"
    depends_on:
      - api
"""

def env_example():
    return """\
# ── Server ──────────────────────────────────────────────
SERVER_HOST=0.0.0.0
GRPC_PORT=50051
HTTP_PORT=8080

# ── SurrealDB ────────────────────────────────────────────
SURREAL_URL=ws://localhost:8000
SURREAL_USER=root
SURREAL_PASS=root
SURREAL_NS=dev
SURREAL_DB=twentyfour

# ── Auth ─────────────────────────────────────────────────
JWT_SECRET=change_me_in_production
JWT_EXPIRY_SECONDS=3600

# ── RevenueCat ───────────────────────────────────────────
REVENUECAT_SECRET_KEY=
REVENUECAT_WEBHOOK_AUTH=

# ── Push Notifications ───────────────────────────────────
APNS_KEY_ID=
APNS_TEAM_ID=
APNS_KEY_PATH=./infra/certs/apns.p8
FCM_SERVER_KEY=

# ── Ops Dashboard ────────────────────────────────────────
OPS_DASHBOARD_SECRET=change_me
OPS_DASHBOARD_HOST=0.0.0.0
OPS_DASHBOARD_PORT=9000

# ── Object Storage ───────────────────────────────────────
S3_BUCKET=
S3_REGION=
S3_ACCESS_KEY=
S3_SECRET_KEY=
CDN_BASE_URL=

# ── Moderation ───────────────────────────────────────────
AUTOMOD_THRESHOLD_SCORE=0.85
AUTOMOD_ENABLED=true
SHADOWBAN_ENABLED=true

# ── Feature Flags ────────────────────────────────────────
ENABLE_GHOST_REPLIES=true
ENABLE_VAULT=true
ENABLE_BOOST=true

# ── Observability ────────────────────────────────────────
SENTRY_DSN=
JAEGER_ENDPOINT=
"""

def github_ci():
    return """\
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo clippy --all -- -D warnings
      - run: cargo test --all
      - run: cargo fmt --all -- --check
"""


# ---------------------------------------------------------------------------
# Scaffold
# ---------------------------------------------------------------------------

def scaffold(root):
    print(f"\n🔥  Scaffolding 24 (codename: Hearth)")
    print(f"    Root: {os.path.abspath(root)}\n")

    # ── .github ────────────────────────────────────────────────────────────
    write(f"{root}/.github/workflows/ci.yml",             github_ci())
    write(f"{root}/.github/workflows/deploy-staging.yml", "# TODO: staging deploy\n")
    write(f"{root}/.github/workflows/deploy-prod.yml",    "# TODO: prod deploy\n")
    write(f"{root}/.github/CODEOWNERS",                   "* @neoqiss\n")
    write(f"{root}/.github/pull_request_template.md",
          "## What\n\n## Why\n\n## Notes\n")

    # ── Root files ─────────────────────────────────────────────────────────
    write(f"{root}/Cargo.toml", cargo_workspace([
        "apps/mobile",
        "apps/ops",
        "services/api",
        "services/worker",
        "services/blinc",
        "packages/core",
        "packages/proto-gen",
    ]))
    write(f"{root}/.env.example",      env_example())
    write(f"{root}/.gitignore",
          "target/\n.env\n*.pem\n*.p8\n*.key\ndist/\n")
    write(f"{root}/rust-toolchain.toml",
          '[toolchain]\nchannel = "stable"\n')

    # ── proto/ ─────────────────────────────────────────────────────────────
    write(f"{root}/proto/auth.proto", proto("Auth", [
        ("Register",      "RegisterRequest",      "RegisterResponse"),
        ("Login",         "LoginRequest",         "LoginResponse"),
        ("RefreshToken",  "RefreshTokenRequest",  "RefreshTokenResponse"),
        ("Logout",        "LogoutRequest",        "LogoutResponse"),
        ("OAuthCallback", "OAuthCallbackRequest", "OAuthCallbackResponse"),
        ("DeleteAccount", "DeleteAccountRequest", "DeleteAccountResponse"),
    ]))
    write(f"{root}/proto/users.proto", proto("Users", [
        ("GetProfile",    "GetProfileRequest",    "UserProfile"),
        ("UpdateProfile", "UpdateProfileRequest", "UserProfile"),
        ("FollowUser",    "FollowRequest",        "FollowResponse"),
        ("UnfollowUser",  "UnfollowRequest",      "UnfollowResponse"),
        ("GetFollowers",  "GetFollowersRequest",  "UserListResponse"),
        ("GetFollowing",  "GetFollowingRequest",  "UserListResponse"),
        ("BlockUser",     "BlockRequest",         "BlockResponse"),
        ("UnblockUser",   "UnblockRequest",       "UnblockResponse"),
        ("MuteUser",      "MuteRequest",          "MuteResponse"),
        ("ReportUser",    "ReportRequest",        "ReportResponse"),
        ("SearchUsers",   "SearchRequest",        "UserListResponse"),
        ("GetSuggested",  "SuggestRequest",       "UserListResponse"),
    ]))
    write(f"{root}/proto/posts.proto", proto("Posts", [
        ("CreatePost",   "CreatePostRequest",   "Post"),
        ("GetPost",      "GetPostRequest",      "Post"),
        ("DeletePost",   "DeletePostRequest",   "DeleteResponse"),
        ("GetFeed",      "GetFeedRequest",      "FeedResponse"),
        ("LikePost",     "LikeRequest",         "LikeResponse"),
        ("DislikePost",  "DislikeRequest",      "DislikeResponse"),
        ("RepostPost",   "RepostRequest",       "RepostResponse"),
        ("BookmarkPost", "BookmarkRequest",     "BookmarkResponse"),
        ("GetPostStats", "GetPostStatsRequest", "PostStats"),
        ("BoostPost",    "BoostRequest",        "BoostResponse"),
        ("StreamFeed",   "StreamFeedRequest",   "stream FeedEvent"),
    ]))
    write(f"{root}/proto/comments.proto", proto("Comments", [
        ("CreateComment", "CreateCommentRequest", "Comment"),
        ("DeleteComment", "DeleteCommentRequest", "DeleteResponse"),
        ("GetComments",   "GetCommentsRequest",   "CommentListResponse"),
        ("GhostReply",    "GhostReplyRequest",    "Comment"),
        ("LikeComment",   "LikeCommentRequest",   "LikeResponse"),
        ("ReportComment", "ReportCommentRequest", "ReportResponse"),
    ]))
    write(f"{root}/proto/circles.proto", proto("Circles", [
        ("CreateCircle",  "CreateCircleRequest",  "Circle"),
        ("GetCircle",     "GetCircleRequest",     "Circle"),
        ("UpdateCircle",  "UpdateCircleRequest",  "Circle"),
        ("DeleteCircle",  "DeleteCircleRequest",  "DeleteResponse"),
        ("JoinCircle",    "JoinCircleRequest",    "JoinResponse"),
        ("LeaveCircle",   "LeaveCircleRequest",   "LeaveResponse"),
        ("GetCircleFeed", "GetCircleFeedRequest", "FeedResponse"),
        ("SearchCircles", "SearchCirclesRequest", "CircleListResponse"),
        ("BanMember",     "BanMemberRequest",     "BanResponse"),
        ("GetMembers",    "GetMembersRequest",    "UserListResponse"),
    ]))
    write(f"{root}/proto/messages.proto", proto("Messages", [
        ("SendMessage",      "SendMessageRequest",      "Message"),
        ("GetConversation",  "GetConversationRequest",  "ConversationResponse"),
        ("GetConversations", "GetConversationsRequest", "ConversationListResponse"),
        ("CreateGroupChat",  "CreateGroupChatRequest",  "Conversation"),
        ("DeleteMessage",    "DeleteMessageRequest",    "DeleteResponse"),
        ("MarkRead",         "MarkReadRequest",         "MarkReadResponse"),
        ("StreamMessages",   "StreamMessagesRequest",   "stream Message"),
        ("ReactToMessage",   "ReactRequest",            "ReactResponse"),
    ]))
    write(f"{root}/proto/notifications.proto", proto("Notifications", [
        ("GetNotifications",    "GetNotificationsRequest", "NotificationListResponse"),
        ("MarkRead",            "MarkReadRequest",         "MarkReadResponse"),
        ("StreamNotifications", "StreamRequest",           "stream Notification"),
        ("UpdatePreferences",   "UpdatePrefRequest",       "NotificationPrefs"),
        ("ClearAll",            "ClearAllRequest",         "ClearAllResponse"),
    ]))
    write(f"{root}/proto/search.proto", proto("Search", [
        ("Search",       "SearchRequest",      "SearchResponse"),
        ("Trending",     "TrendingRequest",    "TrendingResponse"),
        ("Suggestions",  "SuggestRequest",     "SuggestResponse"),
        ("NearbyUsers",  "NearbyRequest",      "UserListResponse"),
    ]))
    write(f"{root}/proto/subscriptions.proto", proto("Subscriptions", [
        ("GetEntitlements",   "GetEntitlementsRequest",   "Entitlements"),
        ("ValidateReceipt",   "ValidateReceiptRequest",   "ValidateResponse"),
        ("WebhookRevenueCat", "WebhookRequest",           "WebhookResponse"),
        ("GetPlans",          "GetPlansRequest",          "PlansResponse"),
        ("CancelSubscription","CancelRequest",            "CancelResponse"),
    ]))
    write(f"{root}/proto/media.proto", proto("Media", [
        ("RequestUploadUrl", "UploadUrlRequest",    "UploadUrlResponse"),
        ("ConfirmUpload",    "ConfirmUploadRequest","ConfirmUploadResponse"),
        ("DeleteMedia",      "DeleteMediaRequest",  "DeleteResponse"),
        ("GetMediaInfo",     "MediaInfoRequest",    "MediaInfo"),
    ]))
    write(f"{root}/proto/moderation.proto", proto("Moderation", [
        ("ReportContent",   "ReportContentRequest",  "ReportResponse"),
        ("ReviewReport",    "ReviewReportRequest",   "ReviewResponse"),
        ("BanUser",         "BanUserRequest",        "BanResponse"),
        ("UnbanUser",       "UnbanUserRequest",      "UnbanResponse"),
        ("ShadowbanUser",   "ShadowbanRequest",      "ShadowbanResponse"),
        ("GetReportQueue",  "ReportQueueRequest",    "ReportQueueResponse"),
        ("AutoModDecision", "AutoModRequest",        "AutoModResponse"),
        ("AppealDecision",  "AppealRequest",         "AppealResponse"),
        ("GetActionHistory","ActionHistoryRequest",  "ActionHistoryResponse"),
        ("FlagContent",     "FlagContentRequest",    "FlagResponse"),
    ]))
    write(f"{root}/proto/ops.proto", proto("Ops", [
        ("GetDashboardStats",  "DashboardStatsRequest", "DashboardStats"),
        ("GetUserDetail",      "UserDetailRequest",     "UserDetail"),
        ("GetReportQueue",     "OpsReportQueueRequest", "OpsReportQueueResponse"),
        ("GetAuditLog",        "AuditLogRequest",       "AuditLogResponse"),
        ("GetSystemHealth",    "HealthRequest",         "HealthResponse"),
        ("TakeAction",         "TakeActionRequest",     "TakeActionResponse"),
        ("GetActiveIncidents", "IncidentRequest",       "IncidentListResponse"),
        ("CreateIncident",     "CreateIncidentRequest", "Incident"),
        ("ResolveIncident",    "ResolveIncidentRequest","Incident"),
        ("GetMetrics",         "MetricsRequest",        "MetricsResponse"),
        ("StreamMetrics",      "StreamMetricsRequest",  "stream MetricEvent"),
        ("GetFeatureFlags",    "FeatureFlagsRequest",   "FeatureFlags"),
        ("SetFeatureFlag",     "SetFeatureFlagRequest", "FeatureFlag"),
        ("GetOpsUsers",        "OpsUsersRequest",       "OpsUsersResponse"),
        ("CreateOpsUser",      "CreateOpsUserRequest",  "OpsUser"),
    ]))

    # ── packages/proto-gen ─────────────────────────────────────────────────
    pg = f"{root}/packages/proto-gen"
    write(f"{pg}/Cargo.toml", cargo_pkg("proto-gen", deps=[
        "prost.workspace = true",
        "tonic.workspace = true",
    ]))
    write(f"{pg}/build.rs",
        'fn main() -> Result<(), Box<dyn std::error::Error>> {\n'
        '    let protos = &[\n'
        '        "../../proto/auth.proto",\n'
        '        "../../proto/users.proto",\n'
        '        "../../proto/posts.proto",\n'
        '        "../../proto/comments.proto",\n'
        '        "../../proto/circles.proto",\n'
        '        "../../proto/messages.proto",\n'
        '        "../../proto/notifications.proto",\n'
        '        "../../proto/search.proto",\n'
        '        "../../proto/subscriptions.proto",\n'
        '        "../../proto/media.proto",\n'
        '        "../../proto/moderation.proto",\n'
        '        "../../proto/ops.proto",\n'
        '    ];\n'
        '    tonic_build::configure()\n'
        '        .build_server(true)\n'
        '        .build_client(true)\n'
        '        .compile_protos(protos, &["../../proto"])?;\n'
        '    Ok(())\n'
        '}\n'
    )
    write(f"{pg}/src/lib.rs",
        rs("Re-exports all tonic-generated gRPC types") +
        "\n// tonic::include_proto!(\"twentyfour.auth\");\n"
        "// Uncomment each as you add protos to build.rs\n"
    )

    # ── packages/core ──────────────────────────────────────────────────────
    pc = f"{root}/packages/core"
    write(f"{pc}/Cargo.toml", cargo_pkg("core", deps=[
        "serde.workspace      = true",
        "serde_json.workspace = true",
        "uuid.workspace       = true",
        "chrono.workspace     = true",
        "anyhow.workspace     = true",
        "thiserror.workspace  = true",
    ]))
    write(f"{pc}/src/lib.rs", rs_mod(
        "models", "errors", "utils", "constants", "entitlements"
    ))
    write(f"{pc}/src/models/mod.rs", rs_mod(
        "user", "post", "circle", "message",
        "notification", "subscription", "report", "media", "audit"
    ))
    for m in ["user", "post", "circle", "message", "notification",
              "subscription", "report", "media", "audit"]:
        write(f"{pc}/src/models/{m}.rs", rs(f"{m} domain model"))
    write(f"{pc}/src/errors.rs",      rs("AppError, ApiError, DbError"))
    write(f"{pc}/src/utils.rs",       rs("Shared utils — pagination, hashing, time"))
    write(f"{pc}/src/entitlements.rs",rs("Plan → feature flag map. Always checked server-side."))
    write(f"{pc}/src/constants.rs",
        "pub const POST_TTL_SECS_FREE: u64   = 86_400;     // 24 h\n"
        "pub const POST_TTL_SECS_MAX:  u64   = 2_592_000;  // 30 days\n"
        "pub const POST_LEN_FREE:      usize = 500;\n"
        "pub const POST_LEN_PAID:      usize = 2_000;\n"
        "pub const FREE_CIRCLE_LIMIT:  u32   = 2;\n"
    )

    # ── services/blinc fork ────────────────────────────────────────────────
    sb = f"{root}/services/blinc"
    write(f"{sb}/Cargo.toml", cargo_pkg("blinc-fork", deps=[
        "blinc_app.workspace       = true",
        "blinc_layout.workspace    = true",
        "blinc_animation.workspace = true",
        "blinc_gpu.workspace       = true",
        "blinc_theme.workspace     = true",
    ]))
    write(f"{sb}/UPSTREAM_DIFF.md",
        "# Upstream Diff\n\n"
        "Track every divergence from project-blinc/Blinc here.\n\n"
        "## Patches\n\n- (none yet)\n"
    )
    write(f"{sb}/src/lib.rs",
        rs_mod("hearth_patches", "theme_ext", "expiry_ring", "ops_widgets"))
    write(f"{sb}/src/hearth_patches/mod.rs",
        rs_mod("state_hooks", "animation_ext", "platform_ext"))
    write(f"{sb}/src/hearth_patches/state_hooks.rs",
        rs("Extended state hook patterns for feed + expiry countdown"))
    write(f"{sb}/src/hearth_patches/animation_ext.rs",
        rs("Extra spring configs for countdown ring and post decay animations"))
    write(f"{sb}/src/hearth_patches/platform_ext.rs",
        rs("Platform-specific patches for iOS/Android targets"))
    write(f"{sb}/src/theme_ext.rs",   rs("Hearth theme tokens on top of blinc_theme"))
    write(f"{sb}/src/expiry_ring.rs", rs("CountdownRing — GPU-rendered, signal-driven, wgpu"))
    write(f"{sb}/src/ops_widgets.rs", rs("Ops-specific widgets: KPI card, severity badge, live ticker"))

    # ── apps/mobile ────────────────────────────────────────────────────────
    am = f"{root}/apps/mobile"
    write(f"{am}/Cargo.toml", cargo_pkg("mobile", deps=[
        "blinc_app.workspace            = true",
        "blinc_layout.workspace         = true",
        "blinc_animation.workspace      = true",
        "blinc_gpu.workspace            = true",
        "blinc_theme.workspace          = true",
        "blinc_cn.workspace             = true",
        "blinc_platform.workspace       = true",
        'blinc_platform_ios     = { version = "0.5", optional = true }',
        'blinc_platform_android = { version = "0.5", optional = true }',
        'blinc-fork  = { path = "../../services/blinc" }',
        'proto-gen   = { path = "../../packages/proto-gen" }',
        'core        = { path = "../../packages/core" }',
        "tonic.workspace  = true",
        "tokio.workspace  = true",
        "serde.workspace  = true",
        "uuid.workspace   = true",
        "anyhow.workspace = true",
    ]))

    s = f"{am}/src"
    write(f"{s}/main.rs",
        "use blinc_app::prelude::*;\n"
        "use blinc_app::windowed::WindowedApp;\n\n"
        "mod app;\nmod router;\nmod state;\nmod theme;\nmod grpc;\n"
        "mod screens;\nmod components;\n\n"
        "fn main() -> anyhow::Result<()> {\n"
        "    WindowedApp::run(Default::default(), |ctx| app::root(ctx))\n"
        "}\n"
    )
    write(f"{s}/app.rs",    rs("Root app shell — wraps theme provider + router"))
    write(f"{s}/router.rs", rs("Screen stack router"))

    # state
    write(f"{s}/state/mod.rs", rs_mod(
        "auth", "feed", "user", "subscription", "theme", "notifications", "search"
    ))
    for st in ["auth", "feed", "user", "subscription", "theme", "notifications", "search"]:
        write(f"{s}/state/{st}.rs", rs(f"{st} reactive state — fine-grained signals"))

    # theme
    write(f"{s}/theme/mod.rs", rs_mod(
        "monochrome", "ember", "aurora", "dusk", "obsidian", "tokens"
    ))
    write(f"{s}/theme/tokens.rs", rs("Shared design tokens — spacing, radius, type scale"))
    for t in ["monochrome", "ember", "aurora", "dusk", "obsidian"]:
        write(f"{s}/theme/{t}.rs", rs(f"{t} palette + material definitions"))

    # grpc client
    write(f"{s}/grpc/mod.rs", rs_mod(
        "client", "auth", "posts", "comments", "users", "circles",
        "messages", "notifications", "search", "subscriptions", "media"
    ))
    write(f"{s}/grpc/client.rs", rs("tonic channel, auth interceptor, retry config"))
    for svc in ["auth", "posts", "comments", "users", "circles",
                "messages", "notifications", "search", "subscriptions", "media"]:
        write(f"{s}/grpc/{svc}.rs", rs(f"gRPC client wrapper — {svc}"))

    # screens
    screens = {
        "auth":          ["login", "register", "onboarding", "forgot_password"],
        "feed":          ["home", "discover", "trending"],
        "post":          ["detail", "create", "composer", "boost"],
        "circles":       ["list", "detail", "explore", "create", "settings"],
        "profile":       ["view", "edit", "visitor", "vault", "followers", "following"],
        "messages":      ["inbox", "conversation", "group_chat", "new_conversation"],
        "notifications": ["list"],
        "search":        ["index", "results", "people", "topics"],
        "settings": [
            "index", "account", "appearance",
            "notifications_prefs", "subscription",
            "privacy", "blocked", "muted",
        ],
    }
    write(f"{s}/screens/mod.rs", rs_mod(*screens.keys()))
    for screen, views in screens.items():
        write(f"{s}/screens/{screen}/mod.rs", rs_mod(*views))
        for v in views:
            write(f"{s}/screens/{screen}/{v}.rs", rs(f"screen: {screen}/{v}"))

    # components
    comps = {
        "ui": [
            "button", "avatar", "badge", "verified_badge",
            "ghost_badge", "sheet", "modal", "toast", "skeleton",
            "chip", "divider", "icon", "text_input", "spinner",
        ],
        "feed": [
            "post_card", "post_card_expiring", "feed_list",
            "story_bar", "countdown_ring", "boost_badge", "expiry_glow",
        ],
        "post":     ["post_actions", "post_media", "post_header", "reply_composer"],
        "circles":  ["circle_card", "circle_header", "join_button", "member_list"],
        "profile":  ["profile_header", "stats_row", "post_grid", "vault_grid", "bio"],
        "messaging":["chat_bubble", "conversation_row", "message_input", "typing_indicator", "reaction_bar"],
        "modals":   ["report_modal", "paywall_modal", "theme_picker", "icon_picker", "confirm_dialog"],
        "paywall":  ["feature_gate", "plan_card", "cta_banner"],
    }
    write(f"{s}/components/mod.rs", rs_mod(*comps.keys()))
    for group, items in comps.items():
        write(f"{s}/components/{group}/mod.rs", rs_mod(*items))
        for item in items:
            write(f"{s}/components/{group}/{item}.rs", rs(f"{item} component"))

    gitkeep(f"{am}/assets/icons/app_icons")
    gitkeep(f"{am}/assets/fonts")
    gitkeep(f"{am}/assets/images")

    # ── apps/ops  (internal ops dashboard — Blinc desktop) ─────────────────
    ao = f"{root}/apps/ops"
    write(f"{ao}/Cargo.toml", cargo_pkg("ops", bin_name="ops", deps=[
        "blinc_app.workspace            = true",
        "blinc_layout.workspace         = true",
        "blinc_animation.workspace      = true",
        "blinc_gpu.workspace            = true",
        "blinc_theme.workspace          = true",
        "blinc_cn.workspace             = true",
        'blinc_platform_desktop = "0.5"',
        'blinc-fork  = { path = "../../services/blinc" }',
        'proto-gen   = { path = "../../packages/proto-gen" }',
        'core        = { path = "../../packages/core" }',
        "tonic.workspace  = true",
        "tokio.workspace  = true",
        "serde.workspace  = true",
        "anyhow.workspace = true",
    ]))

    os_ = f"{ao}/src"
    write(f"{os_}/main.rs",
        "use blinc_app::prelude::*;\n"
        "use blinc_app::windowed::{{WindowedApp, WindowConfig}};\n\n"
        "mod app;\nmod router;\nmod state;\nmod grpc;\nmod theme;\n"
        "mod screens;\nmod components;\n\n"
        "fn main() -> anyhow::Result<()> {\n"
        "    WindowedApp::run(\n"
        "        WindowConfig {\n"
        '            title: "24 — Ops Dashboard".into(),\n'
        "            width:  1440.0,\n"
        "            height:  900.0,\n"
        "            ..Default::default()\n"
        "        },\n"
        "        |ctx| app::root(ctx),\n"
        "    )\n"
        "}\n"
    )
    write(f"{os_}/app.rs",    rs("Ops root — sidebar nav + main content panel"))
    write(f"{os_}/router.rs", rs("Ops page router"))
    write(f"{os_}/theme.rs",  rs("Ops theme — dark, high-density, data-forward"))

    # ops state
    write(f"{os_}/state/mod.rs", rs_mod(
        "auth", "dashboard", "reports", "users",
        "audit", "incidents", "metrics", "flags"
    ))
    for st in ["auth", "dashboard", "reports", "users",
               "audit", "incidents", "metrics", "flags"]:
        write(f"{os_}/state/{st}.rs", rs(f"ops {st} state"))

    # ops grpc
    write(f"{os_}/grpc/mod.rs", rs_mod(
        "client", "ops", "users", "moderation", "subscriptions"
    ))
    write(f"{os_}/grpc/client.rs", rs("tonic channel — ops dashboard → API (ops role JWT)"))
    for svc in ["ops", "users", "moderation", "subscriptions"]:
        write(f"{os_}/grpc/{svc}.rs", rs(f"ops gRPC client — {svc}"))

    # ops screens
    ops_screens = {
        "auth":       ["login", "mfa"],
        "dashboard":  ["overview"],
        "users": [
            "list", "detail", "search",
            "ban_history", "appeal_list", "risk_queue",
        ],
        "reports": [
            "queue", "detail", "resolved",
            "escalated", "bulk_review",
        ],
        "moderation": [
            "content_queue", "auto_mod_log", "appeals",
            "shadowban_list", "action_history",
            "rule_editor", "keyword_lists",
        ],
        "incidents":  ["list", "detail", "create", "postmortem"],
        "audit_log":  ["list", "detail"],
        "metrics": [
            "growth", "engagement", "revenue",
            "content_health", "realtime", "retention",
        ],
        "settings": [
            "index", "ops_users", "feature_flags",
            "automod_thresholds", "notification_config",
        ],
    }
    write(f"{os_}/screens/mod.rs", rs_mod(*ops_screens.keys()))
    for screen, views in ops_screens.items():
        write(f"{os_}/screens/{screen}/mod.rs", rs_mod(*views))
        for v in views:
            write(f"{os_}/screens/{screen}/{v}.rs", rs(f"ops screen: {screen}/{v}"))

    # ops components
    ops_comps = {
        "layout": [
            "sidebar", "topbar", "panel",
            "breadcrumb", "status_bar", "split_pane",
        ],
        "ui": [
            "button", "table", "badge", "stat_card",
            "chart", "alert", "modal", "toast", "avatar",
            "search_bar", "pagination", "empty_state",
            "loading", "tag", "tooltip", "dropdown",
        ],
        "reports": [
            "report_card", "report_detail", "action_toolbar",
            "severity_badge", "decision_panel", "evidence_viewer",
        ],
        "users": [
            "user_row", "user_detail_panel", "risk_score_badge",
            "account_flags", "activity_timeline", "device_list",
        ],
        "moderation": [
            "content_preview", "mod_action_panel",
            "auto_mod_rule_card", "appeal_card",
            "bulk_action_bar", "keyword_tag",
        ],
        "metrics": [
            "kpi_card", "time_series_chart", "funnel_chart",
            "heatmap", "realtime_ticker", "cohort_table",
        ],
        "incidents": [
            "incident_card", "severity_indicator",
            "timeline", "responder_list", "impact_summary",
        ],
    }
    write(f"{os_}/components/mod.rs", rs_mod(*ops_comps.keys()))
    for group, items in ops_comps.items():
        write(f"{os_}/components/{group}/mod.rs", rs_mod(*items))
        for item in items:
            write(f"{os_}/components/{group}/{item}.rs", rs(f"ops {item}"))

    # ── services/api ──────────────────────────────────────────────────────
    sa = f"{root}/services/api"
    write(f"{sa}/Cargo.toml", cargo_pkg("api", bin_name="api", deps=[
        "axum.workspace              = true",
        "tonic.workspace             = true",
        "prost.workspace             = true",
        "tokio.workspace             = true",
        "surrealdb.workspace         = true",
        "serde.workspace             = true",
        "serde_json.workspace        = true",
        "anyhow.workspace            = true",
        "thiserror.workspace         = true",
        "tracing.workspace           = true",
        "tracing-subscriber.workspace= true",
        "uuid.workspace              = true",
        "chrono.workspace            = true",
        'proto-gen = { path = "../../packages/proto-gen" }',
        'core      = { path = "../../packages/core" }',
    ]))

    a = f"{sa}/src"
    write(f"{a}/main.rs",
        "mod config;\nmod db;\nmod auth;\nmod grpc;\nmod handlers;\n"
        "mod models;\nmod payments;\nmod search;\nmod notifications;\n"
        "mod realtime;\nmod moderation;\nmod errors;\n\n"
        "#[tokio::main]\nasync fn main() -> anyhow::Result<()> {\n"
        "    tracing_subscriber::init();\n"
        "    let cfg = config::Config::from_env()?;\n"
        "    let db  = db::connect(&cfg).await?;\n"
        "    grpc::serve(cfg, db).await\n"
        "}\n"
    )
    write(f"{a}/config.rs", rs("Config from env — ports, secrets, feature flags"))
    write(f"{a}/errors.rs", rs("AppError — maps to tonic Status codes"))

    # db
    write(f"{a}/db/mod.rs",        rs_mod("surreal", "migrations"))
    write(f"{a}/db/surreal.rs",    rs("SurrealDB 3.0 client + pool"))
    write(f"{a}/db/migrations.rs", rs("Run .surql migrations on startup"))
    for q in ["feed", "posts", "users", "graph", "circles",
              "messages", "search", "moderation", "audit"]:
        write(f"{a}/db/queries/{q}.surql", surql(f"{q} queries"))
    for m in ["001_init_schema", "002_subscriptions", "003_ghost_replies",
              "004_vault", "005_moderation", "006_audit_log", "007_search_index"]:
        write(f"{a}/db/migrations/{m}.surql", surql(f"migration: {m}"))

    # auth
    write(f"{a}/auth/mod.rs",        rs_mod("jwt", "oauth", "middleware", "password"))
    write(f"{a}/auth/jwt.rs",        rs("JWT issue + verify"))
    write(f"{a}/auth/oauth.rs",      rs("OAuth2 — Apple, Google"))
    write(f"{a}/auth/middleware.rs", rs("tonic interceptor — JWT on every RPC"))
    write(f"{a}/auth/password.rs",   rs("argon2 hashing"))

    # grpc service impls
    grpc_svcs = [
        "auth", "users", "posts", "comments", "circles",
        "messages", "notifications", "search",
        "subscriptions", "media", "moderation", "ops",
    ]
    write(f"{a}/grpc/mod.rs",    rs_mod("server", *grpc_svcs))
    write(f"{a}/grpc/server.rs", rs("Assemble all gRPC services + serve on port"))
    for svc in grpc_svcs:
        write(f"{a}/grpc/{svc}.rs", rs(f"tonic service impl — {svc}"))

    # handlers (business logic)
    handlers = [
        "feed", "post_expiry", "ghost_reply", "vault",
        "verification", "boost", "report", "shadowban",
        "auto_mod", "appeal", "content_pipeline",
    ]
    write(f"{a}/handlers/mod.rs", rs_mod(*handlers))
    for h in handlers:
        write(f"{a}/handlers/{h}.rs", rs(f"handler: {h}"))

    # models (db layer)
    api_models = [
        "user", "post", "comment", "circle", "message",
        "notification", "subscription", "report", "media",
        "audit", "incident",
    ]
    write(f"{a}/models/mod.rs", rs_mod(*api_models))
    for m in api_models:
        write(f"{a}/models/{m}.rs", rs(f"db model: {m}"))

    # payments
    write(f"{a}/payments/mod.rs",         rs_mod("revenuecat", "webhooks", "entitlements"))
    write(f"{a}/payments/revenuecat.rs",  rs("RevenueCat REST client"))
    write(f"{a}/payments/webhooks.rs",    rs("Incoming RevenueCat webhook handler (axum route)"))
    write(f"{a}/payments/entitlements.rs",rs("Plan → feature flags. Never trust the client."))

    # search
    write(f"{a}/search/mod.rs",     rs_mod("indexer", "ranking", "suggest"))
    write(f"{a}/search/indexer.rs", rs("Index posts + users into SurrealDB FTS"))
    write(f"{a}/search/ranking.rs", rs("Feed + search ranking signals"))
    write(f"{a}/search/suggest.rs", rs("Type-ahead suggestions"))

    # notifications
    write(f"{a}/notifications/mod.rs",      rs_mod("push", "dispatcher", "templates"))
    write(f"{a}/notifications/push.rs",     rs("APNS + FCM push delivery"))
    write(f"{a}/notifications/dispatcher.rs",rs("Fan-out notification events"))
    write(f"{a}/notifications/templates.rs", rs("Notification copy + deep-link payloads"))

    # realtime
    write(f"{a}/realtime/mod.rs",      rs_mod("ws_server", "hub", "events"))
    write(f"{a}/realtime/ws_server.rs",rs("WebSocket upgrade + connection management"))
    write(f"{a}/realtime/hub.rs",      rs("Broadcast hub — fan-out to connected clients"))
    write(f"{a}/realtime/events.rs",   rs("Event types: FeedEvent, ExpiryTick, TypingIndicator"))

    # moderation
    write(f"{a}/moderation/mod.rs",       rs_mod("pipeline", "rules", "classifier", "audit"))
    write(f"{a}/moderation/pipeline.rs",  rs("Every post + comment runs through here"))
    write(f"{a}/moderation/rules.rs",     rs("Rule engine — thresholds, keyword lists, config"))
    write(f"{a}/moderation/classifier.rs",rs("ML classifier stub — hooks external moderation API"))
    write(f"{a}/moderation/audit.rs",     rs("Audit log — every mod action written here"))

    # tests
    for t in ["auth", "post_expiry", "subscription",
              "moderation", "ghost_reply", "grpc_smoke"]:
        write(f"{sa}/tests/{t}_test.rs", rs(f"integration test: {t}"))

    # ── services/worker ────────────────────────────────────────────────────
    sw = f"{root}/services/worker"
    write(f"{sw}/Cargo.toml", cargo_pkg("worker", bin_name="worker", deps=[
        "tokio.workspace             = true",
        "surrealdb.workspace         = true",
        "anyhow.workspace            = true",
        "tracing.workspace           = true",
        "tracing-subscriber.workspace= true",
        "serde.workspace             = true",
        "chrono.workspace            = true",
        'proto-gen = { path = "../../packages/proto-gen" }',
        'core      = { path = "../../packages/core" }',
    ]))
    w = f"{sw}/src"
    write(f"{w}/main.rs",
        "mod config;\nmod db;\nmod jobs;\n\n"
        "#[tokio::main]\nasync fn main() -> anyhow::Result<()> {\n"
        "    tracing_subscriber::init();\n"
        "    jobs::run_all().await\n"
        "}\n"
    )
    write(f"{w}/config.rs", rs("Worker config from env"))
    write(f"{w}/db.rs",     rs("SurrealDB client for worker process"))
    jobs = [
        "post_reaper",       # deletes/vaults posts at T+TTL
        "feed_ranker",       # refreshes feed ranking signals
        "notification_batcher",
        "subscription_sync", # reconcile RevenueCat entitlements
        "search_indexer",    # keep FTS index fresh
        "media_cleanup",     # delete orphaned media from S3
        "audit_archiver",    # compress + archive old audit rows
        "metrics_rollup",    # aggregate hourly metrics
        "automod_sweep",     # re-run classifier on queued content
    ]
    write(f"{w}/jobs/mod.rs",    rs_mod("runner", *jobs))
    write(f"{w}/jobs/runner.rs", rs("Schedule all jobs with tokio interval loops"))
    for j in jobs:
        write(f"{w}/jobs/{j}.rs", rs(f"job: {j.replace('_', ' ')}"))

    # ── infra ──────────────────────────────────────────────────────────────
    write(f"{root}/infra/docker/api.Dockerfile",          dockerfile("api"))
    write(f"{root}/infra/docker/worker.Dockerfile",       dockerfile("worker"))
    write(f"{root}/infra/docker/ops.Dockerfile",          dockerfile("ops"))
    write(f"{root}/infra/docker/docker-compose.yml",      docker_compose())
    write(f"{root}/infra/docker/docker-compose.prod.yml", "# TODO: prod compose overrides\n")

    for f in ["api-deployment", "worker-deployment", "ops-deployment",
              "surrealdb-statefulset", "ingress", "hpa"]:
        write(f"{root}/infra/k8s/{f}.yaml", f"# TODO: {f}\n")

    for f in ["main", "variables", "outputs", "networking"]:
        write(f"{root}/infra/terraform/{f}.tf", f"# TODO: {f}\n")

    gitkeep(f"{root}/infra/certs")

    # ── docs ───────────────────────────────────────────────────────────────
    write(f"{root}/docs/architecture.md",
        "# Architecture\n\n"
        "Full Rust monorepo.\n"
        "gRPC (tonic + prost) for all internal communication.\n"
        "Blinc (forked) for mobile UI — iOS (Metal) + Android (Vulkan) from one source tree.\n"
        "Blinc desktop for the ops dashboard.\n"
        "SurrealDB 3.0 as the primary datastore (graph + document + FTS).\n"
        "SurrealQL for all queries — no ORM.\n"
        "Worker binary handles all async/scheduled jobs.\n"
    )
    write(f"{root}/docs/api-spec.md",
          "# API Spec\n\nAll service definitions are in `/proto/*.proto`.\n")
    write(f"{root}/docs/db-schema.md",
          "# DB Schema\n\nSee `/services/api/src/db/migrations/`.\n")
    write(f"{root}/docs/subscription-tiers.md",
          "# Subscription Tiers\n\n## Free\n\n## 24+\n")
    write(f"{root}/docs/moderation-playbook.md",
        "# Moderation Playbook\n\n"
        "This is where the weird stuff lives. Document every edge case.\n\n"
        "## Severity Levels\n\n"
        "## Escalation Path\n\n"
        "## Auto-mod Thresholds\n\n"
        "## Ghost Reply Abuse Patterns\n\n"
        "## Shadowban Criteria\n\n"
        "## Known Bad Actor Patterns\n\n"
        "## CSAM Protocol\n\n"
        "## Coordinated Inauthentic Behaviour\n\n"
        "## Appeals Process\n"
    )
    write(f"{root}/docs/grpc-guidelines.md",
        "# gRPC Guidelines\n\n"
        "- All `.proto` definitions live in `/proto/`\n"
        "- Generated code lives in `packages/proto-gen/` — never edit it by hand\n"
        "- Never call the DB directly from a gRPC handler — go through `handlers/`\n"
        "- Streaming RPCs for: messages, notifications, feed updates, ops metrics\n"
        "- Auth interceptor runs on every RPC — JWT required except Register/Login\n"
    )
    write(f"{root}/docs/blinc-fork-rationale.md",
        "# Why We Forked Blinc\n\n"
        "Upstream roadmap (Zyntax DSL, missing widgets) doesn't match 24's current needs.\n"
        "Key patches in `services/blinc/UPSTREAM_DIFF.md`.\n"
    )

    adrs = {
        "001-surreal-over-postgres":   "SurrealDB 3.0 instead of PostgreSQL",
        "002-rust-axum-api":           "Rust + Axum for gRPC / HTTP layer",
        "003-24h-expiry-strategy":     "Post TTL and deletion system",
        "004-blinc-over-rn":           "Blinc (GPU/Rust) over React Native",
        "005-grpc-over-rest":          "gRPC + Protocol Buffers for all comms",
        "006-monorepo-cargo-workspace":"Single Cargo workspace monorepo",
        "007-ops-dashboard-blinc":     "Ops dashboard built in Blinc desktop",
    }
    for slug, title in adrs.items():
        write(f"{root}/docs/ADRs/{slug}.md",
            f"# ADR: {title}\n\n"
            "## Status\n\nProposed\n\n"
            "## Context\n\n\n\n"
            "## Decision\n\n\n\n"
            "## Consequences\n\n\n"
        )

    # ── Done ───────────────────────────────────────────────────────────────
    total = sum(len(files) for _, _, files in os.walk(root)
                if ".git" not in _)
    print(f"✅  Done.  {total} files in tree.\n")
    print("    Next steps:")
    print("      1.  cp .env.example .env  &&  fill in your secrets")
    print("      2.  docker-compose -f infra/docker/docker-compose.yml up -d")
    print("      3.  cargo build --workspace")
    print("      4.  cargo run -p api")
    print("      5.  cargo run -p ops          (ops dashboard, desktop)")
    print()


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(root, "README.md")):
        print("⚠️   No README.md found next to this script.")
        print("    Put scaffold.py in your repo root and try again.")
        sys.exit(1)
    scaffold(root)
