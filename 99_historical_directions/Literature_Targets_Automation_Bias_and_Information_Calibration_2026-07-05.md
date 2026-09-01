# Literature Targets: Automation Bias, Reduced Search, and Information Calibration

## Purpose

This is a **working memo** for Paper 1. It is meant to support later work on:

- literature review
- gap construction
- criticism / positioning
- PPT pages on `existing work -> traditional view -> gap`

It is **not** a formal bibliography record and does **not** replace the separate shared-library / bib workflow.

## Core Positioning

These papers are useful because together they form a clear critical target:

> A large share of the automation bias / decision aid / verifiability / technology dominance literature can slide into an implicit narrative:
> `AI / decision aid -> less search / less independent checking -> worse decisions`

Paper 1's stronger move is:

> The problem is not merely whether users search less. The deeper issue is whether AI changes the information structure that users can see, compare, and challenge. In particular, the key question is whether AI summaries omit counterevidence, minority information, or highly diagnostic peripheral cues, thereby changing users' judgments about evidentiary sufficiency.

## Target Table

| No. | Target Paper | Domain / Context | Core Target Claim | Problem in That Claim | Your Critical Angle |
| --- | --- | --- | --- | --- | --- |
| 1 | **Sutton, Arnold, & Holt. “An extension of the theory of technology dominance.”** | Management, auditing, professional judgment, AI-assisted decisions | TTD / TTD2 argue that intelligent systems reshape reliance structures in professional judgment and may lead to short-run judgment bias, long-run deskilling, and erosion of professional knowledge. The paper explicitly extends TTD2 to accounting, auditing, finance, medicine, and law. | Its risk narrative can slide toward: once humans are dominated by technology, they search less and think less independently, so decision quality deteriorates. | Critique it as still too macro-level: technology dominance is not just about reduced search; AI rewrites the information structure users can see, compare, and question. |
| 2 | **Seow, P.-S. (2011). “The effects of decision aid structural restrictiveness on decision-making outcomes.”** | Auditing, internal control, computerized decision aids | Highly restrictive decision aids force users to follow system-defined procedures; experimentally, greater restrictiveness makes users less able to identify issues not prompted by the system. | This is very close to your argument, but it still attributes the problem mainly to decision aid restrictiveness rather than to the representativeness of AI summaries. | Use it as a bridge paper: bad decisions are not simply caused by less search, but by the structural exclusion of “unprompted information” from the user's field of view. |
| 3 | **Lyell & Coiera (2017). “Automation bias and verification complexity: a systematic review.”** | Medicine, human factors, clinical decision support | Automation bias is defined as over-reliance on decision support systems, thereby reducing vigilance in information seeking and information processing. | The review treats verification complexity as a key mechanism, but this can easily reduce the issue to the intensity of user verification behavior. | Your response: verification complexity by itself does not determine decision quality; what matters is whether the verification path contains diagnostic evidence, counterevidence, and representative information. |
| 4 | **Hondrich & Ruschemeier (2023). “Addressing Automation Bias Through Verifiability.”** | Algorithmic governance, human-in-the-loop, legal compliance | The paper treats verification behavior as the key variable for mitigating automation bias and proposes verifiability as a minimum condition for meaningful human involvement. | It institutionalizes “verifiability,” but can still implicitly assume that if humans can verify, want to verify, and verify enough, supervision quality will improve. | Critique: the core of meaningful human oversight is not formal verifiability alone, but whether AI outputs preserve enough representative, conflicting, and rebuttable information for human judgment. |
| 5 | **Kupfer et al. (2023). “Check the box! How to deal with automation bias in AI-based personnel selection.”** | AI personnel screening, résumé summaries, AI dashboards | Verification intensity indicators are positively related to objective decision quality; lower clicks, page visits, and dwell time imply greater automation bias and worse decisions. | This is the clearest “less search = worse decisions” target. The experiment increases verification intensity by lowering aggregation and warning about system errors, but it does not adequately control the representativeness of AI summaries. | This is your sharpest critique target: increasing search is only a remedial move; the real causal mechanism is whether AI summaries omit key counterexamples, minority information, or peripheral yet highly diagnostic cues. |

## Best Later Uses

### 1. Reverse positioning in the Paper 1 literature review

These papers are most useful when organized into the following logic:

1. Existing literature already recognizes automation bias, structural restrictiveness, verification complexity, and technology dominance.
2. This literature correctly sees that AI / decision aids can reduce independent checking, lower information search, and reshape reliance.
3. But much of it still frames the problem mainly in terms of:
   - reduced search intensity
   - insufficient verification intensity
   - insufficient user vigilance
4. Paper 1 pushes the argument one level further:
   - the real object of identification is not whether people search less, but whether AI summaries change users' judgments about the value of additional evidence, evidentiary sufficiency, and the hidden signal structure behind the summary.

### 2. PPT use: `existing work / traditional view / gap`

This set is especially useful for a PPT sequence like:

- `existing work`
  Existing automation bias and decision aid literature often frames the risk as users checking less, clicking less, and searching less.

- `traditional view`
  The traditional fix is often implicit: if we can increase verification intensity or search intensity, judgment quality should improve.

- `gap`
  But this still leaves a deeper question unresolved: were users actually given sufficiently representative, conflicting, and rebuttable information in the first place?

- `our move`
  Paper 1 therefore does not stop at `less search`; it moves to whether AI changes judgments about evidentiary sufficiency and the value of additional evidence.

### 3. Best single direct target

If later you want to highlight only one especially clear target, the priority order is:

1. **Kupfer et al. (2023)**  
   Because it comes closest to the claim `less search = worse decisions`.

2. **Seow (2011)**  
   Because it works well as a bridge from “restrictive design” to “representativeness and omission structure.”

3. **Lyell & Coiera (2017)**  
   Because it supports your critique that `verification complexity / vigilance` is still not specific enough.

## Reminder to Self

- Do not criticize these papers as simply “wrong.”
- The stronger and more accurate move is: they correctly identify verification, reliance, and reduced search as important, but they do not yet push the argument to the level of information structure, representativeness, conflict, and diagnosticity in AI summaries.
- Paper 1 is strongest when it does **not** reject automation bias research, but instead shows that much of it remains at the level of behavioral intensity, while your paper moves the argument to the level of information calibration.
