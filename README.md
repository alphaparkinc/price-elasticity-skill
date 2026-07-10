# genpark-price-elasticity-skill

> **GenPark AI Agent Skill** -- Calculate price elasticity of demand and find revenue-maximizing price points.

## Features

- Log-linear regression to fit price-demand curves
- Elasticity classification: Elastic / Inelastic / Unit Elastic
- Revenue and margin optimization across custom price ranges
- Single price-change impact simulator
- Actionable pricing recommendations

## Quick Start

```python
from client import PriceElasticityClient

client = PriceElasticityClient()
result = client.analyze(
    price_demand_data=[{"price": 29.99, "units_sold": 280}, {"price": 39.99, "units_sold": 140}],
    current_price=29.99,
    cost_per_unit=8.00,
)
print(f"Elasticity: {result['elasticity']} ({result['elasticity_type']})")
print(f"Optimal Price: ${result['optimal_price']}")
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
