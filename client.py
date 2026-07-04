"""
price-elasticity-skill: Client SDK
Calculate price elasticity of demand and find optimal price points.
"""
from __future__ import annotations
import math
from typing import Optional


class PriceElasticityClient:
    """
    SDK for price elasticity analysis and optimal pricing.

    Uses log-linear regression to estimate the price-demand relationship,
    then simulates revenue across a price range to find optimal points.
    """

    def analyze(
        self,
        price_demand_data: list[dict],
        current_price: float,
        cost_per_unit: float = 0.0,
        price_range: Optional[dict] = None,
        steps: int = 50,
    ) -> dict:
        """
        Full price elasticity analysis.

        Args:
            price_demand_data: List of {price, units_sold} dicts.
            current_price:     Current selling price.
            cost_per_unit:     Unit cost for margin calculation.
            price_range:       Dict with {min, max} for simulation.
            steps:             Number of price points to simulate.

        Returns:
            dict with elasticity, optimal_price, revenue_curve, recommendations
        """
        if len(price_demand_data) < 2:
            raise ValueError("Need at least 2 data points to calculate elasticity.")

        # Clean data
        data = [(float(d["price"]), float(d["units_sold"])) for d in price_demand_data
                if d.get("price", 0) > 0 and d.get("units_sold", 0) > 0]
        if len(data) < 2:
            raise ValueError("Insufficient valid data points.")

        # Log-linear regression: ln(Q) = a + b * ln(P)
        # b is the price elasticity coefficient
        elasticity, intercept = self._log_regression(data)

        # Classify elasticity
        abs_e = abs(elasticity)
        if abs_e > 1:
            elas_type = "Elastic (price-sensitive)"
        elif abs_e < 1:
            elas_type = "Inelastic (price-insensitive)"
        else:
            elas_type = "Unit Elastic"

        # Current demand estimate
        avg_price = sum(p for p, _ in data) / len(data)
        avg_qty = sum(q for _, q in data) / len(data)
        current_demand = avg_qty * ((current_price / avg_price) ** elasticity)

        # Price range simulation
        p_range = price_range or {}
        p_min = max(float(p_range.get("min", cost_per_unit * 1.1 if cost_per_unit else current_price * 0.5)), 0.01)
        p_max = float(p_range.get("max", current_price * 2.0))

        revenue_curve = []
        margin_curve = []
        step_size = (p_max - p_min) / steps
        for i in range(steps + 1):
            p = round(p_min + i * step_size, 2)
            q = max(0, avg_qty * ((p / avg_price) ** elasticity))
            rev = round(p * q, 2)
            margin = round((p - cost_per_unit) * q, 2) if cost_per_unit > 0 else rev
            revenue_curve.append({"price": p, "estimated_units": round(q, 1), "revenue": rev, "margin": margin})
            margin_curve.append((p, margin))

        # Optimal prices
        optimal_rev = max(revenue_curve, key=lambda x: x["revenue"])
        optimal_price = optimal_rev["price"]

        optimal_margin_price = current_price
        if cost_per_unit > 0:
            best_margin = max(margin_curve, key=lambda x: x[1])
            optimal_margin_price = best_margin[0]

        # Revenue impact of moving to optimal
        current_rev = current_price * current_demand
        optimal_rev_val = optimal_rev["revenue"]
        revenue_uplift = round((optimal_rev_val - current_rev) / max(current_rev, 1) * 100, 1)

        recommendations = self._generate_recommendations(
            elasticity, current_price, optimal_price, revenue_uplift, cost_per_unit
        )

        return {
            "elasticity": round(elasticity, 3),
            "elasticity_type": elas_type,
            "current_price": current_price,
            "current_estimated_demand": round(current_demand, 1),
            "optimal_price": optimal_price,
            "optimal_margin_price": optimal_margin_price,
            "revenue_uplift_pct": revenue_uplift,
            "revenue_curve": revenue_curve,
            "data_points_used": len(data),
            "recommendations": recommendations,
        }

    def simulate_price_change(
        self,
        current_price: float,
        new_price: float,
        current_units: float,
        elasticity: float,
    ) -> dict:
        """
        Quick simulation of a single price change impact.

        Args:
            current_price:  Current price.
            new_price:      Proposed new price.
            current_units:  Current units sold per period.
            elasticity:     Known price elasticity coefficient.

        Returns:
            dict with new_demand, revenue_change, and recommendation.
        """
        pct_price_change = (new_price - current_price) / current_price
        pct_demand_change = elasticity * pct_price_change
        new_demand = current_units * (1 + pct_demand_change)
        current_revenue = current_price * current_units
        new_revenue = new_price * new_demand
        revenue_change = new_revenue - current_revenue
        return {
            "current_price": current_price,
            "new_price": new_price,
            "price_change_pct": round(pct_price_change * 100, 1),
            "current_demand": round(current_units, 1),
            "new_demand": round(new_demand, 1),
            "demand_change_pct": round(pct_demand_change * 100, 1),
            "current_revenue": round(current_revenue, 2),
            "new_revenue": round(new_revenue, 2),
            "revenue_change": round(revenue_change, 2),
            "revenue_change_pct": round(revenue_change / max(current_revenue, 1) * 100, 1),
        }

    @staticmethod
    def _log_regression(data: list[tuple]) -> tuple[float, float]:
        """Fit ln(Q) = a + b*ln(P) using OLS."""
        log_p = [math.log(p) for p, _ in data]
        log_q = [math.log(q) for _, q in data]
        n = len(data)
        mean_lp = sum(log_p) / n
        mean_lq = sum(log_q) / n
        num = sum((log_p[i] - mean_lp) * (log_q[i] - mean_lq) for i in range(n))
        den = sum((log_p[i] - mean_lp) ** 2 for i in range(n))
        b = num / den if den != 0 else -1.0
        a = mean_lq - b * mean_lp
        return b, a

    @staticmethod
    def _generate_recommendations(elasticity, current, optimal, uplift, cost) -> list[str]:
        recs = []
        if abs(elasticity) > 1:
            recs.append("Product is price-elastic: small price decreases can significantly boost volume.")
            if optimal < current:
                recs.append(f"Consider reducing price to ${optimal:.2f} for estimated {abs(uplift):.1f}% revenue uplift.")
        else:
            recs.append("Product is price-inelastic: price increases have limited impact on demand.")
            if optimal > current:
                recs.append(f"Consider increasing price to ${optimal:.2f} -- demand unlikely to drop significantly.")
        if cost > 0 and current < cost * 1.5:
            recs.append("Current margin is thin -- prioritize margin-maximizing price over volume.")
        if uplift > 5:
            recs.append(f"Optimal price offers {uplift:.1f}% revenue uplift -- worth testing via A/B experiment.")
        return recs
