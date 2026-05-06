# GOVERNANCE MAP

Purpose: one-page map of the governance loop.

This file shows how the control surfaces relate. It does not add a new claim.

---

## Loop

```text
claim
  ↓
invariant
  ↓
adversarial vector
  ↓
verifier
  ↓
receipt
  ↓
change control
  ↓
claim
```

---

## Surface roles

| Surface | Role |
| --- | --- |
| Claim register | Defines what may be said. |
| Invariants | Define what must remain true. |
| Adversarial vectors | Define what must fail. |
| Verifier | Re-checks proof obligations locally. |
| CI workflow | Configures push/PR enforcement. |
| Build receipts | Records evidenced state changes. |
| Change control | Defines when claim or truth-status may change. |
| PR template | Forces contributor-side boundary checks. |
| Governance index | Routes readers through the control surface. |

---

## Standing boundary

Local verification is present and discoverable.

CI enforcement is configured but not yet evidenced green.

No claim is upgraded without evidence.
