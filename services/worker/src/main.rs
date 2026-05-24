mod config;
mod db;
mod jobs;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::init();
    jobs::run_all().await
}
