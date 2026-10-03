### 4.2 Card payment with a 3-D Secure challenge

This section describes how the Brightwater store takes a card payment when the card issuer asks
for a challenge. Five parties take part. The Checkout page, the Orders API and the Payment service
belong to the Brightwater store. Paylane PSP, the payment provider, and the Issuer ACS, the
challenge page of the card issuer, are external.

#### 4.2.1 Steps

1. The Checkout page sends the order to the Orders API.
2. The Orders API calls the Payment service with `POST /payments`. The request carries the nine
   fields of Table 4.3.
3. The Payment service asks Paylane PSP to create a payment intent and waits up to 8 s.
4. Paylane PSP answers `challenge_required` with a `redirect_url`.
5. The Payment service returns the `redirect_url` to the Orders API.
6. The Orders API returns the `redirect_url` to the Checkout page.
7. The Checkout page opens the challenge at the Issuer ACS.
8. The Issuer ACS sends the browser back to the `return_url` of the Checkout page.
9. Paylane PSP sends the webhook `payment.succeeded` to the Payment service.
10. The Payment service answers the webhook with HTTP 200.
11. The Payment service publishes `payment.confirmed`. The Orders API consumes it and marks the
    order as paid.

When step 3 fails with a network error, the Payment service repeats it up to 2 times with the same
idempotency key. When Paylane PSP answers `authorized` instead of `challenge_required`, the
payment skips steps 4 to 8 and continues at step 9.

#### 4.2.2 Table 4.3 — fields of `POST /payments`

| Field | Content |
| :--- | :--- |
| `order_id` | the order to pay |
| `amount_minor` | the amount in minor currency units |
| `currency` | the currency code |
| `card_token` | the card, as a token from the payment form |
| `billing_country` | the country of the billing address |
| `device_fingerprint` | browser data for the risk check of the issuer |
| `return_url` | the Checkout page address that the Issuer ACS returns to |
| `idempotency_key` | one value for a request and all its repeats |
| `customer_ip` | the IP address of the browser |

#### 4.2.3 Time limits

- The Payment service fails a payment that receives no webhook within 15 min.
- Paylane PSP repeats an unanswered webhook every 5 min for up to 24 h.
- The Orders API keeps the stock of an unpaid order reserved for 20 min.
