use blinc_app::prelude::*;
use blinc_app::windowed::{{WindowedApp, WindowConfig}};

mod app;
mod router;
mod state;
mod grpc;
mod theme;
mod screens;
mod components;

fn main() -> anyhow::Result<()> {
    WindowedApp::run(
        WindowConfig {
            title: "24 — Ops Dashboard".into(),
            width:  1440.0,
            height:  900.0,
            ..Default::default()
        },
        |ctx| app::root(ctx),
    )
}
