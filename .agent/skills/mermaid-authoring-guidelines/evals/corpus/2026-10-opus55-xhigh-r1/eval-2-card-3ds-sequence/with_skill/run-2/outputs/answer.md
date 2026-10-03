**Figure 4.2.** Card payment with a 3-D Secure challenge — the eleven steps of §4.2.1 between the five parties, numbered as in the list, with the challenge steps 4 to 8 shaded.

```mermaid
%%{init: {"look": "classic", "themeVariables": {"noteBkgColor": "#FFF8E1", "noteTextColor": "#263238", "noteBorderColor": "#C9A227"}, "sequence": {"wrap": true}}}%%
sequenceDiagram
  accTitle: Card payment with a 3-D Secure challenge
  accDescr: The eleven steps of §4.2.1 between the five parties, numbered as in the list, with the challenge steps 4 to 8 shaded.
  autonumber
  participant ACS as Issuer ACS
  participant CP as Checkout page
  participant OA as Orders API
  participant PS as Payment service
  participant PSP as Paylane PSP
  CP->>OA: order
  OA->>PS: POST /payments
  PS->>PSP: create payment intent<br/>waits up to 8 s
  rect rgba(127,127,127,0.10)
    Note over ACS,PSP: 3-D Secure challenge<br/>skipped when Paylane PSP answers authorized
    PSP-->>PS: challenge_required<br/>redirect_url
    PS-->>OA: redirect_url
    OA-->>CP: redirect_url
    CP->>ACS: open challenge
    ACS-->>CP: browser to return_url
  end
  PSP->>PS: webhook<br/>payment.succeeded
  PS-->>PSP: HTTP 200
  PS-->>OA: publish<br/>payment.confirmed
  Note over OA: marks the order<br/>as paid
```

Legend:
- solid arrow = call; dashed arrow = reply or unwaited message; numbers = the steps of §4.2.1;
- grey band = the 3-D Secure challenge, named by its first note; the other note states the outcome of step 11.

Not drawn: the repeats of step 3 after a network error, the nine fields of step 2 (Table 4.3), the time limits of §4.2.3 and the boundary of the Brightwater store.