# CODING_STYLE.md
## Author: Chris Rafuse
## Version: 1.0

# 0. CORE RULE

ALL variables MUST start with:

    CR_

NO EXCEPTIONS

---

# 1. NAMING

GOOD:
CR_event_id
CR_market_type
CR_implied_probability

BAD:
eventId
prob
x

---

# 2. FUNCTION STYLE

Use simple, readable Python:

def compute_implied_probability(CR_price: int) -> dict:
    if CR_price > 0:
        CR_prob = 100 / (CR_price + 100)
    else:
        CR_prob = abs(CR_price) / (abs(CR_price) + 100)

    return {
        "CR_implied_probability": CR_prob
    }

---

# 3. STRUCTURE

- no nested complexity beyond 2–3 levels
- small focused functions
- pure functions preferred
- no hidden state

---

# 4. DATA HANDLING

- always explicit keys
- no mutation of shared state
- return new objects

---

# 5. ERROR HANDLING

Return structured errors:

return {
    "CR_error": True,
    "CR_message": "Invalid price"
}

---

# 6. LOGGING

Always structured:

CR_log = {
    "CR_step": "compute_vig",
    "CR_status": "success"
}

---

# 7. DETERMINISM

- no randomness unless explicitly seeded
- stable ordering required
- same input = same output

---

# 8. FILE ORGANIZATION

core_engine/
tools/
agent/
data/
reporting/
chat/
tests/

---

# 9. COMMENT STYLE

Use short intent-driven comments:

# PURPOSE: compute implied probability from American odds
# INPUT: CR_price (int)
# OUTPUT: dict with CR_implied_probability

---

# 10. AUTHOR STAMP

All major files should include:

## Author: Chris Rafuse

---

# 11. PHILOSOPHY

- clarity > cleverness
- determinism > magic
- tools > prompts
- truth > narrative