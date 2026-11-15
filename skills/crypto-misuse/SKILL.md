---
name: crypto-misuse
description: >-
  Finds cryptographic misuse that weakens confidentiality, integrity, or
  authentication, including password hashing, randomness, authenticated
  encryption, TLS verification, and secret comparison. Use when reviewing
  crypto, tokens, TLS, signatures, or key handling, or when the user mentions
  encryption, hashing, ciphertext, or CWE-327.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# Cryptography misuse

Review cryptography where it enforces a security decision: passwords, session tokens, signatures, key agreement, and TLS. A hash used as a cache key is not a crypto finding.

Do not design a new cipher. Point the code at a maintained library and a standard construction.

## When to use

Use this skill when the code hashes passwords, issues tokens, encrypts data, verifies signatures, compares secrets, or disables TLS verification. Skip it for general application review with no cryptographic API in the diff, unless you are in a full review and the map shows auth tokens or encryption.

## Method

1. Find the security decision: "this password is correct", "this token is authentic", "this ciphertext is private", "this peer is the server."
2. Check the primitive, the key source, the nonce or IV, and the compare.
3. Check whether the attacker can see ciphertext, tokens, or timing. A weak hash of a password the attacker never receives is a different severity from a weak hash dumped in a response.
4. Prefer the library's high-level API (password hash, AES-GCM, HMAC, TLS defaults) over a block-cipher mode assembled in the handler.

## What to look for

### Passwords and API secrets at rest

Unsafe: MD5, SHA-1, SHA-256, or SHA-512 of a password, with or without a single static salt; reversible encryption of passwords so the app can "decrypt" them; a salt stored in code next to a custom scheme.

Safe: argon2id, bcrypt, or scrypt through a maintained implementation that generates a unique salt and stores it inside the hash string. Verify with the library's verify function.

A fast hash is also wrong for long-lived API tokens if the database stores the token and a database read lets the attacker test offline. Store a hash of the token (HMAC or SHA-256 of a high-entropy token is fine; the token itself must be high entropy). Passwords need a password hash because they have low entropy. Random 256-bit tokens do not.

### Randomness

Unsafe for tokens, reset codes, CSRF secrets, encryption nonces, or key material: `Math.random`, `random.random`, `rand()`, `mt_rand`, `math/rand` without a crypto source, time-based seeds, or a token shorter than 128 bits.

Safe: `crypto/rand`, `secrets.token_urlsafe`, `crypto.randomBytes`, `random_bytes`, or the language wrapper that documents a CSPRNG. UUIDv4 from a CSPRNG is acceptable as an unguessable id. UUIDv1 is not a secret.

`math/rand` for jitter, sampling, or a game is fine. Say so and drop the lead.

### Encryption

Unsafe:

- ECB mode.
- CBC or CTR with a static or reused nonce/IV, or with no MAC. Encrypt-then-MAC or an AEAD is required. CBC without a MAC is a finding when the attacker can modify ciphertext (at rest or in transit).
- AES key hardcoded, derived from a password with one hash, or stored beside the ciphertext in the same database row with no separate key store.
- Nonce reuse for GCM. The nonce must be unique per key. A random 96-bit nonce per message is the usual construction; a counter is fine if it is actually unique under that key.
- Rolling your own stream cipher, "XOR with the key", or MAC-then-encrypt assembled ad hoc.

Safe: AES-GCM or ChaCha20-Poly1305 via the platform API, random nonce per message stored with the ciphertext, key from a KMS or an environment-held data key that is not in the repo.

Encoding (base64, hex) is not encryption. Report code that treats a base64 blob as secret from the user.

### TLS

`InsecureSkipVerify`, `rejectUnauthorized: false`, `verify=False`, `CURLOPT_SSL_VERIFYPEER` disabled, or a custom callback that returns nil are findings when the connection carries credentials or private data. The fix is to verify, and to pin a private CA explicitly if the organization uses one. "It was failing so we disabled it" is the bug, not a reason to downgrade.

Internal service meshes that terminate TLS at a sidecar are needs-validation if the app then talks cleartext only to localhost and you can see that. Disabled verification on a call to a public API is a finding.

### Comparison and HMAC

Secret compare with `==` is a timing lead in languages where the compare returns on the first differing byte and the value is a long-lived secret (HMAC, token, API key). Use `hmac.compare_digest`, `crypto.subtle.timingSafeEqual`, `subtle.ConstantTimeCompare`, or `hash_equals`.

Do not spend a finding on `==` between two short user-typed strings that are then password-hashed anyway. Do report `==` for password hashes only if the comparison is of the raw secret and the hash is not using the library verify function. PHP `==` is also a type-juggling bug, not only a timing bug (`php-security`).

JWT algorithm and key selection: review with `auth-security`. The crypto piece is: pin the algorithm, use a long random HMAC secret or a real asymmetric key, and do not take the key id from the token as a path.

### Deprecated primitives

MD5 or SHA-1 as a file checksum for a cache is Info at most. MD5 or SHA-1 as a signature or integrity check on untrusted data is a finding (collision). SHA-1 certificates are the platform's problem if the code does not implement the verifier itself.

## Verify before you report

1. Name the decision the primitive protects.
2. Quote the API: mode, key source, nonce source, compare.
3. Confirm the data is attacker-influenced or attacker-visible. ECB of a constant internal flag may be Low or a drop. ECB of attacker-influenced personal data is a finding.
4. Match the language. Some standard-library functions look similar and are not (`math/rand` versus `crypto/rand`).
5. Do not attempt to recover plaintext or forge a MAC to prove it.

## Severity

| Misuse | Typical rating |
| --- | --- |
| Password stored with a fast hash or in plaintext | High. Critical if the store is already exposed or the hashes are in a response. |
| TLS verification off for a connection that carries secrets | High |
| Session or reset token from a non-CSPRNG | High if the entropy is low enough to guess; Medium if it is a weak generator but the space is still large. Explain which. |
| Hardcoded encryption key in the repo | High, and rotate the key. Data encrypted only with that key is exposed to everyone with the repo. |
| ECB, static IV, or unauthenticated encryption on attacker-visible data | Medium or High, based on whether the attacker can modify or recognize plaintext |
| Non-constant-time compare on a long-lived HMAC | Low or Medium. Not High unless the token is also low entropy. |
| `math/rand` for non-secret jitter | Drop |

## Examples

```python
# Unsafe: fast hash, no unique salt, reversible by anyone with the database.
stored = hashlib.sha256(password.encode()).hexdigest()

# Safe: the library stores the salt and parameters in the string.
from argon2 import PasswordHasher
ph = PasswordHasher()
stored = ph.hash(password)
ph.verify(stored, password)
```

```go
// Unsafe token.
token := strconv.FormatUint(uint64(rand.Int63()), 16)

// Safe token.
buf := make([]byte, 32)
if _, err := rand.Read(buf); err != nil { // crypto/rand
    return err
}
token := hex.EncodeToString(buf)
```

The Go example is only safe when `rand` is `crypto/rand`. `math/rand` has a `Read` that is not a CSPRNG.

## False positives

- SHA-256 of a content-addressed artifact, a cache key, or an etag.
- bcrypt, argon2, or scrypt used with the library defaults, even if the work factor is not the one you would pick. You may note a very low cost as Low. Do not report "uses bcrypt instead of argon2" as a vulnerability.
- AES-GCM with a random nonce stored alongside the ciphertext.
- TLS verification left at the default.
- Constant-time compare already in use.
- A hardcoded key in a unit test that is not compiled into the service. If production falls back to that test key, report the fallback.

## Related skills

`auth-security` for what the token means once verified. `secrets-exposure` for keys committed beside the ciphertext. Language skills for the exact import path (`crypto/rand` vs `math/rand`, `secrets` vs `random`).
