// INTENTIONALLY VULNERABLE — teaching fixture for security-audit-skills.
// Do not deploy. Do not run against real data.

const express = require("express");
const db = require("./db");

const app = express();

function requireLogin(req, res, next) {
  if (!req.user) return res.status(401).end();
  next();
}

app.get("/api/orders/:id", requireLogin, async (req, res) => {
  const order = await db.order.findById(req.params.id);
  if (!order) return res.status(404).end();
  res.json(order);
});

module.exports = app;
