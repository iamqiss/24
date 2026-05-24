mod config;
mod db;
mod auth;
mod grpc;
mod handlers;
mod models;
mod payments;
mod search;
mod notifications;
mod realtime;
mod moderation;
mod errors;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::init();
    let cfg = config::Config::from_env()?;
    let db  = db::connect(&cfg).await?;
    grpc::serve(cfg, db).await
}
