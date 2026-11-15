---
name: iac-security
description: >-
  Reviews Terraform, Kubernetes, Docker, and cloud IAM for network exposure
  and excess privilege that configuration makes explicit. Use when reviewing
  infrastructure as code, Dockerfiles, Helm or Kubernetes manifests, or when
  the user mentions Terraform, Kubernetes, IAM, containers, or cloud security.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# Infrastructure as code

Review the configuration the deployer will apply. Report exposure and privilege you can see in the files. Do not guess what a cloud account contains if the resource is not here, and do not request changes against a live account.

## When to use

Use this skill for Terraform, OpenTofu, CloudFormation, Kubernetes manifests, Helm charts, Dockerfiles, and IAM policies checked into the repo. Skip it when there is no infrastructure in scope. A Dockerfile that only builds the app under review is in scope if it is in the tree.

## Method

1. Identify how the app is exposed: load balancer, ingress, security group, bucket, API gateway.
2. Identify who can act: IAM policies, IRSA or workload identity, Kubernetes RBAC, cloud admin users.
3. Compare each permission and each open port to what the workload does in source. Unused admin is a finding. Unused port open to the world is a finding when the subnet path makes it reachable, or Medium when reachability is not in the repo.
4. Look for secrets in the same files (`secrets-exposure`).

## What to look for

### Network

- `0.0.0.0/0` or `::/0` ingress on administration or data ports: SSH (22), RDP (3389), Kubernetes API (6443), databases (5432, 3306, 1433, 6379, 9200, 27017), Docker daemon (2375). Rate High when a route table or a public load balancer in the same tree shows the path is public. Rate Medium when the rule is open and you cannot see the subnet. Do not call it Critical from the CIDR alone.
- Security group or firewall rule that allows all ports (`from_port = 0`, `to_port = 65535`, or protocol `-1` ingress from the world).
- Object storage with `public-read`, a disabled public-access block, or a bucket policy whose principal is `*`, when the objects are not meant to be public. A bucket that is intentionally a static website is not a finding if the contents are public assets. State files and backups in a public bucket are High or Critical.
- Kubernetes `NodePort` or `hostNetwork` for an admin workload, and an ingress with no authentication annotation on an admin service.

Egress `0.0.0.0/0` is normal for many services. Do not report it unless the design is a locked-down subnet and the chart opens egress anyway, or the workload should have no outbound path and a metadata or exfiltration note is in scope.

### IAM and RBAC

- `Action: "*"` and `Resource: "*"`, or the cloud equivalent (`roles/owner`, `AdministratorAccess`) attached to an application workload.
- A policy that allows `iam:PassRole`, `sts:AssumeRole`, or privilege escalation actions the app does not need. Name the action.
- Kubernetes `cluster-admin` bound to a default service account, or a Role that can create pods and secrets in all namespaces when the app is one namespace.
- `automountServiceAccountToken: true` on a pod that does not call the API, combined with a powerful role. The token mount alone is Low.
- Instance profiles and GitHub `id-token` roles whose trust policy allows any repo or any branch (`repo:*`). Tighten the subject to the repository and the protected ref.

Wildcard resource on a single read action the app needs is not the same as full admin. Read the actions.

### Containers

- Privileged pod (`privileged: true`), `hostPID`, `docker.sock` mounted, or `CAP_SYS_ADMIN`, on a workload that receives traffic or runs build jobs. High when an attacker who can run code in the container (see the app review) becomes root on the node. If there is no code-execution path, still report privileged plus exposed socket as High for any multi-tenant or untrusted-build cluster, and Medium for a single-tenant app until an execution path exists.
- Root user with no `USER` in the Dockerfile is Low or Info unless the container is privileged or the image processes untrusted archives. Do not mark every root container Critical.
- `latest` tags for a base image in production manifests. Low. Prefer a digest.
- Missing `readOnlyRootFilesystem`, missing drop of capabilities, and missing seccomp are hardening. Report them as Info only when the user asked for a hardening pass.

### Terraform state and inputs

- State bucket unencrypted or public, or state committed to git. State contains secrets. High.
- `terraform.tfvars` or `*.auto.tfvars` with passwords committed.
- `lifecycle { prevent_destroy = false }` is not a vulnerability.

### Kubernetes admission and policy gaps

A missing network policy is a finding when the cluster hosts more than one trust zone (tenants, or a public namespace beside an admin namespace) and namespaces can talk freely. It is Info on a single-namespace demo. Say which case you are looking at.

## Verify before you report

1. Quote the resource, the port or action, and the principal.
2. Tie it to reachability evidence in the repo (public subnet, internet-facing load balancer, public ingress). If that evidence is missing, say so and cap severity.
3. For IAM, name one action that is broader than the code's API calls. "The policy is not least privilege" without an extra action is not a finding.
4. Do not plan, apply, or call the cloud API. Reading the files is the review.
5. Check that a "public" bucket or wide rule is not a deliberate, documented choice for public assets. If it is deliberate and the data is public, drop it.

## Severity

| Misconfiguration | Typical rating |
| --- | --- |
| Admin port or database open to the world on a public subnet | High |
| Same rule, subnet unknown | Medium |
| Public bucket or container holding state, backups, or private objects | High; Critical if the objects include secrets and the bucket is anonymously listable |
| Workload role with full admin | High |
| Privileged container or host Docker socket on a multi-tenant or CI-build node | High |
| Root container, `latest` tag, missing hardening flags | Low or Info |
| Open egress alone | Drop |

## Examples

```hcl
# Unsafe: SSH from the entire internet.
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}

# Safe: SSH only from the bastion security group, or no SSH and use the cloud's session manager.
ingress {
  from_port       = 22
  to_port         = 22
  protocol        = "tcp"
  security_groups = [aws_security_group.bastion.id]
}
```

Do not "fix" a database by changing `0.0.0.0/0` to a slightly smaller public range. Restrict it to the application security group.

## False positives

- Egress to the internet for an app that calls external APIs.
- A public bucket serving a static site, named and scoped as public content.
- `Action: "*"` on a single resource ARN for a purpose the code documents (for example a CI role that administers one non-production account), when the trust policy is locked to that pipeline. Still mention it if the role can reach production.
- Network policy absent in a single-service development manifest.
- Container runs as root, with no other exposure, during a feature review that did not ask for hardening.
- Security group open between two private groups you can see. That is east-west connectivity, not internet exposure. Report it only if the source group is a public tier and the port is a database.

## Related skills

`secrets-exposure` for values in tfvars, state, and manifests. `supply-chain-security` for image builds and CI roles that assume these policies. `web-security` for an application SSRF that becomes serious because the instance profile or the metadata service is wide open. Mention that combination when both are in the tree.
