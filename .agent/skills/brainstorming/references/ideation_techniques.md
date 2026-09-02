# Ideation Techniques: Operational Guide

This reference provides step-by-step algorithms for each ideation technique. When SKILL.md says "use SCAMPER" or "use Inversion", follow the concrete steps here.

---

## 1. SCAMPER

SCAMPER is a checklist-based technique. Apply each letter to the problem systematically. Not every letter will yield a useful idea — that's expected. The value is in forcing you to explore angles you'd otherwise skip.

**Steps:**
1. State the current solution or approach in one sentence
2. Apply each letter. For each, generate at least one variant:
   - **S — Substitute**: What component, material, or process could be replaced? ("What if we used WebSockets instead of polling?")
   - **C — Combine**: What could be merged? ("What if auth and billing were one service?")
   - **A — Adapt**: What existing solution from another context fits here? ("How does Netflix handle this?")
   - **M — Modify**: What could be enlarged, shrunk, or changed in shape? ("What if we cached aggressively and accepted eventual consistency?")
   - **P — Put to other use**: Can this component serve another purpose? ("The referral link could also be a personalized onboarding flow")
   - **E — Eliminate**: What could be removed entirely? ("What if we don't need a database table — use event sourcing instead?")
   - **R — Reverse**: What if the order or direction flipped? ("What if the referee invites the referrer?", "What if we process payments before validation?")
3. Collect all variants. Discard obvious non-starters. Present the rest.

**When to use**: COMPLEX tasks where you need systematic coverage of the solution space.

---

## 2. How Might We (HMW)

HMW reframes problems as opportunities. The key is the word "might" — it signals possibility, not commitment.

**Steps:**
1. Identify the core constraint or pain point: "Users churn because onboarding is too long"
2. Reframe as HMW: "How might we onboard users in under 60 seconds?"
3. Generate 3-5 HMW variants by tweaking the frame:
   - Change the subject: "How might we let users onboard *themselves*?"
   - Change the constraint: "How might we make onboarding *feel* fast even if it takes 5 minutes?"
   - Remove the assumption: "How might we skip onboarding entirely?"
   - Flip the emotion: "How might we make onboarding the *best* part of the experience?"
4. For each HMW, brainstorm 1-2 concrete solutions

**When to use**: When the problem feels stuck or the solution space is narrow. HMW is the best technique for breaking out of "there's only one way to do this" thinking.

---

## 3. Inversion (Pre-Mortem variant)

Inversion asks: "What would guarantee failure?" Then designs the opposite.

**Steps:**
1. State the goal: "We want a reliable referral system"
2. Invert: "How would we guarantee the referral system fails?"
   - "Don't validate referral codes"
   - "Process credits synchronously in the checkout critical path"
   - "Allow unlimited referrals per user"
   - "Don't handle duplicate events"
3. For each failure mode, design the countermeasure:
   - "Validate referral codes against DB on use" → becomes a design requirement
   - "Process credits asynchronously" → becomes an architecture decision
4. The countermeasures become your solution architecture

**When to use**: COMPLEX tasks where reliability, security, or fraud prevention matter. Especially powerful for finding edge cases that optimistic thinking misses.

---

## 4. Analogy / Cross-Domain Transfer

Borrow solutions from other fields, companies, or systems. The further the domain, the more novel the insight.

**Steps:**
1. Abstract the problem to its essence: "We need to distribute limited resources fairly among competing requests"
2. Identify domains that solve this abstract problem:
   - Computer science: load balancing, scheduling algorithms
   - Economics: auction theory, market mechanisms
   - Biology: resource allocation in ecosystems
   - Urban planning: traffic flow management
   - Medicine: triage systems
3. For each domain, extract the mechanism:
   - "Hospital triage uses severity-based priority, not first-come-first-served"
   - "Uber uses surge pricing to match supply/demand in real-time"
4. Translate back to your context: "What if we used a priority queue with severity scoring instead of a FIFO queue?"

**Naming sources is mandatory.** Don't say "some systems use X". Say "Stripe's payment retry system uses exponential backoff with jitter — we could apply this pattern to our notification delivery."

**When to use**: When you need genuinely novel approaches. Best for COMPLEX tasks where standard patterns feel insufficient.

---

## 5. First Principles Thinking

Strip the problem to fundamental truths, then build up from scratch — ignoring existing solutions.

**Steps:**
1. State the conventional approach: "Referral systems give credits for inviting friends"
2. Ask "Why?" repeatedly until you hit bedrock truths:
   - "Why credits?" → "To incentivize sharing"
   - "Why sharing?" → "To acquire users cheaply"
   - "Why cheaply?" → "CAC must be below LTV"
   - Bedrock truth: **"We need a user acquisition channel where cost < lifetime value"**
3. From the bedrock truth, generate solutions without referencing existing approaches:
   - "What if instead of credits, we gave referrers a permanent status upgrade?"
   - "What if the product itself was inherently shareable (like Figma collaboration links)?"
   - "What if we made the free tier so good that word-of-mouth replaces paid referrals?"
4. Compare first-principles solutions with conventional ones. Often the best answer is a hybrid.

**When to use**: When the problem statement itself might be wrong. When you suspect the user is solving a symptom rather than the root cause.

---

## 6. Constraint Removal / "What If"

Temporarily remove constraints to discover what the ideal solution looks like, then add constraints back one by one.

**Steps:**
1. List all constraints: budget, timeline, tech stack, team size, backwards compatibility
2. Remove ALL constraints: "If we had infinite time, money, and the best team, what would we build?"
3. Describe the ideal solution in detail
4. Add constraints back one at a time. For each:
   - "Does this constraint change the ideal solution?"
   - "Is this constraint actually real, or assumed?"
   - "Can we partially achieve the ideal within this constraint?"
5. The final solution is the closest achievable approximation to the ideal

**When to use**: When the team feels boxed in by constraints. Often reveals that some "constraints" are actually assumptions that can be challenged.

---

## 7. Wild Card Generation

Force at least one radically different option that challenges the problem framing.

**Steps:**
1. After generating "reasonable" options, deliberately ask:
   - "What would a completely different industry do?"
   - "What would this look like in 10 years?"
   - "What if we did the opposite of what everyone does?"
   - "What would a startup with zero legacy do?"
2. Generate one option that feels uncomfortable or impractical
3. Label it explicitly as "Wild Card"
4. Even if rejected, document what insight it provides

**When to use**: Always for COMPLEX tasks. Wild cards prevent groupthink and often inspire hybrid solutions that wouldn't emerge from conventional thinking.

---

## Technique Selection Guide

| Situation | Primary Technique | Secondary |
|---|---|---|
| "How do we build X?" (clear goal, open implementation) | Direct Alternatives + SCAMPER | Analogy |
| "We're stuck, nothing works" | HMW + Constraint Removal | Inversion |
| "We need this to be bulletproof" | Inversion | First Principles |
| "Is there a better way entirely?" | First Principles | Wild Card + Analogy |
| "What are the options?" (broad exploration) | SCAMPER + Analogy | HMW |
| "Everyone does X, should we?" | First Principles + Wild Card | Constraint Removal |
