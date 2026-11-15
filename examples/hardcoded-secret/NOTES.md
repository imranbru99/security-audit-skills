# Committed credentials

**Two scanner hits, one finding.**

The AWS access key id `AKIAIOSFODNN7EXAMPLE` and secret `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` are Amazon's published documentation pair. Report the pattern match as a known fixture. Do not tell the owner to rotate that documentation key, and do not call AWS with it.

`BILLING_API_TOKEN` is a fictional value committed as if it were production. **Confirmed** secret in source. High, because anyone who can read the repository can read the token. The report should redact the value to `bill_live_…` and say to rotate it if the same pattern appears with a real token. Do not send the token to the billing host to test it.

**Fix.** Read both values from the environment or a secret manager. Fail closed when they are missing. Remove the billing token from history after rotation if it was ever real.

**False positive to avoid.** `changeme`, `your-api-key-here`, unit-test placeholders, and this exact AWS example pair are not incidents. The same assignment with any other key id is a lead.
