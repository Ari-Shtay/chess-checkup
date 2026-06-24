#!/usr/bin/env python3
"""
Generate the pre-baked puzzle packs for the "Train your weaknesses" trainer.

Streams the bulk Lichess puzzle database (CC0, ~286 MB zstd) once and fills
(theme, rating-band) buckets for the two diagnosis categories that map to
puzzles: tactical safety and endgames. Writes two JSON files next to this
script: tactical-puzzles.json and endgame-puzzles.json.

The file is sorted by PuzzleId (random vs. theme/rating), so a small prefix
already yields full coverage; this fills every (theme, band) slot in well
under a minute / ~5 MB downloaded.

Requires the `zstandard` module:  python3 -m pip install --user zstandard
Run:  python3 gen_packs.py   (re-run to refresh against a newer DB dump)
"""
import urllib.request, zstandard as zstd, io, csv, json, time, os

URL = "https://database.lichess.org/lichess_db_puzzle.csv.zst"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

TACTICAL = ["fork","pin","skewer","hangingPiece","discoveredAttack","deflection",
            "attraction","trappedPiece","capturingDefender","doubleCheck","intermezzo","sacrifice"]
ENDGAME  = ["rookEndgame","pawnEndgame","queenEndgame","bishopEndgame","knightEndgame",
            "queenRookEndgame","zugzwang","promotion"]

BAND_LO, BAND_HI, BAND_W = 800, 2400, 200
NBANDS = (BAND_HI - BAND_LO) // BAND_W      # 8 bands: [800,1000)...[2200,2400)
K = 14                                      # puzzles per (theme, band)

def band_idx(r):
    if r < BAND_LO or r >= BAND_HI: return None
    return (r - BAND_LO) // BAND_W

class Counter(io.RawIOBase):
    def __init__(self, fp): self.fp = fp; self.n = 0
    def readable(self): return True
    def readinto(self, b):
        c = self.fp.read(len(b))
        if not c: return 0
        b[:len(c)] = c; self.n += len(c); return len(c)

def make_slots(themes): return {t: [[] for _ in range(NBANDS)] for t in themes}
slots = {"tactical": make_slots(TACTICAL), "endgame": make_slots(ENDGAME)}
seen = {"tactical": set(), "endgame": set()}
order = {"tactical": TACTICAL, "endgame": ENDGAME}

def full(cat):
    return all(len(slots[cat][t][b]) >= K for t in order[cat] for b in range(NBANDS))

req = urllib.request.Request(URL, headers={"User-Agent": "chess-checkup-packgen/0.1"})
resp = urllib.request.urlopen(req, timeout=120)
counter = Counter(resp)
reader = zstd.ZstdDecompressor().stream_reader(counter)
text = io.TextIOWrapper(io.BufferedReader(reader), encoding="utf-8", newline="")
r = csv.reader(text); next(r)

MAX_ROWS = 1_200_000
scanned = 0
t0 = time.time()
for row in r:
    scanned += 1
    try: rating = int(row[3])
    except (ValueError, IndexError): continue
    bi = band_idx(rating)
    if bi is None: continue
    ths = set(row[7].split())
    pid, fen, moves = row[0], row[1], row[2]
    for cat in ("tactical", "endgame"):
        if pid in seen[cat]: continue
        for t in order[cat]:
            if t in ths and len(slots[cat][t][bi]) < K:
                slots[cat][t][bi].append({"id": pid, "fen": fen, "moves": moves, "rating": rating, "theme": t})
                seen[cat].add(pid)
                break
    if scanned >= MAX_ROWS or (full("tactical") and full("endgame")):
        break
try: resp.close()
except Exception: pass
dt = time.time() - t0

def flatten_and_write(cat, themes, fname):
    puzzles = []
    for t in themes:
        for b in range(NBANDS):
            puzzles.extend(slots[cat][t][b])
    obj = {"category": cat, "themes": themes,
           "band_lo": BAND_LO, "band_hi": BAND_HI, "band_w": BAND_W,
           "count": len(puzzles), "puzzles": puzzles}
    path = os.path.join(OUT_DIR, fname)
    with open(path, "w") as f:
        json.dump(obj, f, separators=(",", ":"))
    kb = os.path.getsize(path) / 1024
    print(f"{cat}: {len(puzzles)} puzzles -> {fname} ({kb:.0f} KB)")
    for t in themes:
        per_band = [len(slots[cat][t][b]) for b in range(NBANDS)]
        print(f"   {t:<18} total {sum(per_band):>4}   per-band {per_band}")
    return len(puzzles)

print(f"Scanned {scanned:,} rows in {dt:.1f}s (~{counter.n/1e6:.0f} MB compressed read).")
print(f"Bands: {[f'{BAND_LO+i*BAND_W}-{BAND_LO+(i+1)*BAND_W}' for i in range(NBANDS)]}, K={K}/band\n")
nt = flatten_and_write("tactical", TACTICAL, "tactical-puzzles.json")
ne = flatten_and_write("endgame", ENDGAME, "endgame-puzzles.json")
print(f"\nTOTAL {nt+ne} puzzles across both packs.")
