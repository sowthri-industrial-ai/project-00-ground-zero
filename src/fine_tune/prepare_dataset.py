"""Dataset prep · tokenisation · train/val split · no real training."""
from __future__ import annotations
import json
import random
from pathlib import Path


def prepare(input_path: str = "data/fine-tune-corpus.jsonl", output_dir: str = ".ft_prepared") -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    records = [json.loads(l) for l in Path(input_path).read_text().splitlines() if l.strip()]
    random.Random(42).shuffle(records)
    split = int(len(records) * 0.9)
    train, val = records[:split], records[split:]
    (out / "train.jsonl").write_text("\n".join(json.dumps(r) for r in train))
    (out / "val.jsonl").write_text("\n".join(json.dumps(r) for r in val))
    return {"train": len(train), "val": len(val), "output_dir": str(out)}


if __name__ == "__main__":
    print(prepare())
