use blinc_app::prelude::*;
use blinc_app::windowed::WindowedApp;

mod app;
mod router;
mod state;
mod theme;
mod grpc;
mod screens;
mod components;

fn main() -> anyhow::Result<()> {
    WindowedApp::run(Default::default(), |ctx| app::root(ctx))
}
