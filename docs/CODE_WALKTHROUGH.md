# Code walkthrough

## `RelayMessageCopy`

The selected production model gives each copied Discord message its own row.
`chunk_index` exists because one long source message may become multiple
destination messages. A source index supports efficient lookup by relay surface
and source message ID, while destination message IDs are unique.

## `replace_relay_message_copies(...)`

Relay fan-out returns the message IDs actually created at each destination.
The function builds replacement rows, then deletes the old mapping and inserts
the new rows in one transaction. This supports changed chunk counts after an
update without leaving a stale source mapping behind.

## `get_relay_message_copies(...)`

Results are ordered by destination guild/channel and then chunk index. This is
useful when later logic needs to edit or delete mirrored message chunks in a
deterministic order.

## `edited_destination_content(...)`

Edits use inert `[raid]` labels rather than live role mentions, illustrating a
deliberate product behavior: editing already-relayed content should not trigger
another notification burst.

## Offline demonstration

`FakeTransport` is deliberately simple. It is not production source and does
not model Discord permissions or rate limits. It exists so a reviewer can run
an end-to-end example locally and see the selected persistence code being used
to fan out a synthetic message, modify it, then delete it.
