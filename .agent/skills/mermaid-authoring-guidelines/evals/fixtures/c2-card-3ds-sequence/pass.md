**Figure 1.** Card payment with a 3-D Secure challenge — the eleven steps of one payment in order,
with the retry of the payment intent and the authorized answer that skips the challenge.

```mermaid
%%{init: {"look": "classic", "themeVariables": {"noteBkgColor": "#FFF8E1", "noteTextColor": "#263238", "noteBorderColor": "#C9A227"}, "sequence": {"wrap": true}}}%%
sequenceDiagram
  accTitle: Card payment with a 3-D Secure challenge
  accDescr: The Checkout page places the order and the Orders API calls the Payment service, which asks Paylane PSP for a payment intent. On a challenge_required answer the browser goes to the Issuer ACS and back. The webhook confirms the payment, and the Orders API marks the order as paid.
  autonumber
  participant ACS as Issuer ACS
  participant CHK as Checkout page
  participant ORD as Orders API
  participant PAY as Payment service
  participant PSP as Paylane PSP
  CHK->>ORD: place order
  ORD->>PAY: POST /payments
  loop up to 2 retries
    PAY->>PSP: create payment intent
  end
  PSP-->>PAY: answer
  alt authorized
    Note over ORD,PAY: no challenge
  else challenge_required
    PAY-->>ORD: redirect_url
    ORD-->>CHK: redirect_url
    CHK->>ACS: open challenge
    ACS-->>CHK: back to return_url
  end
  PSP->>PAY: payment.succeeded
  PAY-->>PSP: HTTP 200
  PAY-->>ORD: payment.confirmed
  Note over ORD: order marked as paid
```

Legend:
- solid arrow = a call; the sender waits for the answer
- dashed arrow = an answer, or a message the sender does not wait on
- number = the step of the list in §4.2.1
- `loop` and `alt` frames = the repeat and the choice that the text states
- note box = a fact of the text, on the participant it concerns
