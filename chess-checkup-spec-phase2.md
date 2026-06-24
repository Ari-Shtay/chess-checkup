# Chess Checkup: Phase 2 Spec Addendum
Date: June 20, 2026. This extends the original spec. Where the two conflict, this wins, because the product direction changed after launch prep.

## The shift in one sentence
The diagnosis is no longer the whole product. It becomes the doorway: a visitor runs a checkup, sees their biggest weakness, and is then pushed into training that fixes it, using the player's own data. The training is the product now; the diagnosis is the setup.

## Why this changed
Two independent signals (a builder in the same space, and Ari's own gut) said the diagnosis alone can feel obvious, since at the 1000 to 1800 band the honest answer is often just "fix your tactics." The cure for "obvious" is not a prettier page, it is depth: a tool that does more and goes deeper, specific to the player. Training built from the player's own games is specific, impossible to fake, and impossible for a general chatbot to copy.

## The new structure (user side)
1. A simplified, de-emphasized first page. One line on what it does, the username box, the example. Calm and uncrowded. Its only job is to get someone to run a checkup. The first page is deliberately lighter than before, because the weight moved deeper into the product.
2. The checkup runs (existing loading state and diagnosis, unchanged) and ends by pointing forward into the tabs instead of stopping.
3. Two tabs appear after a checkup:
   - **Your own blunders** (the differentiator, build first). Puts the user on the board one move before a real blunder from their actual games and asks them to find the better move. They solve it, then a reveal: "and here is what you actually played," a pause, then their real blunder. Walks through several. Roast tone (see below). Teaches by doing, not by explaining.
   - **Train your weaknesses** (build second). Curated puzzles from the Lichess puzzle database, filtered to the player's weak themes, in proportion to their severity. Same solve-on-a-board interaction, sourced from the puzzle database instead of their own games.

## Locked decisions
- First page gets simplified and de-emphasized. The diagnosis stays but becomes the entry point and ends by pushing into the tabs.
- Two tabs, both built on the same interactive board: "Your own blunders" first, "Train your weaknesses" second.
- The playable board is the one new technical piece and was built and proven in isolation first (board-test.html, using chess.js plus cm-chessboard, both from CDN). Tap-to-move and drag both work, with legal-move markers in the Lichess/chess.com style. This is the foundation both tabs reuse.
- "Solving" a position: the correct move is the engine's best move (from the Lichess analysis already used), with a small tolerance so an equally good second move also passes. Wrong moves let the user retry with no lockout; after two misses, offer a "show me."
- The puzzle split across themes is dynamic, driven by the player's severity scores relative to each other. Not a fixed ratio.
- Roast tone for "Your own blunders": playful "look at this disaster" energy on the reveal, but it scales. Full roast only for genuinely bad blunders; gentler for marginal slips, so the humor never turns into the tool just being mean.
- No written explanations of mistakes. The interaction (solve it yourself, then see what you played) replaces the explanation. This is deliberate: auto-writing chess explanations would require an AI model, which would reintroduce the AI-generated text Ari spent the project removing, on the one feature where being wrong is most embarrassing. The "show your mistakes" idea is honored as a board to play, not an essay to read.

## Build order (each its own focused session)
1. Build and prove the interactive board in isolation. DONE (board-test.html).
2. Build "Your own blunders" on top of the board, reusing the existing blunder detection, with the solve-then-roast reveal. Handle users who have few clean blunder positions gracefully (pull from more games if needed).
3. Separately, prove the Lichess puzzle database loads and filters by theme before building any puzzle UI.
4. Build "Train your weaknesses" on top of the board, split by severity scores.
5. Restructure into tabs and simplify the first page last, once the tabs exist to point to.

## What stays true from the original spec
One HTML file, vanilla JS, no framework (a chess board library and chess.js from CDN are allowed, since the board genuinely needs them). The diagnostic-report aesthetic. No AI tells. No em dashes. The honest, no-slop voice. Verify against real data, never guess. Show Ari the result before committing.

## Puzzle tab scope decision (June 20)
The diagnosis-to-puzzle-theme mapping was reviewed against real puzzle availability. Only two of the five categories map cleanly to puzzles, and those are the two biggest levers for improvers anyway:
- Tactical safety: maps strongly (fork, pin, skewer, hangingPiece, discoveredAttack, deflection, and similar tactical motifs).
- Endgames: maps cleanly (rookEndgame, pawnEndgame, queenEndgame, bishopEndgame, knightEndgame, plus zugzwang and promotion).
The other three were deliberately dropped from the puzzle tab, not forced in: converting winning positions (the available themes really just mean "win material," which duplicates tactics), opening reliability (a repertoire problem, not a puzzle problem, see the planned opening trainer below), and time and decision-making (a process skill untimed puzzles cannot train). The served puzzle mix is weighted by the player's severity scores across the two mappable categories, in proportion to each other, not a fixed ratio, pulled in a rating band around the player's Lichess rating.

## Planned future tab: Opening trainer
Openings were kept out of the puzzle tab because they are a different kind of problem (drilling correct lines until known, closer to flashcards than to solving a position). The planned opening trainer is the personalized version that fits Chess Checkup's identity: the diagnosis already names the specific opening the player keeps failing with, so the trainer would surface the correct lines for that exact opening and let the player drill them. This is a real future build, not a someday-maybe, but it is deliberately sequenced AFTER the puzzle tab and the tab restructure, so it can be informed by how players actually use the blunder and puzzle tabs first. Ari has prior experience here (a chessreps-style opening trainer with study and drill modes), which lowers the lift. The bigger-effort, on-brand version (personalized to the diagnosed opening, needing a source of correct lines plus a drilling mechanic) is preferred over a generic "pick any opening and drill it" tool.

## Still parked (deliberate decisions, not now)
- Rich written explanations of mistakes. Only if Ari later decides the AI tradeoff and cost are worth it. Default is off.
- Progress over time (save a result, return later, see the weakness shrink). A strong future feature, but after the two trainers exist.
- chess.com support and in-browser analysis of unanalyzed games. Both are projects, not touch-ups.
- A final copy pass written by Ari himself, across the whole site and both trainers, replacing all placeholder and AI-sounding text. This is the agreed fix for voice: the words must be Ari's, since generated copy reads as AI. All text work waits for this pass.
