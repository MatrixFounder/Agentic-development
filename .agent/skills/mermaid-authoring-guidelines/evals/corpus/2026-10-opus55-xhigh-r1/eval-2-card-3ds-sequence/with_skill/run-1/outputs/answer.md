**Figure 4.1.** Card payment with a 3-D Secure challenge: steps 1 to 11 of §4.2.1 as numbered messages, with the repeat of step 3 as a loop and the challenge as an option.

```mermaid
%%{init: {"look": "classic", "themeVariables": {"noteBkgColor": "#FFF8E1", "noteTextColor": "#263238", "noteBorderColor": "#C9A227"}, "sequence": {"wrap": true}}}%%
sequenceDiagram
  accTitle: Card payment with a 3-D Secure challenge
  accDescr: Steps 1 to 11 of section 4.2.1 as numbered messages, with the repeat of step 3 as a loop and the challenge as an option.
  autonumber
  participant ACS as Issuer ACS
  participant CP as Checkout page
  participant OA as Orders API
  participant PS as Payment service
  participant PSP as Paylane PSP
  CP->>OA: send order
  OA->>PS: POST /payments
  loop on network error<br/>up to 2 repeats
    PS->>PSP: create payment intent<br/>waits up to 8 s
  end
  opt challenge_required
    PSP-->>PS: challenge_required<br/>redirect_url
    PS-->>OA: redirect_url
    OA-->>CP: redirect_url
    CP->>ACS: open challenge
    ACS-->>CP: back to return_url
  end
  PSP->>PS: webhook<br/>payment.succeeded
  PS-->>PSP: HTTP 200
  PS-->>OA: publish<br/>payment.confirmed
  Note over OA: marks the order<br/>as paid
```

- Solid arrow = call, where the sender waits for the result. Dashed arrow = reply or unwaited message. Numbers = the steps of §4.2.1.
- `loop` = step 3 repeats on a network error, up to 2 times, with the same idempotency key.
- `opt` = steps 4 to 8 run only when Paylane PSP answers `challenge_required`. On `authorized`, the payment continues at step 9.
- Note = what the Orders API does when it consumes `payment.confirmed`.

The figure leaves out the request fields of Table 4.3 and the time limits of §4.2.3.