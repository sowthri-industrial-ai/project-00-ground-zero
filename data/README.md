# Brief E · Data fixtures

## nist-ai-rmf.pdf · primary corpus
Public-domain · ~80 pages. Fetch:
```
curl -L -o data/nist-ai-rmf.pdf "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf"
```

## sample-form.pdf · Document Intelligence demo
Generate once:
```
uv run python scripts/generate_sample_form.py
```

## saudi-vision-2030-bilingual.pdf · ALLaM Arabic path
Public bilingual doc. Fetch:
```
curl -L -o data/saudi-vision-2030-bilingual.pdf "https://www.vision2030.gov.sa/media/rc0b5oy1/saudi_vision203.pdf"
```

## fine-tune-corpus.jsonl · scaffold
Shipped in repo below · ~10 synthetic instruction pairs · NO real training.
