# Chess Checkup: Master Spec v1.1
Date: June 10, 2026. Status: name locked, accounts created, ready for build session 1.
Note for Claude Code: this file is the source of truth for the project. Follow it. Where it marks something as tunable or unverified, verify against reality before relying on it, and never guess data formats from memory when the real API response is one curl away.

## 1. What this is

A free web tool: enter your Lichess username, it reads your real games, names the ONE weakness costing you the most rating right now, shows the evidence, and hands you the single best resource to fix it. Sometimes that resource is free. Sometimes it is "you don't need to buy anything, you need to change a habit." That honesty is the product.

Positioning for the college resume: a business experiment, not just a tool. The hypothesis being tested: "improving players will trust and act on a personalized, evidence-backed study recommendation." Users are the evidence. Affiliate and subscription are the thesis. A well-documented yes or no is the win either way.

## 2. Locked decisions

1. Lichess first. Free open API, no auth needed for public games, evals and clock data included. Chess.com support comes later (its API has no evals, so it needs our own engine pass).
2. Target user: the 1000 to 1800 online improver who plays rapid or classical.
3. Output: one primary diagnosis plus a ranked list of the rest, each with confidence labels. Never a flat list of six problems.
4. Format-agnostic recommendations. Books are the flagship, but free tools and habit changes are given whenever they are honestly better.
5. The organic recommendation is never for sale. No sponsored placement in v1 at all.
6. v0 has no accounts, no database, no payments. Anonymous, instant, free. Subscription only gets built if v0 proves demand.
7. Launch with plain links, no affiliate tags. Apply for affiliate programs only after the site is live with content and traffic (this is also what Amazon requires, see section 7).
8. Name: Chess Checkup. Chosen after checking for collisions (BlunderLab was rejected because BlunderLabs.com already exists in this exact space). The product language follows the name: checkup, diagnosis, evidence, prescription. v0 ships on the free Vercel subdomain, a custom domain waits until the launch gate is hit.
9. Owner setup completed: GitHub repo (chess-checkup, public), Vercel account linked to GitHub, Lichess-first confirmed by Ari.

## 3. The diagnosis engine

### Data input
Endpoint: `GET https://lichess.org/api/games/user/{username}`
Parameters: `max=100, rated=true, perfType=rapid,classical, analysed=true, evals=true, clocks=true, opening=true, sort=dateDesc`
Format: NDJSON (one JSON game per line) or PGN. NDJSON is easier to parse.

Verified facts about this endpoint:
- evals=true includes engine evaluation comments, but only for games that already have Lichess server analysis. That is why we filter analysed=true in v0.
- clocks=true includes per-move clock comments.
- The analysed filter parameter exists in the API.
- Anonymous access works at usable speed (a forum user measured roughly 20 games per second).

Honest limitation to disclose in the UI: v0 only reads games the user (or their opponent) requested analysis for. That sample can be biased toward interesting games. The tool says this in small print. v1 fixes it by running Stockfish WASM in the browser on unanalyzed games.

Minimum sample rule: fewer than 15 usable games means the tool refuses to diagnose and instead tells the user how to get more analyzed games. Refusing to guess is a feature.

### Definitions (all tunable constants, keep them in one config file)
- Win-probability conversion: use the Lichess open-source formula that maps centipawns to win percent (the exact constant is in the lichess accuracy code on GitHub, copy it from there during the build). Simpler v0 fallback: raw centipawn thresholds below.
- Blunder: eval swing of 200+ centipawns against the mover, measured only while the position was within plus or minus 500 centipawns (swings in already-decided positions are noise).
- Winning position: eval at or beyond +300 centipawns for the user, held for at least 2 consecutive plies.
- Endgame: both queens off the board, or each side has 13 or fewer points of non-pawn material (Q=9, R=5, B/N=3). Requires replaying moves with chess.js to count material.
- Opening exit: move 12 (ply 24).

### The five categories, their signals, and their metrics

1. TACTICAL SAFETY AND VISION (usually the primary diagnosis at this level)
   - Metric A: blunders per game while the position was roughly equal (within 200cp).
   - Metric B: missed wins, positions where the engine best move gains 250+ cp over the move played.
   - Why it ranks first by default: at 1000 to 1800 the largest share of rating is lost to single-move tactical errors. The weighting reflects that.

2. ENDGAME TECHNIQUE
   - Metric A: average centipawn loss in the endgame phase versus the middlegame phase (a big gap means endgames specifically are the leak).
   - Metric B: games entering the endgame at +200cp or better that ended in a draw or loss.

3. HOLDING A WINNING POSITION (conversion)
   - Metric: of all games that reached "winning" (+300cp sustained), the share that did not end in a win. The threshold for flagging this gets calibrated from real user data, not invented. v0 flags it only when the user's rate is clearly worse than their other metrics, relative comparison, not an absolute baseline.

4. OPENING RELIABILITY
   - Metric A: average eval at move 12, grouped by opening family (the opening field in the API gives the name and ECO code).
   - Metric B: recurring disaster, the same opening family appearing 3+ times with eval at or below -100cp at move 12.
   - Metric C: scatter, the count of distinct opening families in the sample. Many families and shallow results means "too many openings," which is its own diagnosis.

5. TIME AND DECISION PROCESS
   - Metric A: share of losses that were on time (game status field).
   - Metric B: blunders made with under 20 seconds or under 10 percent of starting time remaining.
   - Metric C: snap-move blunders, blunders on moves where the clock delta shows under 10 seconds of thought in a non-forced position.

### Ranking and output
Each category gets a severity score: normalized metric, times a band weight (tactics weighted highest by default), times a confidence factor from sample size. The top score is the primary diagnosis. Confidence labels: under 15 games, refuse; 15 to 30, low; 30 to 60, medium; over 60, high. If no category clearly leads (top two scores within 15 percent of each other), the tool says so honestly and shows both.

## 4. The curation database v1 (verified June 10, 2026)

Every item below was confirmed to exist via web search today. Default means the first thing the tool hands over.

### Category 1: Tactics
- DEFAULT (free): a structured Lichess puzzle protocol. Specific, not vague: 20 minutes daily, mixed themes, solve slowly and fully before moving, no streak-chasing. The tool prints the protocol.
- PAID OPTION: The Woodpecker Method, Axel Smith and Hans Tikkanen, Quality Chess, 2018, 1100+ exercises. Verified: the method is solving the same large set repeatedly, faster each cycle, and the authors deliberately chose simpler tactics to make it accessible and to mirror real games. Paperback runs roughly 27 to 32 dollars. Honest framing in the tool: this is for the committed, it is a workload, and the free protocol covers most people. Note: Woodpecker Method 2 exists (verified) but covers positional problems, not tactics, so it is NOT the recommendation here. Do not confuse them.
- BUDGET OPTION: the classic Reinfeld 1001 puzzle collections, cheap and battle-tested.

### Category 2: Endgames
- DEFAULT: Silman's Complete Endgame Course, Jeremy Silman, Siles Press. Verified: organized by rating class so a 1300 reads the 1300 chapter and stops. That structure maps one-to-one onto our diagnosis model, which is why it beats every alternative as the default. Available in paperback and Kindle.
- UPPER BAND OPTION (1500+): 100 Endgames You Must Know, Jesus de la Villa, New in Chess. Verified: excellent and beloved, and also verified that the author himself positions it as second-phase endgame study, so it is wrong as a first book for the lower band. A Chessable course version exists (verified) for people who prefer spaced-repetition training to reading.

### Category 3: Holding a winning position
- DEFAULT (no purchase): a printed process protocol. When you realize you are winning: slow down for one full minute, ask what the opponent's only tricks are, trade pieces not pawns, stop hunting for brilliancies. The tool presents this as the fix.
- OPTIONAL BOOK: A Guide to Chess Improvement: The Best of Novice Nook, Dan Heisman, Everyman Chess. Verified: the book explicitly covers prioritizing to maintain won positions, thought process, and technique. It double-serves category 5, which is efficient for our database.

### Category 4: Openings
- DEFAULT (free): the honest advice "study openings less, pick one weapon," plus a Chessable Short and Sweet course for the user's most-played first move. Verified: Short and Sweets are free Chessable courses, typically 10 to 30 annotated lines, often with video, real mini-repertoires. Zero cost to try a repertoire before committing.
- BOOK OPTION: Discovering Chess Openings: Building a Repertoire from Basic Principles, John Emms, Everyman Chess, 2006, 192 pages. Verified: teaches development, center, and king safety as principles instead of memorized lines, written by a GM coach, aimed at beginners and improvers. Roughly 15 dollars. This is the pick precisely because it talks people out of memorizing theory.

### Category 5: Time and decision process
- DEFAULT (no purchase): a process protocol. Budget the clock by phase, adopt a one-line blunder check before every move (what does this piece leave undefended, what is their check, capture, or threat), and review every time-loss for where the time actually went.
- OPTIONAL BOOK: the same Heisman book as category 3. Verified: time management is one of its core listed subjects.

Database shape note: two of five categories lead with "buy nothing," one leads with a free course, and the two purchase-led categories lead with the two most consensus-backed books in chess instruction. That asymmetry is deliberate. It is the trust engine.

## 5. Output copy templates

Primary diagnosis card:
"Your number one leak: [category]. In your last [N] analyzed games, [evidence sentence with the user's actual numbers]. Players in your range usually gain more rating fixing this than anything else. Confidence: [low/medium/high] based on [N] games."

Evidence sentence examples:
- Tactics: "you lost 200+ centipawns in one move 1.8 times per game in equal positions."
- Conversion: "you reached a clearly winning position in 14 games and only won 8 of them."
- Time: "6 of your last 11 losses were on time, and 70 percent of your blunders came with under 20 seconds left."

Recommendation card:
"The fix: [resource or protocol]. Why this one: [one or two sentences of reasoning]. [If paid: price range and a plain link.] [If a cheaper or free path covers it: say so first.]"

Refusal card (under 15 games):
"Not enough analyzed games to diagnose you honestly. Here is how to get more: [instructions for requesting analysis on Lichess]. We would rather say 'not enough data' than guess."

Footer, always visible:
"Recommendations are never sponsored. If we ever add affiliate links, we will say so right here." (Swap to the FTC disclosure line in section 7 once affiliate is live.)

## 6. Tech spec

Stack (revised from v1, which said React): one plain HTML file with vanilla JavaScript, no frameworks and no build step. Reasons: it deploys to Vercel as a static file instantly, there is no toolchain to break for a first-time GitHub user, and the entire v0 is one input box and a results panel, which does not need React. chess.js loaded from a CDN for move replay and material counting. Refactor to React later only if the UI genuinely outgrows this. No backend, no database, no accounts in v0.

Session 1 working rule: fetch one real game from the API and inspect the actual response shape before writing any parsing code. Lichess may deliver evals and clocks differently in NDJSON versus PGN format (inline arrays versus PGN comments). Match the code to what the real response shows, not to assumptions, and prefer whichever format is cleaner to parse based on what comes back.

Data flow:
1. User enters username.
2. Browser fetches the Lichess endpoint from section 3. If the browser blocks the call on CORS (test this first thing, Lichess generally allows it on public endpoints but verify in practice), fall back to a 10-line serverless proxy on Vercel.
3. Stream-parse NDJSON. For each game: replay moves with chess.js, tag each ply with phase, parse eval and clk comments, compute the per-category metrics.
4. Score, rank, render the cards from section 5.

Outbound link click tracking without a backend: route resource links through a free link shortener that reports click counts. Crude but it answers the launch question (do people click) with zero infrastructure.

Feedback capture: a Google Form linked under the diagnosis, three questions. Did the diagnosis feel accurate (yes, partly, no). Did you open the recommended resource. Your rating range. This form is the v0 version of the outcome-data moat.

Explicitly NOT in v0: accounts, payments, chess.com support, in-browser Stockfish, progress tracking, the questionnaire layer. Every one of these waits for proof of demand.

## 7. Money and trust rules (corrected after verification)

Verified affiliate reality, which is thinner than assumed earlier in planning:
- Amazon books: about 4.5 percent commission. A 25-dollar book earns about a dollar. The 24-hour cart window helps slightly.
- Chess.com runs an affiliate program paying around 15 percent standard commission on memberships, but explicitly not on their courses.
- Chessable: per recent reporting, affiliates can currently only promote Chessable PRO subscriptions, not individual courses. The earlier working assumption that course affiliates pay 10 to 30 percent was wrong and is hereby corrected. This makes affiliate even more of a side dish and strengthens the case that the long-term business (if any) is the subscription relationship, not commissions.

Verified Amazon Associates requirements, which dictate sequencing:
- Applicants must be able to lawfully enter contracts, meaning not a minor. A parent or guardian must own the account, the tax info, and the payment details. This is a when-you-get-there logistics item, not a blocker, and it is one of the reasons v0 launches with plain links.
- Amazon requires a live site with original content before applying, and three qualifying sales within 180 days of approval or the account closes.
- FTC disclosure is mandatory once links are live. Standard line: "As an Amazon Associate, this site earns from qualifying purchases."

Trust rules, permanent:
- The organic recommendation is never for sale.
- Any future sponsored slot is labeled, sits beside the organic pick, and never replaces it.
- Free recommendations are shown first whenever they are honestly the best fix.

## 8. Build plan (about 10 to 13 hours total)

Session 1, data pipeline (3 to 4 hours): fetch and parse for Ari's own account, compute all five metric sets, print to console. Done when the numbers for a known account look sane.
Session 2, brain and face (3 to 4 hours): scoring, ranking, confidence labels, render the diagnosis and recommendation cards. Done when a stranger's username produces a coherent one-screen result.
Session 3, honesty pass (2 to 3 hours): the refusal card, the sample-bias disclosure, the never-sponsored footer, error states, deploy to Vercel free tier.
Session 4, launch prep (1 to 2 hours): Google Form, shortened outbound links, test on 5 chess club friends, fix what confuses them.

## 9. Launch plan and the decision gate

Order: chess club friends first (5 to 10 users, fix the confusing parts), then Reddit. Check the current self-promotion rules of r/chess and r/chessbeginners before posting, subs change these rules often and some require posting in designated threads.

Draft post (tune the numbers to whatever is true at posting time):
"I'm a high school student and a ~1900 player. I got frustrated trying to figure out which chess book to buy, so I built a free tool instead. You enter your Lichess username, it reads your analyzed rapid and classical games, and it tells you the single weakness costing you the most rating, with the evidence, plus one honest resource to fix it. Two of the five possible diagnoses tell you to buy nothing at all. No ads, no sponsors, no signup. I'd genuinely like to know if the diagnosis feels accurate to you, there's a 3-question feedback form on the result page."

Success gate, measured over roughly 2 to 3 weeks:
- 100 or more diagnoses run
- 10 or more feedback responses with at least 70 percent saying the diagnosis felt accurate or partly accurate
- A nonzero, measurable click rate on resource links

Hit the gate: proceed to accounts, re-assessment, and the subscription experiment. Miss it: write up why, with the data, and that writeup is itself the resume artifact. Both outcomes complete the project.

## 10. Verification log (what was checked today, June 10, 2026)

Confirmed real and accurately described:
- The Woodpecker Method (Smith and Tikkanen, Quality Chess 2018, 1100+ repeated-cycle tactics exercises; WM2 exists but is positional, excluded on purpose)
- Silman's Complete Endgame Course (organized by rating class, the core reason it is our default)
- 100 Endgames You Must Know (real, Chessable version real, repositioned to the upper band because the author frames it as second-phase study)
- Discovering Chess Openings (Emms, Everyman 2006, principles over memorization, aimed at improvers)
- A Guide to Chess Improvement (Heisman, covers time management and maintaining won positions, double-serves two categories)
- Chessable Short and Sweet courses (free, 10 to 30 lines, real mini-repertoires)
- Lichess API parameters: evals, clocks, opening, analysed filter, anonymous access
- Amazon Associates: book rate near 4.5 percent, adult account holder required, live site required before applying, 3 sales in 180 days, FTC disclosure

Corrected during verification:
- Chessable course affiliate commissions of 10 to 30 percent: wrong, affiliates currently promote PRO only. Monetization expectations revised down.
- 100 Endgames as a co-equal default: wrong for the lower band, now upper-band only.

Still open, verify during the build (cannot be confirmed from a phone today):
- Whether the Lichess endpoint allows direct browser calls (CORS) or needs the tiny proxy
- The exact win-percent constant, copy it from the Lichess accuracy source on GitHub
- Current self-promotion rules of the target subreddits at posting time
- Live prices at posting time

## 11. Task list and status

Done: name (Chess Checkup), Lichess-first confirmed, GitHub repo created, Vercel account created and linked.

Remaining, in order:
1. Build sessions 1 through 4 with Claude Code, following section 8. Session 1 first task: the API smoke test and CORS check from section 10.
2. Make the Google Form (3 questions, listed in section 6).
3. Recruit the 5 to 10 chess club testers.
4. Check subreddit rules, adapt the draft post in section 9, and post it.
5. Later, only if the launch gate in section 9 is hit: a parent or guardian holds the Amazon Associates account, since the program requires an adult account holder.

Everything else is decided, verified, and written down. Build.
