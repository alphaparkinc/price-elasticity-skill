"""
example_usage.py -- Demonstrates the PriceElasticityClient SDK.
"""
from client import PriceElasticityClient

def main():
    client = PriceElasticityClient()

    # Historical price-demand data
    data = [
        {"price": 19.99, "units_sold": 520},
        {"price": 24.99, "units_sold": 380},
        {"price": 29.99, "units_sold": 280},
        {"price": 34.99, "units_sold": 195},
        {"price": 39.99, "units_sold": 140},
        {"price": 44.99, "units_sold": 95},
    ]

    print("[1] Price Elasticity Analysis")
    result = client.analyze(
        price_demand_data=data,
        current_price=29.99,
        cost_per_unit=8.00,
        price_range={"min": 18.0, "max": 49.99},
    )
    print(f"Elasticity Coefficient: {result['elasticity']}")
    print(f"Type: {result['elasticity_type']}")
    print(f"Current Price: ${result['current_price']} | Est. Demand: {result['current_estimated_demand']} units")
    print(f"Optimal Price (Revenue): ${result['optimal_price']}")
    print(f"Optimal Price (Margin):  ${result['optimal_margin_price']}")
    print(f"Revenue Uplift if moved to optimal: {result['revenue_uplift_pct']}%")
    print("\nRecommendations:")
    for r in result["recommendations"]:
        print(f"  - {r}")
    print("\nRevenue Curve (sample):")
    for pt in result["revenue_curve"][::10]:
        print(f"  Price: ${pt['price']:>6.2f} | Units: {pt['estimated_units']:>6.1f} | Revenue: ${pt['revenue']:>8.2f} | Margin: ${pt['margin']:>8.2f}")

    print("\n[2] Quick Price Change Simulation")
    sim = client.simulate_price_change(
        current_price=29.99, new_price=24.99,
        current_units=280, elasticity=result["elasticity"]
    )
    print(f"Price Change: ${sim['current_price']} -> ${sim['new_price']} ({sim['price_change_pct']}%)")
    print(f"Demand Change: {sim['current_demand']} -> {sim['new_demand']} units ({sim['demand_change_pct']}%)")
    print(f"Revenue Change: ${sim['current_revenue']} -> ${sim['new_revenue']} ({sim['revenue_change_pct']:+.1f}%)")

if __name__ == "__main__":
    main()
