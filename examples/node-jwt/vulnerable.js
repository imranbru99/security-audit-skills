// INTENTIONALLY VULNERABLE — teaching fixture for security-audit-skills.
// Do not deploy. Do not mint tokens against a real service.
import jwt from "jsonwebtoken";

const secret = "secret";

export function verifySession(token) {
  return jwt.verify(token, secret);
}
