# Lichess API data notes (verified against real responses, June 10, 2026)

Findings from the Session 1 smoke test required by spec sections 3 and 10.
Endpoint: `GET https://lichess.org/api/games/user/{username}` with
`max, rated, perfType, analysed, evals, clocks, opening, sort` params and
`Accept: application/x-ndjson`. Sample: 100 analyzed rated rapid/classical
games for Ari_Ferrari_0.

## CORS (section 10 open question — RESOLVED)
Direct browser calls work. Response includes `access-control-allow-origin: *`.
No Vercel proxy needed.

## NDJSON game shape
- `moves`: single space-separated SAN string.
- `analysis`: array, one entry per ply. `analysis[i]` is the eval of the
  position **after** move `i`. Entries are `{eval: <centipawns, White POV>}`
  or `{mate: <signed moves-to-mate, White POV>}` (240 of 6650 plies in the
  sample were mate scores — must be handled). Bad moves additionally carry
  `best`, `variation`, and `judgment {name, comment}`.
- In games ending in checkmate, `analysis` has one FEWER entry than moves
  (the final position is not evaluated). True for all 12 mate games sampled.
- `clocks`: array of **centiseconds**; `clocks[i]` is the mover's remaining
  time after ply i (white = even indices). Usually `moves + 1` entries
  (87/100 games), sometimes equal (13/100). Index by ply, ignore extras.
- `clock`: `{initial, increment, totalTime}` in **seconds**. Needed to compute
  time spent per move: `spent = clocks[i-2] - clocks[i] + increment*100`.
- `winner`: `"white"`/`"black"`, **absent entirely on draws** (4/100 games).
- `players.{color}.analysis`: Lichess's own `{inaccuracy, mistake, blunder,
  acpl}` — used as a cross-check against our computed ACPL.
- `opening`: `{eco, name, ply}`. Family = name up to the first `:`.
- `status` values seen: `resign`, `mate`, `outoftime`, `draw`.

## Win-probability formula (section 10 open question — RESOLVED)
Copied from lichess-org/scalachess `core/src/main/scala/eval.scala`:

    winningChances(cp) = 2 / (1 + exp(-0.00368208 * cp)) - 1   // clamped [-1, 1]
    WinPercent = 50 + 50 * winningChances(cp)                   // cp ceiled at ±1000

Mate scores map to the ±1000 cp ceiling (`Cp.ceilingWithSignum`).

## Interpretation choices made in index.html (tunable, flagged for review)
- Mate eval entries → ±1000 cp (the Lichess ceiling).
- "Missed win" implemented literally per spec: swing ≥ 250cp inside the ±500
  sanity window. Overlaps with the blunder count by design.
- Phase priority: endgame material condition wins over the ply-24 opening
  cutoff (early queen trades count as endgame).
- Opening exit eval: games shorter than 24 plies use the final available eval.
- "Non-forced position" for snap-blunders = more than 1 legal move.
- Eval before move 1 treated as 0 cp.
