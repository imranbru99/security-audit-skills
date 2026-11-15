# Security policy

This repository is a set of instructions for defensive code review. It is not a running service.

## Report a problem in the skills

Open an issue if a skill:

- tells an agent to attack a system, use a discovered credential, or write an exploit
- teaches a fix that is still vulnerable
- would systematically produce a false positive or miss a well-known, source-visible bug class
- includes a real secret (the AWS values under `examples/hardcoded-secret/` are Amazon's published documentation examples)

Do not send live credentials, customer data, or a proof-of-concept against a third-party system.

## Reviewing your own product

These skills help an agent read source you are allowed to review. They do not authorize testing a deployed system. If you find a vulnerability in someone else's project, use that project's disclosure policy.
