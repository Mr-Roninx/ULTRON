# ULTRON Synthetic Payment Universe v1.2 Scale Guide

## 1. World Scale Profiles
- **`tiny`**: 100 customers, 1,000 payments (~2 MB, <50 MB RAM)
- **`dev`**: 5,000 customers, 50,000 payments (~80 MB, <150 MB RAM)
- **`standard`**: 25,000 customers, 250,000 payments (~400 MB, <250 MB RAM)
- **`large`**: 100,000 customers, 1,000,000 payments (~1.6 GB, <400 MB RAM)

### CLI Command to Generate Large World:
```bash
python -m synthetic_payment_universe.world_v12.cli.create --profile large --seed 12345 --partition evaluation
```
Streaming chunk size = 500 records; zero RAM exhaustion.
