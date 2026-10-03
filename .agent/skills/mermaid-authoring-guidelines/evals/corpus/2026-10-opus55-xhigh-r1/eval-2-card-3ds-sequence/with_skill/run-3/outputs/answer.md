**Figure 4.1.** Card payment with a 3-D Secure challenge — steps 1 to 11 of §4.2.1 when Paylane PSP answers `challenge_required`, with the repeats of step 3 on a network error.

```mermaid
%%{init: {"look": "classic", "themeVariables": {"noteBkgColor": "#FFF8E1", "noteTextColor": "#263238", "noteBorderColor": "#C9A227"}, "sequence": {"wrap": true}}}%%
sequenceDiagram
  accTitle: Card payment with a 3-D Secure challenge
  accDescr: Steps 1 to 11 of section 4.2.1 when Paylane PSP answers challenge_required, with the repeats of step 3 on a network error.
  autonumber
  participant ACS as Issuer ACS
  participant CP as Checkout page
  participant OA as Orders API
  participant PS as Payment service
  participant PSP as Paylane PSP
  CP->>OA: order
  OA->>PS: POST /payments<br/>fields of Table 4.3
  loop network error<br/>up to 2 repeats
    PS->>PSP: create payment intent<br/>waits up to 8 s
  end
  PSP-->>PS: challenge_required<br/>with redirect_url
  PS-->>OA: redirect_url
  OA-->>CP: redirect_url
  CP->>ACS: open challenge
  ACS-->>CP: browser to return_url
  PSP->>PS: webhook<br/>payment.succeeded
  PS-->>PSP: HTTP 200
  PS-->>OA: publish<br/>payment.confirmed
  Note over OA: marks the order<br/>as paid
```

- solid arrow = call, the sender waits for the result; dashed arrow = reply, or a message the sender does not wait on;
- number = the step of §4.2.1; note = the rest of step 11;
- `loop` = step 3 repeats on a network error, up to 2 times, with the same idempotency key;
- Issuer ACS and Paylane PSP, at the two ends, are external; the three participants between them belong to the Brightwater store.

Not drawn: when Paylane PSP answers `authorized`, the payment skips steps 4 to 8 and continues at step 9. The fields of `POST /payments` stay in Table 4.3, and the time limits stay in §4.2.3.