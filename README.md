# CK Cart Population

Automates bulk-adding cards to your [Card Kingdom](https://www.cardkingdom.com/) cart from a simple text file.

Instead of searching and clicking "Add to Cart" one by one, define your cards in a `.txt` file and let the script handle login, product ID extraction, and cart population — all in a single browser session.

## How It Works

1. **Login** — Opens a browser, prompts for credentials, handles retries and CAPTCHAs
2. **Parse** — Reads your card list from `Cards_to_add/*.txt`
3. **Extract** — Visits each card's URL to grab its internal product ID
4. **Add** — Adds each card to the cart

## Setup

**Requirements:** Python 3.10+ and [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/<your-username>/CK-Cart-Population.git
cd CK-Cart-Population
uv sync
```

## Usage

### 1. Add your cards

Create a `.txt` file inside the `Cards_to_add/` directory:

```
# Cards_to_add/order.txt
# Format: url, quality, quantity
# Quality: NM (Near Mint), EX (Excellent), VG (Very Good), G (Good)

https://www.cardkingdom.com/mtg/ice-age/brainstorm, NM, 4
https://www.cardkingdom.com/mtg/modern-horizons-3/flare-of-denial, EX, 2
https://www.cardkingdom.com/mtg/foundations/llanowar-elves, NM, 1
```

Lines starting with `#` are treated as comments and ignored.

### 2. Run

```bash
uv run python main.py
```

You'll be prompted for your Card Kingdom email and password (password input is hidden). If a CAPTCHA appears, solve it in the browser and press Enter in the terminal to continue.

After all cards are processed, the browser stays open so you can review your cart. Press Enter in the terminal to close it.

## Project Structure

```
├── main.py              # Entry point & orchestrator
├── login.py             # LoginManager — authentication
├── cart.py              # CartManager — parsing, extraction, cart operations
├── Cards_to_add/        # Drop your .txt card lists here
│   └── order.txt
├── pyproject.toml       # Dependencies
├── uv.lock              # Lockfile
└── .gitignore
```

## Known Limitations

- **No quantity updates for duplicates.** If a card is already in your cart from a previous run, the script does not detect or update it. You'll need to adjust quantities manually in the browser.

- **No stock availability check.** If you request 4 copies but only 2 are in stock, the script has no way of knowing. It may silently add fewer than expected.

- **Single file only.** Only the first `.txt` file found in `Cards_to_add/` is read. Multiple files are not merged.