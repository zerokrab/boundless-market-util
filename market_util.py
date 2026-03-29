#!/usr/bin/env python3
"""
Boundless Market Utilization Calculator

Computes the % of submitted PoVW cycles that were market order cycles for a given
prover/miner address pair over a specified epoch range.

Usage:
    python3 market_util.py --prover <PROVER_ADDRESS> --miner <MINER_ADDRESS> \
                           --start-epoch <N> --end-epoch <M>
"""

import argparse
import json
import subprocess
import sys

BASE_URL = "https://explorer.boundless.network/api"


def log(msg: str) -> None:
    print(f"[INFO] {msg}", file=sys.stderr)


def curl_get(url: str) -> dict:
    """Fetch a URL via curl and return parsed JSON."""
    log(f"Fetching: {url}")
    result = subprocess.run(
        ["curl", "-s", "--fail", "--max-time", "30", url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[ERROR] curl failed (exit {result.returncode}) for URL: {url}", file=sys.stderr)
        if result.stderr:
            print(f"[ERROR] {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON response from {url}: {e}", file=sys.stderr)
        print(f"[ERROR] Raw response: {result.stdout[:500]}", file=sys.stderr)
        sys.exit(1)


def fetch_prover_epochs(prover_address: str) -> dict[int, dict]:
    """Fetch per-epoch market order aggregates for a prover address."""
    url = f"{BASE_URL}/provers/{prover_address}/aggregates/epoch"
    data = curl_get(url)
    epochs = {}
    for entry in data:
        epoch = entry["epoch"]
        epochs[epoch] = entry
    log(f"Fetched {len(epochs)} prover epochs for {prover_address}")
    return epochs


def fetch_miner_epochs(miner_address: str) -> dict[int, dict]:
    """Fetch per-epoch PoVW mining aggregates for a miner address."""
    url = f"{BASE_URL}/miners/{miner_address}/aggregates/epoch"
    data = curl_get(url)
    epochs = {}
    for entry in data:
        epoch = entry["epoch"]
        epochs[epoch] = entry
    log(f"Fetched {len(epochs)} miner epochs for {miner_address}")
    return epochs


def compute_utilization(
    prover_epochs: dict[int, dict],
    miner_epochs: dict[int, dict],
    start_epoch: int,
    end_epoch: int,
) -> list[dict]:
    """
    For each epoch in [start_epoch, end_epoch], compute:
      market_util_pct = (market_cycles / povw_cycles) * 100

    Returns a list of per-epoch result dicts.
    """
    results = []
    for epoch in range(start_epoch, end_epoch + 1):
        prover_data = prover_epochs.get(epoch)
        miner_data = miner_epochs.get(epoch)

        market_cycles = prover_data["total_cycles"] if prover_data else None
        povw_cycles = miner_data["work_submitted"] if miner_data else None

        if market_cycles is not None and povw_cycles is not None and povw_cycles > 0:
            pct = (market_cycles / povw_cycles) * 100
        else:
            pct = None

        results.append(
            {
                "epoch": epoch,
                "market_cycles": market_cycles,
                "povw_cycles": povw_cycles,
                "market_util_pct": pct,
            }
        )
    return results


def format_cycles(n: int | None) -> str:
    """Format cycle counts with K/M/G suffixes for readability."""
    if n is None:
        return "N/A"
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}G"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.2f}K"
    return str(n)


def print_table(results: list[dict], prover_address: str, miner_address: str) -> None:
    """Print a formatted table to stdout."""
    col_epoch = 8
    col_market = 14
    col_povw = 14
    col_pct = 12

    header_epoch = "Epoch".ljust(col_epoch)
    header_market = "Market Cycles".rjust(col_market)
    header_povw = "PoVW Cycles".rjust(col_povw)
    header_pct = "Market Util %".rjust(col_pct)

    sep = "-" * (col_epoch + col_market + col_povw + col_pct + 9)

    print()
    print(f"  Boundless Market Utilization")
    print(f"  Prover : {prover_address}")
    print(f"  Miner  : {miner_address}")
    print()
    print(f"  {header_epoch}  {header_market}  {header_povw}  {header_pct}")
    print(f"  {sep}")

    valid_pcts = []
    for row in results:
        epoch_str = str(row["epoch"]).ljust(col_epoch)
        market_str = format_cycles(row["market_cycles"]).rjust(col_market)
        povw_str = format_cycles(row["povw_cycles"]).rjust(col_povw)
        pct = row["market_util_pct"]
        if pct is not None:
            pct_str = f"{pct:.2f}%".rjust(col_pct)
            valid_pcts.append(pct)
        else:
            note = ""
            if row["market_cycles"] is None and row["povw_cycles"] is None:
                note = "(no data)"
            elif row["povw_cycles"] is None:
                note = "(no PoVW data)"
            elif row["market_cycles"] is None:
                note = "(no market data)"
            elif row["povw_cycles"] == 0:
                note = "(0 PoVW cycles)"
            pct_str = note.rjust(col_pct)

        print(f"  {epoch_str}  {market_str}  {povw_str}  {pct_str}")

    print(f"  {sep}")

    if valid_pcts:
        avg = sum(valid_pcts) / len(valid_pcts)
        avg_str = f"{avg:.2f}%".rjust(col_pct)
        avg_label = f"Average ({len(valid_pcts)} epochs)".ljust(col_epoch + col_market + col_povw + 4)
        print(f"  {avg_label}{avg_str}")
    else:
        print(f"  No valid epochs found in range — cannot compute average.")

    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute Boundless market utilization % for a given prover/miner pair.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 market_util.py \\
    --prover 0xAbCd...1234 \\
    --miner  0xDeAd...5678 \\
    --start-epoch 10 \\
    --end-epoch   20
""",
    )
    parser.add_argument(
        "--prover",
        required=True,
        metavar="ADDRESS",
        help="Prover (marketplace) address",
    )
    parser.add_argument(
        "--miner",
        required=True,
        metavar="ADDRESS",
        help="Miner (PoVW log ID) address",
    )
    parser.add_argument(
        "--start-epoch",
        required=True,
        type=int,
        metavar="N",
        help="First epoch (inclusive)",
    )
    parser.add_argument(
        "--end-epoch",
        required=True,
        type=int,
        metavar="N",
        help="Last epoch (inclusive)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.start_epoch > args.end_epoch:
        print("[ERROR] --start-epoch must be <= --end-epoch", file=sys.stderr)
        sys.exit(1)

    log(f"Prover address : {args.prover}")
    log(f"Miner address  : {args.miner}")
    log(f"Epoch range    : {args.start_epoch} – {args.end_epoch}")

    prover_epochs = fetch_prover_epochs(args.prover)
    miner_epochs = fetch_miner_epochs(args.miner)

    results = compute_utilization(
        prover_epochs, miner_epochs, args.start_epoch, args.end_epoch
    )

    print_table(results, args.prover, args.miner)


if __name__ == "__main__":
    main()
