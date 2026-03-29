# boundless-market-util

A tool to compute the percentage of submitted PoVW cycles that were market order cycles — i.e. **market utilization** — for a Boundless prover.

## Requirements

- Python 3.10+
- `curl` 

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

## Data Sources

- **Market cycles**: `GET /api/provers/{PROVER_ADDRESS}/aggregates/epoch` → `total_cycles`
- **PoVW cycles**: `GET /api/miners/{MINER_ADDRESS}` → `work_submitted`

## Notes

- Epochs with missing data on either side are shown as `N/A` and excluded from the average.
- `total_cycles` is used for market data, not `total_program_cycles`