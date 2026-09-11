# Investigation protocol and working ledger

Started 2026-09-09 05:12 UTC; eight-hour working window ends 13:12 UTC.
This is an expanded investigation of existing Jambu evidence. The parent directory's
2026-09-08 work is prior analysis to verify, not an authority or a completed denominator.
The final report will be written after annotation and analysis. No report exists in this
subdirectory at the start of the investigation.

## Scope and units

Inventory all language IDs assigned to a Dravidian clade in current CLDF, including
reconstructed languages and unlinked records. Include all DEDR entries and all accepted
ancestry paths involving those records. Preserve source text, alternate hypotheses,
cross-dictionary comparisons, dialect tags, and original strings. Do not treat a
dictionary's graph edge as proof of cognacy, its first reflex as a proto-form, or its
related derivatives as independent sound changes.

The main inferential unit is an etymological root family. Formation-level observations
are subordinate units needed to test morphological and phonological conditioning.
Record duplicate evidence sources together and retain individual stable form IDs.
Separate dialect variants, attested historical variants, and distinct formations.
When root-family membership is disputed, count the conservative accepted partition
and expose sensitivity to alternative partitions, rather than choosing whichever
partition strengthens the rule.

## Independently motivated input classification

Record separately: reconstruction level and authority; C1 identity/absence; V1 quality
and quantity; C2 identity and singleton/geminate/cluster status; V2 quality and its
independent support; root shape; formative shape; grammatical category; evidence for
the root/formative boundary; and reconstructed ordering. Unknown values stay unknown.
Initial screening may use attested comparisons, but these are candidate flags, never
automatically accepted reconstructions or outcome labels.

Predeclared core hypothesis from historical scholarship: short-vowel (C)VC roots with
a singleton apical C2 followed by a formative provide the principal environment for
South-Central displacement. Compare liquids, apical stops, and nasals separately;
compare non-apicals, long V1, geminate C2, root clusters, free roots, and compounds as
controls. Test low versus non-low formative vowels and consonantal formatives for
quantity, keeping unsupported formative reconstructions outside decisive tests.

Outcomes: displacement supported; order retained; mixed/formation-dependent;
other development; ambiguous mechanism; questionable cognacy/borrowing;
missing attestation; not reviewed. Absence of an r in modern Telugu is not itself
retention. Test concealment through cluster simplification, liquid merger,
assimilation, and initial-segment loss.

## Evidential and quantitative requirements

Each reviewed family receives a comparative direction argument, relevant source
locators, proposed intermediate stages with their status (attested/reconstructed/
optional), predicted and observed outcomes, and exception analysis. Reconstruct
segment order from cognate distributions and known correspondences across branches,
not by privileging a modern language. Evaluate metathesis against syncope, aphaeresis,
epenthesis, assimilation, analogical reshaping, borrowing, and uncertain cognacy.

Report eligible families, attested families, decisive families, positives, retentions,
mixed outcomes, ambiguities, exclusions, and missingness separately. Positive/decisive
and positive/attested describe different quantities and must not share a label.
No raw-record count is an independent-etymon denominator. Provide membership lists
for every statistic, with all quantities generated from reviewed annotation files.
Do not infer a language's absence of a sound change from absence in a dictionary.

Test shared innovations, independent development, and contact against more than raw
overlap: compare diagnostic derivative identity, recurrent phonological details,
relative chronology, evidence from early texts, geography, and source dependence.
Do not infer borrowing solely to remove exceptions or infer unattested suffixes solely
to produce the desired output.

## Work plan and coverage ledger

1. Freeze/hash inputs; extract all Dravidian evidence and search candidates.
2. Read scholarship and independently annotate reconstructed inputs and relevant controls.
3. Review comparative families individually; expand targeted unlinked-data searches.
4. Audit exceptions, duplication, missingness, and alternative historical derivations.
5. Generate counts and membership lists; check sensitivity and reproducibility.
6. Only then write the narrative report and complete annotated appendices.

Working notes and structured annotation are updated throughout. If the time window
precludes exhaustive coverage, the final coverage ledger will identify reviewed IDs,
screened-only IDs, remaining IDs, and excluded scopes exactly.

## Initial observations

- Prior inventory: 2,701 Telugu-bearing DEDR groups; 116 groups with initial-cluster
  forms were manually triaged. This is not a metathesis rate or full candidate audit.
- Existing local books and page images are available in `../../../../tmp/telugu-metathesis`.
  Files with .pdf extensions may be HTML access responses; validate before use.
- Keep all prior artifacts and unrelated working-tree changes intact.
- Commands running the research scripts are submitted through a dedicated local tmux
  socket `/private/tmp/jambu-telugu-metathesis-20260909.sock`, session `telugu-metathesis`.
