# Rubric — mobile-token-storage

Score the agent's output. Mark each PASS / FAIL.

## Security (weight: high)
- [ ] Tokens are stored via `EncryptedSharedPreferences` backed by the **Android Keystore** (`AndroidKeyStore`).
- [ ] The master key is generated/held in the Keystore, not hardcoded or derived from user input.
- [ ] No token is written to plain `SharedPreferences`, files, or logs.
- [ ] `clear()` properly removes both tokens (and does not leave residue).

## Correctness (weight: medium)
- [ ] Uses the security-crypto library idiomatically (correct `EncryptedSharedPreferences.create(...)` args / `MasterKey`).
- [ ] API surface is minimal and correct: `get`, `save`, `clear` work as described.
- [ ] Handles the Keystore-unavailable / key-invalidated edge case gracefully (or notes it).

## Contract (weight: medium)
- [ ] Consistent with the token lifecycle in `docs/diagrams/mobile-auth-sequence.md`.
- [ ] No plaintext token returned in a way that defeats the purpose of secure storage.

## Clarity (weight: low)
- [ ] The note correctly states that keys are protected by the hardware-backed Keystore.

**Overall:** PASS requires all high-weight items to PASS.
