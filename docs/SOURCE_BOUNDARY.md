# Source provenance and public-release boundary

This repository deliberately distinguishes **selected production source** from
**new public demonstration scaffolding**.

## Copied from the production project

`src/graids_db/relay_message_copies.py` is copied verbatim from the supplied
current GRAIDS project. It defines the `RelayMessageCopy` SQLAlchemy model and
the asynchronous functions used to query, replace, and delete source-to-copy
mappings.

The two operations in `src/graids_demo/formatting.py` are adapted from reusable
formatting functions in the production message bridge. Function names were made
public-facing and the chunking docstring was clarified; the core behavior is
otherwise retained.

Legitimate engineering comments are intentionally preserved where they explain
an invariant or design decision. Comments are not stripped simply to make the
source look different from the development version.

## Newly written for this public repository

- `src/graids_db/engine.py`: temporary in-memory SQLAlchemy/SQLite setup.
- `src/graids_db/models.py`: minimal SQLAlchemy base class only.
- `src/graids_demo/offline_relay.py`: synthetic local demonstration showing
  how persisted mapping rows can support fan-out, edit synchronization and deletion.
- tests and documentation.

The demo is intentionally **not a reconstructed production Discord bot**. It
omits networking, webhook delivery, moderation, account linking, configuration,
approvals, retries, rate-limit behavior, and deployment details.

## Deliberately excluded

- `.env` files, tokens, webhook URLs, credentials, host configuration;
- production SQLite databases, WAL/SHM files, logs and activity histories;
- Discord user/server/channel/message IDs from production;
- old nested Git history and deployment archives;
- moderation, account-linking and approval internals pending separate review;
- raw production screenshots/messages.

This boundary provides inspectable evidence of database and relay-state design
without treating a public portfolio as a reason to expose users or production
infrastructure.
