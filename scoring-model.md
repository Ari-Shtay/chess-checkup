# Chess Checkup — Scoring & Ranking Model

How Session 2 turns the five category metric-sets (spec §3) into one ranked
diagnosis. Every constant named here lives in the `SCORE` block in `index.html`
and is tunable. Designed via a judge panel of independent proposals, then
hardened by an adversarial review pass (see commit history).

## Overview

```
score[k] = rawSeverity[k]  ×  bandWeight[k]  ×  confidenceFactor(n)
```

Top score = primary diagnosis. Co-leaders within 15% of the leader are shown
together honestly. A leader below a small floor means "no single leak stands
out." Below 15 games the tool refuses to diagnose.

Every raw severity uses one shared map so the categories are comparable despite
different units (per-game counts vs centipawns vs shares):

```
sat(x, ref) = clamp01(1 - exp(-x / ref))    // bounded, monotone, ~0.63 at x = ref
```

All denominators are guarded; a category with no data contributes 0, never NaN.

## Band weights (spec §3: "tactics weighted highest by default")

`cat1 1.00  cat2 0.80  cat3 0.85  cat4 0.75  cat5 0.80`

Tactics is highest because §3 says the most rating at 1000–1800 is lost to
single-move tactical errors. The spread is deliberately shallow so the band only
breaks genuine near-ties — a category still has to earn its raw severity.

## Confidence factor (spec §3 sample-size bands)

```
n < 15   -> REFUSE        15–30 -> low 0.55
31–60    -> medium 0.80   > 60  -> high 1.00
```

The factor genuinely shrinks thin samples so they cannot produce a loud diagnosis.

## Per-category normalization (all → [0,1])

- **cat1 TACTICS** — `0.6·sat(eqBlundersPerGame, 0.60) + 0.4·sat(missedWinsPerGame, 0.70)`.
  Two per-game rates (n-invariant), blended 60/40 toward the spec's named dominant signal.
- **cat2 ENDGAME** — `0.6·sat(max(0, egVsMgGapCp), 25) + 0.4·( sat(goodEntriesNotWon/goodEndgameEntries, 0.50) · clamp01(goodEndgameEntries/4) )`.
  Only a *positive* endgame-worse-than-middlegame gap is a leak; the spoil term is
  sample-trust-shrunk so 1-of-2 spoiled entries can't read as a 50% crisis.
- **cat3 CONVERSION** — relative, never absolute (see below).
- **cat4 OPENINGS** — `max(sigB, 0.85·sigC)`. `sigB = sat(worstShare, 0.40)` where
  worstShare = the highest `disasters/games` among recurring-disaster families.
  `sigC` (scatter) fires only when avg games/family < 4. Scatter is discounted 15%
  so a concrete named disaster beats diffuse scatter at equal magnitude.
- **cat5 TIME** — `0.34·sat(lossesOnTimeShare, 0.30) + 0.33·sat(lowTimeBlunderShare, 0.40) + 0.33·sat(snapShare, 0.40)`.
  On-time term is shrunk when losses < 5 (noisy). Each term guards its own zero denominator.

## cat3 is relative, not absolute (spec verbatim)

Computed **last**, against the user's own other four base raws:

```
peers = [raw1, raw2, raw4base, raw5base]      // pre-specificity base raws
z     = (conversionFailureShare - mean(peers)) / max(populationSD(peers), 1e-9)
raw3  = 0                if conversionFailureShare is null, gamesReachedWinning < 8, or z <= 0
      = sat(z, 1.5)      if z > 0
```

So identical conversion-failure shares score 0 for a sloppy player and high for
an otherwise-clean one. (Ari: z = −4.6 → raw3 = 0, correct — his conversion is
far *better* than his other leaks.)

## "Specific beats generic" (owner rule — affects score AND copy)

Additive bonuses on the base raws, then clamp01:

```
if any recurring-disaster opening:  raw4 += 0.20·sat(worstShare, 0.40)
if snapShare >= 0.30:               raw5 += 0.10·sat(snapShare, 0.40)
```

A named opening can climb the *ranking* (a 70%-failing line out-ranks diffuse
tactics) and is named in the *evidence text*; snap-share is half the opening
bonus. Diffuse signals (scatter, plain ACPL gap) get no bonus.

## Modes / tie rule (spec §3)

```
sort scores desc; lead = scores[0]
if lead == 0 or lead < 0.12          -> "clean"  (no single leak stands out)
coLeaders = scores.filter(s => s > 0 && (lead - s)/lead <= 0.15)
coLeaders.length >= 2                -> "tie"     (show each, with evidence + fix)
else                                 -> "single"
```

A *filter* (not a bare top-two check) so 3-way ties render honestly.
The ranked remainder only treats a row as a real signal when its score ≥ 0.12
(the leak floor) — sub-floor rows show "no meaningful signal" rather than a
near-zero evidence sentence.

## Resource mapping (spec §4 — free shown first whenever honestly best)

| Cat | Default | Optional |
|-----|---------|----------|
| cat1 | FREE Lichess puzzle protocol | Woodpecker Method (~$27–32); Reinfeld 1001 budget. Never Woodpecker 2 (positional). |
| cat2 | Silman's Complete Endgame Course | 100 Endgames You Must Know — only when **median** sample rating ≥ 1500 (second-phase book). |
| cat3 | FREE process protocol | Heisman *Best of Novice Nook* (always offered; "double-serves" note added only when cat5 also elevated). |
| cat4 | FREE "one weapon" + Chessable Short & Sweet (aimed at the named family) | Discovering Chess Openings (~$15) — only when scatter-driven. |
| cat5 | FREE process protocol | Heisman *Best of Novice Nook* (always offered; double-serve note only when cat3 also elevated). |

All links are plain (no affiliate tags) per spec decision 7.

## Verified outcome for Ari (live data, n=100, high confidence)

| Category | score |
|----------|-------|
| Tactical safety | **0.55–0.57 (primary)** |
| Opening reliability (Queen's Pawn / Caro-Kann named, +0.20 bonus) | 0.46 |
| Time & decision process (snap ~37%, +0.10 bonus) | 0.41 |
| Endgame technique | 0.26 |
| Holding a winning position | 0.00 |

Single clear primary (tactics), gap to openings ≈ 16–19% (> 15%), conversion
correctly zeroed. Numbers drift slightly as Ari plays more rated games.
