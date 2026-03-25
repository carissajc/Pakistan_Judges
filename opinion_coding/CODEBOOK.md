# Codebook: four dimensions in judicial opinion text (1–9)

Scale matches the **Vignette Coding Survey** expert ratings of remedies. Code **reasoning and emphasis** in the judgment, not the “correct” legal outcome.

## General rules

- **1** = that strand of reasoning is **absent** or **actively rejected** in the opinion’s reasoning.  
- **5** = **mixed** or **balanced** explicit attention.  
- **9** = that strand **clearly dominates** or is **strongly emphasized** in how the court justifies its decision.  
- Score dimensions **independently** (e.g. high corrective + moderate efficiency is valid).  
- Use **`null`** for a dimension only if the text is **purely procedural** (e.g. credibility, standard of proof) with **no** substantive trace of that dimension—not merely “brief.”

---

## Efficiency (1–9)

**High (7–9):** Reasoning stresses **minimizing waste**, **aggregate costs or benefits**, **proportionality** of remedy or process to social cost, **preserving productive activity**, or **avoiding disproportionate disruption** when weighed against harm.

**Low (1–3):** No attention to costs, waste, or aggregate consequences; or dismisses such concerns.

**Evidence:** Quotes about cost, proportionality, “disproportionate,” economic impact, public interest in continuity of enterprise, etc.

---

## Corrective justice (1–9)

**High (7–9):** Reasoning stresses **making the victim whole**, **wrongdoer–victim** bilateral justice, **restoration** of the status quo, **breach/fault**, **compensation** for wrong, or **disgorgement** framed as undoing wrongful gain.

**Low (1–3):** No corrective framing; only institutional, procedural, or public-order logic.

**Evidence:** Quotes on restoration, compensation, breach, fault, “aggrieved party,” making good loss.

---

## Distributive justice (1–9)

**High (7–9):** Reasoning stresses **fair allocation** across persons or groups by **need**, **equality**, **vulnerability**, **merit**, or **social welfare**—**beyond** simple bilateral correction.

**Low (1–3):** No concern for how burdens/benefits fall across classes of persons or society.

**Evidence:** Quotes on poor/rich, vulnerable groups, equal treatment across litigants or classes, distributive fairness.

---

## Formalist ↔ functionalist (1–9)

**1–3 (formalist):** Emphasis on **statute text**, **formal elements**, **rigid categories**, **precedent labels**, **procedure** without weighing purposes or consequences.

**7–9 (functionalist):** Emphasis on **purposes** of rules, **consequences**, **policy**, **equity**, or **justice of the case**.

**Mid (4–6):** Explicit mix of formal and purposive reasoning.

---

## `insufficient_evidence`

Set `true` and use **`null`** for **all four** scores only when **none** of the dimensions are supported by the text (typical: pure credibility/proof disposition with no policy or justice framing).
