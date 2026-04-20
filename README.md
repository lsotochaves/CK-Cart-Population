# CK Cart Population

Automates bulk-adding cards to your [Card Kingdom](https://www.cardkingdom.com/) cart from a simple text file.

Instead of searching and clicking "Add to Cart" one by one, define your cards in a `.txt` file and let the script handle login, ID resolution, and cart population — all in a single browser session.

## How It Works

1. **Login** — Opens a browser, prompts for credentials, handles retries and CAPTCHAs
2. **Parse** — Reads your card list from `Cards_to_add/*.txt`
3. **Resolve IDs** — Batch-fetches product IDs from your local [Cards-Server](https://github.com/<your-username>/Cards-Server) instance (no per-card page scraping)
4. **Add** — Adds each card to the cart via Card Kingdom's API

## Prerequisites

- Python 3.12+ and [uv](https://github.com/astral-sh/uv)
- A running [Cards-Server](https://github.com/lsotochaves/Cards-Server) instance with a synced card catalog

## Setup

```bash
git clone https://github.com/lsotochaves/CK-Cart-Population.git
cd CK-Cart-Population
uv sync
```

### Configuration

Create a `.env` file in the project root pointing to your Cards-Server instance:

```env
API_SERVER=http://localhost:8000
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

### Testing ID resolution

You can verify that your Cards-Server is returning product IDs correctly without logging in or opening a browser:

```bash
uv run python test_api_id.py
```

This parses your card list, calls the server, and prints the resolved IDs.

## Known Limitations

- **No quantity updates for duplicates.** If a card is already in your cart from a previous run, the script does not detect or update it. You'll need to adjust quantities manually in the browser.

- **No stock availability check.** If you request 4 copies but only 2 are in stock, the script has no way of knowing. It may silently add fewer than expected.

- **Single file only.** Only the first `.txt` file found in `Cards_to_add/` is read. Multiple files are not merged.

- **Requires Cards-Server.** The server must be running and synced before you run the cart tool. If the server is down or the catalog is stale, ID resolution will fail.