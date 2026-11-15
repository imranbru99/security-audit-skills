// Safe counterpart to vulnerable.js. The order must belong to the caller.

const express = require("express");
const db = require("./db");

const app = express();

function requireLogin(req, res, next) {
  if (!req.user) return res.status(401).end();
  next();
}

app.get("/api/orders/:id", requireLogin, async (req, res) => {
  const order = await db.order.findOne({
    _id: req.params.id,
    userId: req.user.id,
  });
  if (!order) return res.status(404).end();
  res.json(order);
});

module.exports = app;
