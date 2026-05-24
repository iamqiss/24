fn main() -> Result<(), Box<dyn std::error::Error>> {
    let protos = &[
        "../../proto/auth.proto",
        "../../proto/users.proto",
        "../../proto/posts.proto",
        "../../proto/comments.proto",
        "../../proto/circles.proto",
        "../../proto/messages.proto",
        "../../proto/notifications.proto",
        "../../proto/search.proto",
        "../../proto/subscriptions.proto",
        "../../proto/media.proto",
        "../../proto/moderation.proto",
        "../../proto/ops.proto",
    ];
    tonic_build::configure()
        .build_server(true)
        .build_client(true)
        .compile_protos(protos, &["../../proto"])?;
    Ok(())
}
