# Architecture

Full Rust monorepo.
gRPC (tonic + prost) for all internal communication.
Blinc (forked) for mobile UI — iOS (Metal) + Android (Vulkan) from one source tree.
Blinc desktop for the ops dashboard.
SurrealDB 3.0 as the primary datastore (graph + document + FTS).
SurrealQL for all queries — no ORM.
Worker binary handles all async/scheduled jobs.
