# Mapping `vignettes_raw` dimensions `c`–`f` to substantive constructs

## Confirmed from instrument design

The [Vignette Coding Survey.docx](../Vignette%20Coding%20Survey.docx) instructs raters to score each remedy on **four** scales (1 = low, 9 = high on each), in this order:

1. **Efficiency** (least efficient → most efficient)  
2. **Corrective justice** (least correctively just → most correctively just)  
3. **Distributive justice** (least distributively just → most distributively just)  
4. **Formalist ↔ functionalist** (purely formalist → purely functionalist)

## Link to Stata ([analysis1121.do](../analysis1121.do))

The pipeline normalizes `c1`–`c4`, `d1`–`d4`, `e1`–`e4`, `f1`–`f4` from `vignettes_raw`, merges by vignette option index `n`, and forms `c_score`, `d_score`, `e_score`, `f_score` per judge (`prim`).

## Working hypothesis (verify once `vignettes_raw` is available)

| Variable family in `vignettes_raw` | Construct |
|-----------------------------------|-----------|
| `c` (c1–c4 per vignette option) | **Efficiency** |
| `d` | **Corrective justice** |
| `e` | **Distributive justice** |
| `f` | **Formalist–functionalist** (high = functionalist) |

## Required verification step

Open `vignettes_raw` in Stata:

```stata
use vignettes_raw, clear
describe c* d* e* f*
```

Confirm with the research team that the **column labels** or **data dictionary** match the table above. If the spreadsheet that built `vignettes_raw` ordered columns differently, update this file and use the corrected mapping in [merge_with_experiment.py](scripts/merge_with_experiment.py).

## Opinion coding alignment

AI opinion outputs use field names `efficiency_1_9`, `corrective_1_9`, `distributive_1_9`, `formalist_functionalist_1_9` to align with this hypothesis for merge to `c_score`–`f_score` after verification.
