// Safe counterpart to vulnerable.js.
// The algorithm is pinned. The secret comes from configuration and is long enough to not be a dictionary word.
import jwt from "jsonwebtoken";

const secret = process.env.JWT_SECRET;
if (!secret || secret.length < 32) {
  throw new Error("JWT_SECRET is missing or too short");
}

export function verifySession(token) {
  return jwt.verify(token, secret, {
    algorithms: ["HS256"],
    issuer: "api.example",
    audience: "app.example",
  });
}
