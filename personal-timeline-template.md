# Personal Symptom Timeline — Template

> **What this is.** A template for the personal medical timeline you should feed to the AI alongside the `sibo-research-db` database. When the AI can read *both* your full history *and* 7 million patient reports, the answers stop being generic and start being specific to you.
>
> **How to use it.** Copy this template into a new file (e.g. `my-research.md`), fill in your own details, then point your AI tool's MCP config at it via the `SIBO_REPORT` env var. The AI gets a `get_report` tool that reads your file. Without the env var, your file stays completely private.
>
> **Where it came from.** This is a *randomized, fictional version* of the actual document the author of this database uses for their own SIBO research. Names, dates, lab values, locations, and event details have all been changed. The **structure** is what matters — copy the headings and the level of detail, then fill in your real information.

---

## Patient Information

| Field | Value |
|---|---|
| **Name** | Sample Patient *(replace with your name, or just initials)* |
| **Date of Birth** | April 12, 1993 |
| **Age / Sex** | 32-year-old Male |
| **Allergies** | Penicillin (mild rash, childhood) |
| **Symptom onset** | June 2020 |
| **Duration** | ~5 years (as of December 2025) |
| **Document last updated** | December 2025 |

## Chief Complaints

*List your primary, persistent symptoms. Order by severity or impact. Be specific — generic "fatigue" is much less useful to an AI than "predictable mid-afternoon energy crash, ~2-3 PM, lasting ~90 minutes."*

- Chronic abdominal bloating, worse in the evening
- Alternating constipation and loose stools, never normal
- Brain fog, especially after meals
- Severe gas pressure pain (frequently wakes me at night)
- Mid-afternoon fatigue (predictable, ~2-3 PM, lasts 90 min)
- Anxiety and racing heart during flares
- Expanding list of food sensitivities (started with FODMAPs, now reactive to most fermentable carbs)

## History of Present Illness

*Tell the story of how you got here, in chronological order. Specific dates and events are more useful than general timeframes. Note any inflection points where symptoms changed materially.*

### Initial Triggering Event (June 2020 — Southeast Asia)

While traveling in Thailand, consumed street food that triggered severe gastroenteritis within 12 hours. Symptoms: violent vomiting, watery diarrhea, fever to 102°F, significant dehydration. Hospitalized for 4 days, IV fluids only. Cultures inconclusive (likely toxin-mediated rather than identifiable pathogen). Discharged without antibiotics.

**Post-discharge sequelae:**
- Persistent diarrhea for ~8 weeks
- Then alternating constipation / loose stools
- Bloating, gas, daily abdominal pain by month 3
- Brain fog and fatigue developed concurrently

### Subsequent Significant Events

**October 2020 — First medical workup.** Primary care, CBC/CMP/stool culture all unremarkable. Diagnosed "post-infectious IBS," recommended FODMAP diet. ~20% symptom reduction on strict low-FODMAP, not full remission.

**February 2021 — First SIBO breath test.** Lactulose hydrogen breath test positive (peak H2 38 ppm at 90 min). Hydrogen-dominant SIBO.

**March 2021 — First rifaximin round (550mg TID × 14 days).** Day 6: significant improvement in bloating and stool form. Day 14 (end of course): symptoms back to baseline.

**August 2021 — Second rifaximin round (same dose).** No noticeable response.

**January 2022 — Functional medicine consult.** Comprehensive panel: GI MAP, organic acids, hormones. Findings: elevated H. pylori antigen, low secretory IgA, dysbiotic flora, depleted Akkermansia.

**April 2022 — 8-week herbal antimicrobial protocol** (oregano oil, berberine, neem). Tolerated well. ~30% symptom reduction during, regressed within 4 weeks of stopping.

**July 2023 — Severe flare.** After a viral GI bug, baseline symptoms worsened markedly. Daily bloating became near-constant. Brain fog severe enough to affect work.

**January 2024 — Methane breath test positive.** Repeat lactulose test showed both H2 and CH4 elevated (CH4 peak 22 ppm). Diagnosed with IMO (intestinal methanogen overgrowth) on top of existing SIBO.

**June 2024 — Allicin / Allimax Pro protocol.** High-dose for 4 weeks. Marginal improvement. Discontinued early due to GI burning sensation.

**December 2024 — Strategy shift.** Realizing repeat antimicrobials weren't producing lasting effects, pivoted to motility-first thinking. Began researching MMC, prokinetics, and the bile-motility axis.

**February 2025 — Started ginger + artichoke prokinetic** (standardized Pycrinil formula, 3 caps at bedtime). First major reduction in nighttime gas pressure since onset.

**May 2025 — Added LDN 3mg.** Prescribed for the autoimmune-feeling component (joint aches, fatigue patterns). Sleep improved within 2 weeks. Overall trajectory turned positive for the first time in years.

**Present (December 2025).** Roughly 70% improvement on the prokinetic + LDN stack. Working on the remaining 30%: residual bloating, occasional flares, expanding tolerated foods.

## Sleep Disruption

| Metric | Detail |
|---|---|
| Wake events per night | 4-8 currently (was 10-15 pre-treatment) |
| Nocturnal pain | Right-lower-quadrant pressure, relieved by passing gas |
| Sleep latency | Normal when bedtime is consistent |
| Morning bloating | Present before any food intake; slowly improving |

## Physical Findings (self-reported)

- **Abdomen:** Visible distension in mid-evening, worse after starchy foods. Tenderness over ileocecal area on deep palpation.
- **Energy:** Mid-afternoon crash, predictable, ~2-3 PM, ~90 minutes if I don't lie down.
- **Mental:** Brain fog tracks with bloating intensity — not independent.
- **Skin:** Occasional rosacea flares correlate with diet violations.

## Laboratory Findings

*Include the labs you've actually run. Don't include normal values you've forgotten — focus on anything abnormal or borderline.*

### GI MAP (March 2022)

| Parameter | Result | Status |
|---|---|---|
| H. pylori | 1.2e3 (ref <1.0e3) | Slightly elevated |
| Bifidobacterium | 8.5e6 (ref >5e7) | Low |
| Lactobacillus | 1.2e7 (ref >5e6) | Normal |
| Akkermansia | <1.0e3 (ref >1.0e4) | Depleted |
| Methanobrevibacter | 5.4e7 (ref <1e7) | Elevated |
| Calprotectin | 105 µg/g (ref <50) | High |
| Secretory IgA | 38 mg/dL (ref >30) | Low-normal |

### Breath Tests

- **02/2021** — Lactulose: H2 peak 38 ppm at 90 min. Positive for hydrogen SIBO.
- **01/2024** — Lactulose: H2 peak 32 ppm + CH4 peak 22 ppm. Positive for SIBO + IMO.

### Blood Work (June 2024)

- TSH: 2.8 mIU/L (high-normal — monitoring)
- Vitamin D: 28 ng/mL (low — supplementing)
- Ferritin: 42 ng/mL (low-normal)
- CBC, CMP, lipid panel: within normal limits

## Complete Intervention History

*Be honest about what worked and what didn't. If you tried something and it did nothing, list it. If something temporarily worked then stopped, say that. The AI is much more useful when it knows what's already been ruled out.*

### Prescription Medications

| Medication | Duration | Response |
|---|---|---|
| Rifaximin 550mg TID — round 1 | 14 days, 03/2021 | Partial. Improvement by day 6. Full relapse within 2 weeks of stopping. |
| Rifaximin 550mg TID — round 2 | 14 days, 08/2021 | No response. |
| Levofloxacin | 7 days, 11/2022 | Partial. 1 week of clear remission, then back. |
| **LDN 3mg** | Ongoing since 05/2025 | **Significant. Energy, sleep, joint pain all improved within 2 weeks.** |

### Natural Antimicrobials

| Treatment | Response |
|---|---|
| Oregano oil | Partial during use, regressed after stopping |
| Berberine | Same pattern |
| Neem | Same pattern |
| Allicin / Allimax Pro | Marginal; tolerability issues (GI burning) |
| Black seed oil | No noticeable effect |

### Probiotics

Tried: Lactobacillus rhamnosus GG, Saccharomyces boulardii, Visbiome, Bio-K+, a soil-based-organism blend.
**Response pattern:** Mild flatulence increase with most. No lasting symptom relief. S. boulardii was best tolerated.

### Gut Support

- L-glutamine 5g/day — mild benefit on stool form
- Zinc carnosine — taken intermittently, hard to evaluate
- DGL (deglycyrrhizinated licorice) — no effect
- Slippery elm — soothing but symptomatic only
- **Betaine HCl with pepsin** — Significant reduction in post-meal bloating. Required for most meals now.

### Prokinetics

| Treatment | Response |
|---|---|
| Iberogast | Mild benefit |
| Ginger alone (low dose) | None |
| MotilPro | Some benefit, less than current stack |
| **Ginger + artichoke (Motility Activator / Pycrinil formula)** | **First major nighttime gas reduction. Current core of protocol.** |

### Antihistamines (suspected MCAS, ruled out)

- Loratadine, cetirizine, famotidine all trialed.
- Famotidine helps the acid-reflux component.
- Other antihistamines: no major effect on primary GI symptoms.
- This patient's symptoms appear **not** to be primarily histamine-driven.

### Dietary Interventions

| Approach | Result |
|---|---|
| Strict low-FODMAP | ~30% baseline symptom reduction. Slow reintroduction in progress. |
| Carnivore (60 days, 2023) | ~50% bloating reduction. Improved brain fog. Unsustainable psychologically/socially. |
| Elemental diet (10 days, 2024) | Cleared symptoms completely. Relapsed within 5 days of refeeding. |
| Periodic extended fasting (24-48hr) | Significant clearing during the fast. Relapse on refeeding. |

### Lifestyle / Nervous System

- Yoga and vagus-nerve breathing — modest help
- Cold exposure (showers, occasional plunges) — neutral
- Sleep hygiene — important; symptoms worse on <7 hrs
- Stress management (therapy, meditation) — clear flare-trigger identified

## Clinical Analysis (working model)

*This is where you put your own theory of what's going on. The AI does much better when it can engage with your hypothesis rather than guess at it.*

### What I currently believe

Post-infectious SIBO (later SIBO + IMO), likely seeded by the 2020 food poisoning event, with secondary motility impairment that has prevented durable clearance through multiple antimicrobial rounds. The pattern — brief partial response then relapse with antimicrobials, sustained improvement only after prokinetic + LDN — suggests motility is the missing variable, not another round of antibiotics.

### What worked vs didn't

**Worked durably:**
- Motility Activator (ginger + artichoke) at bedtime
- LDN 3mg at night
- Betaine HCl with meals
- Real meal spacing (4+ hours, no late snacks)

**Worked temporarily:**
- Rifaximin (only the first round)
- Elemental diet
- Extended fasting
- Herbal antimicrobials during active use

**Did not work:**
- Repeat antimicrobials (rounds 2+)
- Most probiotics
- Most antihistamines
- L-glutamine alone

### Open questions for my doctor

- Is another rifaximin round (this time with motility support throughout) worth trying?
- Should I be on prucalopride given my IMO history and methanogen burden?
- Bile acid sequestrant trial?
- Any value in repeating breath tests before deciding next moves?

## What I want from research right now

*Optional but powerful — telling the AI what you're trying to learn helps it focus searches.*

- Long-term outcomes for people who combined prokinetics with antimicrobial cycling
- Reported experiences with prucalopride for refractory methane-dominant SIBO
- Whether anyone has documented sustained remission after a rifaximin → herbal → prokinetic sequence
- Histamine intolerance overlap with my pattern — worth investigating despite negative antihistamine response?

---

## Tips for filling this out

- **Specificity > completeness.** A short, detailed timeline beats a long vague one. "Tried X, no effect" is less useful than "Tried X 50mg/day for 6 weeks, gradual onset of headaches by week 3, no GI improvement."
- **Update it.** This is a living document. Add new events as they happen.
- **Don't fake symptom severity.** The AI will give you better answers if you're honest about what's a 10/10 vs a 4/10.
- **Include what didn't work.** "Ruled out" is genuinely valuable information.
- **List your working theory.** The AI is much better at engaging with a hypothesis than constructing one from scratch.

## What this template is not

- Not a diagnostic tool
- Not a replacement for actual medical records
- Not a substitute for your doctor or for clinical research
- Not something to feed any AI you don't trust with sensitive health data

Keep this file local. Set the `SIBO_REPORT` env var in your AI tool's MCP config and the AI can read it for you on demand — without it being uploaded, transmitted, or stored anywhere outside your machine.
