# Solution Blueprint: FlexArb Bots

## 1. User Requirements (Prioritized)
- **Persona:** "Trader Tom" (Tech-savvy, paranoid about security)
- **User Stories:**
    1. As Trader Tom, I want to store my API keys locally in an encrypted vault so they never leave my device. (Size: S, LLM-friendliness: 0.9)
    2. As Tom, I want to start arbitrage with one click, automatically finding opportunities across 3 exchanges. (Size: M, LLM-friendliness: 0.6)
    3. As Tom, I want to see real-time profit/loss updates for the running session. (Size: S, LLM-friendliness: 0.8)
    4. As Tom, I want to configure a maximum loss limit that auto-stops the bot. (Size: S, LLM-friendliness: 0.9)
    5. As Tom, I want to view a log of all executed trades for tax purposes. (Size: M, LLM-friendliness: 0.7)
    6. As Tom, I want the bot to auto-rotate proxies if an IP ban is detected. (Size: M, LLM-friendliness: 0.5)
    7. As Tom, I want to simulate trades (paper trading) before risking real funds. (Size: M, LLM-friendliness: 0.7)
    8. As Tom, I want a "Panic Button" to immediately liquidate all positions and stop. (Size: S, LLM-friendliness: 0.9)

## 2. UX Flow (Text-Only)
### Flow 1: Core Arbitrage Loop
1. User opens App and authenticates via OS Biometrics.
   - *System:* Decrypts local vault (using Keytar/Keychain).
2. User selects strategies (e.g., "Triangular Arbitrage") and clicks "Start".
   - *System Check:* Validates API keys and Balance on Exchange A, B, C.
   - *Error Path:* If insufficient balance, show "Deposit Required" modal.
   - *Error Path:* If keys invalid, prompt "Re-enter Keys".
3. Dashboard updates to "Running" state.
   - *System:* Polls order books via WebSocket.
4. User sees "Profit Ticker" update green/red.

### Flow 2: Error Handling & Resilience
1. *System Event:* Exchange A returns 429 (Rate Limit).
2. Bot enters "Cooldown Mode" for Exchange A.
   - *System:* Switches context to Exchange B & C pairs only.
   - *System:* Rotates Proxy IP.
3. User receives "Network Jitter" notification (optional).

## 3. Non-Functional Requirements (NFRs)
- **Security:** Zero-Knowledge architecture. Keys never sent to our server. Local encryption (AES-256).
- **Performance:** Execution latency < 200ms (Rust backend).
- **Compliance:** No KYC data collection (Client-side only software).
- **Reliability:** Auto-restart on crash (Watchdog).

## 4. Business Case & Unit Economics
**Effort Summary** (Standard Mode):
- Total hours: 180h (after LLM discount 0.6)
- Dev Cost: $21,600 (+30% buffer)

**Unit Economics** (Realistic):
- **ARPU:** $15/month (SaaS License)
- **Churn:** 8%/month (High variance in crypto)
- **LTV:** $159 ($15 / 0.08 * Margin)
- **CAC:** $45 (Niche communities)
- **LTV/CAC:** 3.53x
- **Payback:** 4.2 months
- **ROI:** 4.8x (year 1)

**Sensitivity Sensitivity:**
- **Best Case:** LTV/CAC 5.1x (Viral adoption)
- **Worst Case:** 2.1x (Still viable, market crash)

> **Verdict: Strong Go**

## 5. Risk Register
| Risk ID | Risk Description | Impact | Likelihood | Mitigation |
|---------|------------------|--------|------------|------------|
| R01     | Exchange API bans ips | 5      | 4          | Built-in proxy rotation manager |
| R02     | Regulatory changes    | 4      | 3          | Monitor via news skill; geofence restricted regions |
| R03     | Flash crash liquidation | 5    | 2          | Hard stop-loss triggers |
