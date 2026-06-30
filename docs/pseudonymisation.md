# Identity and pseudonymisation design

The demonstrator does not use a name, NHS number, date of birth, postcode or any other direct identifier.

## Interface identifier

Each row uses an opaque, wholly synthetic `PIE_PERSON_KEY`, for example `PIE-LEE-7A4F9C21`. It has no connection to an NHS number or any real person.

## Future authorised deployment pattern

1. An approved tenant-side identity service receives an NHS number under the agreed lawful basis.
2. It creates a stable pseudonymous key using a tenant-held secret, for example `HMAC-SHA-256(NHS number, tenant secret)`.
3. PIE receives the pseudonymous key and the minimum necessary linked attributes.
4. The re-identification mapping remains in the authorised tenant environment. It is not stored in the presentation layer and is available only to roles permitted to identify the person for care.

This is an architecture pattern, not a claim that an integration or re-identification route is already in place.
