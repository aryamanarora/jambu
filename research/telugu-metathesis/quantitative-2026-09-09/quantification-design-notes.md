# Quantification design — working specification, not results

The initial `counts-by-input-class.tsv` is an entry-level diagnostic. Final
tables must instead use the explicitly adjudicated root-family partition and
formation inputs. A dictionary entry can contain short/long roots, singleton/
geminate formations, retained/displaced derivatives and loans simultaneously.

Required final layers:

1. Root family × language: all positive, retained, other, uncertain and borrowed
   evidence flags; never discard R tokens because their cell is labeled A or O.
   Mixed means at least one secure D and one secure R, not merely a vague
   overall label. Count one family per language, irrespective of record count.
2. Formation input × language: independently assigned root quantity, apical
   identity, pre-apical onset, following vowel/cluster and morphology. Assign
   input confidence separately from observed-order confidence. A class may be
   unknown/variable where the family supplies multiple distinct suffixes.
3. Alternative family partitions: certain sharing merged in primary analysis;
   plausible shared roots merged in a conservative sensitivity partition.
4. Historical/source/dialect views: preserve source IDs and exact tags; show
   Old Telugu and historical Kannada separately, then explicitly collapse them
   only in the time-aggregated language view. No double language votes.
5. Mechanism outcomes separate from displacement-family outcomes. Literal
   exchange is not automatically established by a D. Direct medial assimilation
   can erase an apical in a C-initial word just as later Cr simplification can;
   those opaque O forms are not unqualified proof of non-metathesis.

For every class, give eligible families in the reviewed frame; language attested,
not-attested, not-reviewed; D-only, R-only, mixed, O-only, A-only and loan-only,
plus overlapping evidence flags where needed. Fractions must state membership:
secure D-bearing / all attested reviewed families is a descriptive lower-bound
coverage measure; D-bearing / D-or-R-informative families answers a different
question. O and A remain visible, not silently included as unchanged or dropped
from every denominator. Quote alternative upper bounds only with an explicit
list of which unresolved cases could qualify.

Prediction tests:

- Application: broad short-(C)VC singleton-apical domain is a hypothesis about
  eligibility, not an assertion that every member changes. Separate the narrower
  Telugu postconsonantal r/ṟ/ẓ domain from vowel-initial laterals/stops and the
  broader eastern domain. Do not retrospectively exclude a failed case because
  it failed, or infer a long/geminate input from an opaque modern outcome alone.
- Output: test same-V/low-V2 long outcome against high/different-V2 and independently
  consonantal formations. Record the full-form input and immediate post-syncope
  input separately; modern short reflex does not prove when syncope occurred.
- Kui–Kuvi lowering: low V2 must have independent comparative support. Keep
  source-selected *-a claims with no independent evidence in a conditional tier.
  Relative order of lowering and contraction may remain underdetermined.

The reviewed sample is deliberately targeted, with substantial contiguous
vowel-initial review plus scholarship cases and controls. It is not a random
sample or an exhaustive estimate of a language’s metathesis propensity. Publish
the exact frame, reviewed IDs, unresolved source items and remaining inventory.

Certain current family merges: d64+d88; d259+d260; d291+d295; d434+d448;
d686+d689. Check these against annotations before using. Potential sensitivity
merges are recorded in individual exception notes and must be made explicit in
a machine-readable partition file before final counting.
