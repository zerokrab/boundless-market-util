# boundless-market-util

A tiny CLI tool that computes the percentage of submitted PoVW cycles that were market order cycles — i.e. **market utilization** — for a Boundless prover.

## Background

Boundless provers submit proofs of computed cycles for rewards (PoVW). They can also participate in the Boundless marketplace, delivering proofs for customers — and those cycles count towards PoVW too. Each epoch (~48 hrs) cycles are submitted and rewards paid out.

Typically a prover uses one address for the marketplace and a separate address (log ID / miner address) for PoVW. This tool joins the two data sources and reports the utilization ratio.

## Usage

```bash
python3 market_util.py \
  --prover <PROVER_ADDRESS> \
  --miner  <MINER_ADDRESS>  \
  --start-epoch <N>         \
  --end-epoch   <M>
```

### Arguments

| Flag | Required | Description |
|------|----------|-------------|
| `--prover` | ✅ | Prover (marketplace) address |
| `--miner` | ✅ | Miner (PoVW log ID) address |
| `--start-epoch` | ✅ | First epoch to include (inclusive) |
| `--end-epoch` | ✅ | Last epoch to include (inclusive) |

### Example output

```
  Boundless Market Utilization
  Prover : 0xAbCd...1234
  Miner  : 0xDeAd...5678

  Epoch       Market Cycles    PoVW Cycles  Market Util %
  -----------------------------------------------------------
  10               12.34M           48.20M         25.60%
  11                8.91M           42.10M         21.16%
  12               15.02M           51.30M         29.28%
  ...
  -----------------------------------------------------------
  Average (3 epochs)                               25.35%
```

## Requirements

- Python 3.10+
- `curl` (standard on macOS/Linux)
- No external Python dependencies

## Data Sources

- **Market cycles**: `GET /api/provers/{PROVER_ADDRESS}/aggregates/epoch` → `total_cycles`
- **PoVW cycles**: `GET /api/miners/{MINER_ADDRESS}/aggregates/epoch` → `work_submitted`

Both endpoints are on the public [Boundless Explorer API](https://explorer.boundless.network/api). No authentication required.

## Notes

- Epochs with missing data on either side are shown as `N/A` and excluded from the average.
- Cycle counts are displayed with `K`/`M`/`G` suffixes for readability.
- Logs (showing what's being fetched) are written to stderr; the table is written to stdout. This makes it easy to pipe just the table: `python3 market_util.py ... 2>/dev/null`.
