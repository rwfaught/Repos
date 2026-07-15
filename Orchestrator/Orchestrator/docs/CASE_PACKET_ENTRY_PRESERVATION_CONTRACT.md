# Case-Packet Entry Preservation Contract

## Purpose

This is a minimal, pure contract for an explicit caller to preserve the
provenance-addressable identity of selected case-packet entries. It applies
only to `source_material` and `extracted_fact` collections. It is not a broad
dossier-entry model, a revision-history system, or production readiness.

## Caller Authority And Case Scope

The caller supplies the active `case_id`, entry kind, operation, entry ID, and
any permitted payload. Identity is case-scoped only: the same ID may appear in
another supplied case without creating a global collision or reconciliation.
The contract maintains no global identity registry and never infers continuity.

An entry ID is a caller-supplied, non-empty normalized string. It is not
derived from content or collection position. Current case-packet-safe case-ID
validation is applied to the supplied case ID.

Identified entries must store that canonical ID exactly. A structured entry
whose stored `entry_id` differs from its normalized form is malformed and is
rejected. The pure contract does not repair, migrate, or normalize malformed
stored entries. Caller-input normalization permits a caller to address a
canonically stored ID; it never authorizes rewriting existing entry identity.

## Supported Entry Types And Operations

Only these entry kinds are supported:

- `source_material`
- `extracted_fact`

Only these operations are supported:

- `create`: append a new identified entry with a non-null payload; collisions
  in the supplied collection are rejected.
- `preserve`: retain an identified entry exactly as supplied. No payload is
  allowed.
- `edit`: replace the payload while retaining the same ID. Continuity is
  caller-declared only.
- `replace`: replace an existing ID with a distinct new ID and new payload at
  the prior entry's deterministic collection location.
- `retire`: remove an identified entry from the active returned collection.

The contract performs no semantic matching: no text or normalized-text
matching, list-position matching, hashes, fuzzy matching, embeddings, or
model judgment participates in identity decisions.

## Legacy Compatibility

Anonymous legacy strings, dictionaries, and other list values may coexist in a
collection. They are copied through unchanged, receive no durable ID, and
cannot be selected by a preservation operation. There is no adoption operation
in this boundary; producer adoption and legacy migration remain future work.

## Purity, Validation, And Readback

The implementation validates and applies one operation to an in-memory list,
then returns a deterministic updated list and readback. It does not load or
save cases, mutate an input collection, invoke commands, or use persistence.
It rejects malformed structured entries, duplicate current IDs, absent targets,
collisions, missing required payloads, disallowed payloads, and non-distinct
replacement IDs with deterministic operator-legible errors.

Readback includes the case ID, entry kind, operation, transition, prior ID,
resulting ID, caller-declared continuity flag, and these non-proofs:

- caller-declared continuity is not semantic-equivalence proof;
- entry identity does not establish truth;
- source-material identity does not establish source quality;
- fact identity does not establish fact correctness;
- replacement does not establish that the new entry is better; and
- no persistence or evidence-link adoption occurred.

## Boundaries And Future Questions

There is no evidence-link adoption, persistence migration, producer
integration, revision history, global identity, or runtime/provider/model
behavior in this contract. It does not create a broad dossier-entry model.

Future bounded adoption questions include who may assign IDs, how a producer
may explicitly emit them, whether an existing case needs an opt-in adoption
operation, and what separately authorized persistence or evidence-link work
would be necessary. Those questions are not answered or implemented here.
