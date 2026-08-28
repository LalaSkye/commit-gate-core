# Canonical bytes and Ed25519 — schema v1

Status: specification. No verifier in this package version.
HMAC remains a separately constructed lab MAC. It is not a signature.

## Instance ceiling

v1 signs with **Ed25519** (RFC 8032 PureEdDSA) only.

- Ed25519ctx and Ed25519ph are out of v1.
- Context is out of v1.
- `SIGNED_FIELDS` has no `issuer_key_id`. v1 assumes one pinned public key.
  Multiple issuers or rotation require a new canonical-schema version before
  any Ed25519 vectors that mention keys.
- Production injects one verifier type. The `ed25519:` prefix is a format
  check, not algorithm authority. An attacker must not select HMAC vs Ed25519
  by writing a prefix.

JOSE: use the fully specified name `Ed25519`, not polymorphic `EdDSA` (RFC 9864).

## Message M

`canonical_bytes(record)` is UTF-8 JSON of `SIGNED_FIELDS` only,
`sort_keys=True`, `separators=(",", ":")`, `ensure_ascii=True`.
The `signature` field is excluded.

That octet string is **M** for Ed25519 and would remain **M** for Ed25519ctx.
`dom2(F,C)` enters the two internal SHA-512 calculations. It does not alter M
or the SHA-256 fingerprint of M.

## Golden vector (schema v1)

Fields:

```
decision_id      dr_001
actor_id         agent_17
action           approve_invoice
object_id        invoice_778
environment      prod
commit_hash      sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
verdict          ALLOW
policy_version   2026-04-27.1
issued_at        2026-04-27T05:00:00Z
expires_at       2026-04-27T05:05:00Z
nonce            nonce_001
```

M:

```
{"action":"approve_invoice","actor_id":"agent_17","commit_hash":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","decision_id":"dr_001","environment":"prod","expires_at":"2026-04-27T05:05:00Z","issued_at":"2026-04-27T05:00:00Z","nonce":"nonce_001","object_id":"invoice_778","policy_version":"2026-04-27.1","verdict":"ALLOW"}
```

- Length: 349 bytes
- SHA-256 of M: `edef12f65098338ea1952425e75d3fa0571712c3fadf4f1c2554981d0284801d`

An Ed25519ctx fixture may reuse that fingerprint of M. It must additionally
freeze instance, context octets, public key, and signature. Those are not
determined by the fingerprint of M. v1 does not include such a fixture.

## Signature grammar (locked, unimplemented)

```
ed25519: + exactly 128 lowercase hexadecimal characters
```

Reject uppercase, whitespace, wrong length, non-hex, missing prefix, extra
suffix. Decode to exactly 64 bytes or refuse.

## Context (out of v1)

RFC 8032 allows Ed25519ctx context length 0–255 octets. Empty context is a
legal ctx instance and is still a different instance from Ed25519.
Cross-instance verification is designed to be infeasible.

RFC 8032: context SHOULD be a protocol constant and SHOULD NOT copy variable
message fields. Prehashed variants are more vulnerable to hash-function
weakness and SHOULD NOT be used. PureEdDSA retains collision resilience.

OpenSSL documents separate `instance` and `context-string` parameters.
That documentation does not, by itself, establish silent ignoring of a
context string.

Many high-level APIs do not expose contexts. Python `cryptography` exposes
only `sign(data)` and `verify(signature, data)` (PureEd25519).
