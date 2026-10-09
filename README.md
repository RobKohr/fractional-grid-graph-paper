# Fractional grid graph paper

Printable dot-grid PDFs with nested fractional spacings (4×, 1×, ½×, ¼×, and ⅓× of a configurable **base unit**). Each file has **two identical pages**, **zero margins**, and the grid is anchored from the **upper-left** corner (large **4×** dot at the top-left).

Dot **spacing** follows `-base`. Dot **sizes** on the page stay fixed in millimeters (they do not scale when you switch base units).

## Requirements

- Python 3
- [ReportLab](https://www.reportlab.com/) — installed automatically by the shell scripts via `requirements.txt`

## Scripts

| Script | Purpose |
|--------|---------|
| `./start.sh` | Generate one PDF, then open it (defaults: `-base cm`, `-paper letter`) |
| `./generate-all.sh` | Generate all 6 base × paper combinations into `output/` |
| `main.py` | Generator (same options as `start.sh`, long flags) |

First run creates a local `.venv` and installs dependencies.

### Single PDF

```bash
./start.sh
./start.sh -base inches -paper a4
./start.sh -base quarter-inch -paper letter
```

Or without opening the file:

```bash
python main.py --base cm --paper letter
python main.py --base quarter-inch --paper a4
```

### All combinations

```bash
./generate-all.sh
```

## Options

| Flag | Values | Default |
|------|--------|---------|
| `-base` | `cm`, `inches`, `quarter-inch` | `cm` |
| `-paper` | `letter`, `a4` | `letter` |

### What each base means

| `-base` | One base unit (1× spacing) | Example: 4× spacing |
|---------|----------------------------|---------------------|
| `cm` | 1 centimeter | 4 cm |
| `inches` | 1 inch | 4 inches |
| `quarter-inch` | ¼ inch | 1 inch |

## Output

PDFs are written to **`output/`**:

```text
output/fractional-grid-{base}-{paper}.pdf
```

| `-base` (CLI) | `{base}` in filename |
|---------------|----------------------|
| `cm` | `cm` |
| `inches` | `inch` |
| `quarter-inch` | `quarter-inch` |

Full set from `./generate-all.sh`:

- `output/fractional-grid-cm-letter.pdf`
- `output/fractional-grid-cm-a4.pdf`
- `output/fractional-grid-inch-letter.pdf`
- `output/fractional-grid-inch-a4.pdf`
- `output/fractional-grid-quarter-inch-letter.pdf`
- `output/fractional-grid-quarter-inch-a4.pdf`

## Grid layers

All spacings are multiples of the chosen base unit:

| Layer | Spacing | Appearance |
|-------|---------|------------|
| 4× base | 4 | Largest gray dots (darkest) |
| 1× base | 1 | Standard gray dots; every 3rd 1× intersection is **green** |
| ½× base | 0.5 | Gray (same darkness as 1×) |
| ¼× base | 0.25 | Gray (same size as ½×; finest draw step) |
| ⅓× base | 1/3 | **Red** dots drawn on top of the gray grid |

The red ⅓× grid and the green “every third” 1× marks are independent visual cues.

## Angles from dot to dot

The layout is a **square** grid. Use **integer steps** on the **1× base** lattice: **run** = steps horizontally, **rise** = steps vertically (toward the top or bottom edge). Angle from horizontal:

\[
\theta = \arctan\left(\frac{\text{rise}}{\text{run}}\right)
\]

Angles do not change with `-base`; only the **physical distance** per step changes.

### Exact angles (integer rise / run)

| Run | Rise | Angle | Notes |
|-----|------|-------|--------|
| 1 | 1 | **45.00°** | Diagonal of a 1× cell |
| 1 | 2 | **63.43°** | |
| 2 | 1 | **26.57°** | Complement of 1∶2 |
| 1 | 3 | **71.57°** | Ties to every-3rd 1× marking |
| 3 | 1 | **18.43°** | |
| 3 | 4 | **53.13°** | 3–4–5 triangle; 3× vs 4× theme |
| 4 | 3 | **36.87°** | Complement of 3∶4 |
| 2 | 3 | **56.31°** | |
| 3 | 2 | **33.69°** | |
| 1 | 4 | **75.96°** | |
| 4 | 1 | **14.04°** | |

### Near 30° and 60°

\(\tan(30°) = 1/\sqrt{3}\) and \(\tan(60°) = \sqrt{3}\) are irrational, so **no** integer rise/run hits those angles exactly on a square grid.

Close approximations:

| Run | Rise | Angle | Target |
|-----|------|-------|--------|
| 7 | 4 | **29.05°** | ~30° |
| 3 | 5 | **30.96°** | ~30° |
| 12 | 7 | **59.04°** | ~60° |
| 26 | 15 | **60.07°** | ~60° |

### Using the paper

1. Start at a clear landmark (e.g. the upper-left **4×** dot).
2. Count **1×** steps along run and rise to another dot.
3. Use the table or \(\arctan(\text{rise}/\text{run})\) in degrees.

**½×** and **¼×** dots sit on the same lines as **1×** dots; they add more points along existing directions, not new angles.

## Project layout

```text
graph-paper/
├── main.py              # PDF generator
├── start.sh             # one PDF + open
├── generate-all.sh      # all variants → output/
├── requirements.txt
├── output/              # generated PDFs (created on first run)
└── README.md
```

Tuning colors, dot radii, and darkness lives in the constants at the top of `main.py`.
