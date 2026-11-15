# SSH security group

**Confirmed misconfiguration.** SSH accepts connections from every IPv4 address. Severity is High when the subnet route table or an internet gateway in the same tree shows the instance is reachable, and Medium when those resources are not in the review. Do not rate Critical from the CIDR alone.

**Fix.** Remove world-route SSH. Allow the bastion security group, or drop SSH and use the cloud's session manager. Replacing `0.0.0.0/0` with a large public range is the same bug.

**False positive to avoid.** Do not report egress `0.0.0.0/0` on this security group as the same finding. Outbound internet is often required and is not in this fixture. Do not report the bastion pattern in `secure.tf` as open SSH.
