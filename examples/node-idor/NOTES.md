# Order lookup

**Confirmed.** High. Any logged-in user who knows or guesses an order id receives that order, including another customer's. `requireLogin` establishes the caller and never uses `req.user` in the query.

**Fix.** Constrain the query by the caller's id, or call a policy that does the same. The 404 is not the control. A UUID primary key would not fix this either.

**False positive to avoid.** Do not report "id in the URL" when the query already includes `userId: req.user.id`. Do not report a 403-versus-404 existence oracle for unguessable ids as a substitute for this finding, and do not accept a status-code change as the fix.

**Related.** If `res.json(order)` includes a payment secret the owner themselves should not see, that is a second finding (excessive data). It is not required to prove the IDOR.
