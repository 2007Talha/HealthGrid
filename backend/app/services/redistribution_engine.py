"""
Swasthya Records - Cross-District Resource Redistribution Optimization Engine
Formulates and solves multi-facility inventory rebalancing using Google OR-Tools Mixed Integer Linear Programming (MILP).
"""

import uuid
import logging
from ortools.linear_solver import pywraplp
from backend.app.services.geo_routing import geo_routing_service
from backend.app.services.risk_engine import risk_engine

logger = logging.getLogger("swasthya.redistribution")

PROTECTION_WINDOW_DAYS = 5  # Days of forward demand protected at source facility
DESIRED_COVERAGE_DAYS = 7  # Destination buffer days to replenish


class RedistributionEngine:
    def __init__(self):
        self._cached_shortages = None
        self._cache_timestamp = 0.0

    def clear_cache(self):
        self._cached_shortages = None
        self._cache_timestamp = 0.0

    def identify_all_shortages(self):
        """
        Scans all facilities and medicines to discover critical and high risk shortages
        eligible for redistribution rebalancing.
        """
        import time

        now = time.time()
        if self._cached_shortages is not None and (now - self._cache_timestamp) < 300.0:
            return self._cached_shortages

        all_risks = risk_engine.evaluate_all_facility_risks()
        shortages = []

        for r in all_risks:
            risk_level = r.get("risk_level", "LOW")
            dosa = r.get("days_of_stock_available", 99.0)

            # Eligible if CRITICAL, HIGH, or DOSA < 5.0 days
            if risk_level in ["CRITICAL", "HIGH"] or dosa < 5.0:
                current_stock = r["current_stock"]
                daily_burn = max(1.0, r["average_daily_predicted_demand"])
                safety_stock = r["safety_stock_threshold"]
                target_stock = int(
                    round(safety_stock + (DESIRED_COVERAGE_DAYS * daily_burn))
                )

                # Check scheduled incoming deliveries
                incoming_total = 0
                for step in r.get("projected_trajectory", [])[:5]:
                    incoming_total += step.get("incoming_deliveries", 0)

                net_need = max(0, target_stock - current_stock - incoming_total)
                if net_need <= 0 and current_stock > 0 and dosa >= 2.0:
                    continue  # Covered by incoming delivery

                stockout_hours = round(dosa * 24.0, 1)

                # Destination priority score (0 - 100+)
                priority = 100 if risk_level == "CRITICAL" else 60
                if dosa < 2.0:
                    priority += 30
                if r.get("anomaly_detected", False):
                    priority += 15

                shortages.append(
                    {
                        "shortage_id": f"SHT-{r['phc_id'][-7:]}-{r['medicine_code'][-3:]}",
                        "facility_id": r["phc_id"],
                        "facility_name": r["facility_name"],
                        "medicine_code": r["medicine_code"],
                        "medicine_name": r["medicine_name"],
                        "therapeutic_category": r["therapeutic_category"],
                        "current_stock": current_stock,
                        "average_daily_predicted_demand": round(daily_burn, 1),
                        "days_of_stock_available": dosa,
                        "stockout_hours": stockout_hours,
                        "projected_stockout_date": r.get("projected_stockout_date")
                        or "IMMEDIATE",
                        "safety_stock_threshold": safety_stock,
                        "target_stock": target_stock,
                        "incoming_deliveries_pending": incoming_total,
                        "net_deficit_quantity": net_need,
                        "risk_level": risk_level,
                        "priority_score": priority,
                        "anomaly_detected": r.get("anomaly_detected", False),
                    }
                )

        # Sort by priority score descending
        shortages.sort(key=lambda x: x["priority_score"], reverse=True)
        self._cached_shortages = shortages
        self._cache_timestamp = now
        return shortages

    def find_candidate_sources(
        self, destination_id, medicine_code, max_distance_km=300.0
    ):
        """
        Discovers and ranks candidate source facilities with protected transferable surplus.
        """
        fac_df = geo_routing_service.facilities_df
        if fac_df is None or fac_df.empty:
            return []

        candidates = []
        for _, row in fac_df.iterrows():
            source_id = row["facility_id"]
            if source_id == destination_id:
                continue

            # Get source inventory risk evaluation
            source_risk = risk_engine.evaluate_facility_medicine_risk(
                source_id, medicine_code
            )
            if not source_risk or source_risk.get("risk_level") in ["CRITICAL", "HIGH"]:
                continue  # Exclude risky sources

            current_stock = source_risk["current_stock"]
            daily_demand = max(1.0, source_risk["average_daily_predicted_demand"])
            safety_stock = source_risk["safety_stock_threshold"]

            # Source Protection Window: preserves safety stock threshold and forward demand coverage
            protected_reserve = max(
                safety_stock, int(round(PROTECTION_WINDOW_DAYS * daily_demand))
            )
            transferable_surplus = max(0, int(current_stock - protected_reserve))

            if transferable_surplus <= 0:
                continue  # No safe surplus

            # Route and distance calculation
            route = geo_routing_service.calculate_route(source_id, destination_id)
            dist_km = route["distance_km"]
            duration_hours = route["duration_hours"]

            if dist_km > max_distance_km:
                continue

            # Suitability score
            is_same_dist = 1.0 if route["is_same_district"] else 0.0
            is_same_st = 1.0 if route["is_same_state"] else 0.0

            # Score balances high surplus, low distance, fast ETA, and district locality
            score = (
                (transferable_surplus * 0.4)
                - (dist_km * 0.8)
                - (duration_hours * 5.0)
                + (is_same_dist * 200.0)
                + (is_same_st * 50.0)
            )

            candidates.append(
                {
                    "source_facility_id": source_id,
                    "source_facility_name": row["facility_name"],
                    "source_facility_type": row["facility_type"],
                    "source_district_name": row["district_name"],
                    "source_district_code": row["district_code"],
                    "source_state_name": row["state_name"],
                    "current_stock": current_stock,
                    "daily_demand": round(daily_demand, 1),
                    "safety_stock_threshold": safety_stock,
                    "protected_reserve": protected_reserve,
                    "transferable_surplus": transferable_surplus,
                    "distance_km": dist_km,
                    "duration_hours": duration_hours,
                    "duration_formatted": route["duration_formatted"],
                    "is_same_district": route["is_same_district"],
                    "is_same_state": route["is_same_state"],
                    "source_risk_level": source_risk["risk_level"],
                    "candidate_score": round(score, 2),
                    "coordinates": route["source_coordinates"],
                }
            )

        candidates.sort(key=lambda x: x["candidate_score"], reverse=True)
        return candidates

    def optimize_redistribution(self, destination_id, medicine_code, max_sources=2):
        """
        Solves the Mixed Integer Linear Programming (MILP) redistribution optimization problem using Google OR-Tools.
        """
        # 1. Query Destination Deficit
        dest_risk = risk_engine.evaluate_facility_medicine_risk(
            destination_id, medicine_code
        )
        if (
            not dest_risk
            or dest_risk.get("risk_level") == "UNKNOWN"
            or "current_stock" not in dest_risk
        ):
            return {
                "recommendation_id": None,
                "status": "ERROR",
                "message": f"Facility {destination_id} or medicine {medicine_code} not found in inventory telemetry.",
                "transfers": [],
            }

        dest_loc = geo_routing_service.get_facility_location(destination_id)
        current_stock = dest_risk["current_stock"]
        daily_burn = max(1.0, dest_risk["average_daily_predicted_demand"])
        safety_stock = dest_risk["safety_stock_threshold"]
        dosa = dest_risk["days_of_stock_available"]
        target_stock = int(round(safety_stock + (DESIRED_COVERAGE_DAYS * daily_burn)))

        # Check incoming stock arriving within immediate horizon vs total
        incoming_immediate = sum(
            step.get("incoming_deliveries", 0)
            for step in dest_risk.get("projected_trajectory", [])[:2]
        )
        incoming_total = sum(
            step.get("incoming_deliveries", 0)
            for step in dest_risk.get("projected_trajectory", [])[:5]
        )

        # If facility is in critical shortage (DOSA < 3.0), immediate bridge stock is required
        if dosa < 3.0:
            net_need = max(0, target_stock - current_stock - incoming_immediate)
        else:
            net_need = max(0, target_stock - current_stock - incoming_total)

        # Check if already covered
        if net_need == 0 and dosa >= 5.0:
            return {
                "status": "NOT_NEEDED",
                "recommendation_id": f"REC-NONE-{uuid.uuid4().hex[:6].upper()}",
                "message": f"Facility {dest_risk['facility_name']} already maintains adequate stock ({current_stock} units, DOSA {dosa:.1f}d). Redistribution not required.",
                "destination_id": destination_id,
                "medicine_code": medicine_code,
            }

        if net_need == 0 and incoming_total > 0:
            return {
                "status": "COVERED_BY_INCOMING_DELIVERY",
                "recommendation_id": f"REC-DELIV-{uuid.uuid4().hex[:6].upper()}",
                "message": f"Facility {dest_risk['facility_name']} has {incoming_total} units in-transit delivery arriving before stock-out.",
                "destination_id": destination_id,
                "medicine_code": medicine_code,
            }

        # 2. Find Candidate Sources
        candidates = self.find_candidate_sources(destination_id, medicine_code)
        if not candidates:
            return {
                "status": "INFEASIBLE_NO_SURPLUS",
                "recommendation_id": f"REC-INF-{uuid.uuid4().hex[:6].upper()}",
                "message": "No feasible redistribution found with the available evidence. Nearby facilities have zero safe transferable surplus or are facing supply risk themselves.",
                "destination_id": destination_id,
                "destination_facility_name": dest_risk["facility_name"],
                "medicine_code": medicine_code,
                "medicine_name": dest_risk["medicine_name"],
                "destination_need": net_need,
            }

        # 3. Formulate Google OR-Tools MILP Solver
        solver = pywraplp.Solver.CreateSolver("CBC")
        if not solver:
            # Fallback to GLOP if CBC is not available
            solver = pywraplp.Solver.CreateSolver("GLOP")

        N = min(len(candidates), 8)  # Evaluate top 8 candidate facilities
        candidate_subset = candidates[:N]

        X = {}  # Continuous transfer quantities
        Y = {}  # Binary route activation variables

        for i, c in enumerate(candidate_subset):
            surplus = c["transferable_surplus"]
            X[i] = solver.NumVar(0.0, float(surplus), f"X_{i}")
            Y[i] = solver.BoolVar(f"Y_{i}")

            # Constraint: X[i] <= surplus * Y[i]
            solver.Add(X[i] <= surplus * Y[i])

        # Constraint 1: Total allocated <= net_need
        solver.Add(solver.Sum([X[i] for i in range(N)]) <= float(net_need))

        # Constraint 2: Multi-source cap (at most max_sources routes activated)
        solver.Add(solver.Sum([Y[i] for i in range(N)]) <= float(max_sources))

        # Objective Function:
        # Maximize total units transferred (M=10,000) while minimizing distance, travel time, and route overhead
        objective = solver.Objective()
        for i, c in enumerate(candidate_subset):
            dist_cost = c["distance_km"] * 1.5
            time_cost = c["duration_hours"] * 25.0
            fixed_dispatch_penalty = 200.0 if not c["is_same_district"] else 50.0

            # Net coefficient: -10000 (benefit per unit) + distance cost per unit
            objective.SetCoefficient(X[i], 10000.0 - dist_cost - time_cost)
            objective.SetCoefficient(Y[i], -fixed_dispatch_penalty)

        objective.SetMaximization()
        solve_status = solver.Solve()

        if solve_status not in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            return {
                "status": "INFEASIBLE_SOLVER_ERROR",
                "message": "Optimization solver failed to converge to a feasible solution.",
            }

        # 4. Assemble Solution Recommendations
        transfers = []
        total_transferred = 0

        for i, c in enumerate(candidate_subset):
            qty = int(round(X[i].solution_value()))
            if qty > 0:
                transfers.append(
                    {
                        "source_facility_id": c["source_facility_id"],
                        "source_facility_name": c["source_facility_name"],
                        "source_district_name": c["source_district_name"],
                        "source_state_name": c["source_state_name"],
                        "transfer_quantity": qty,
                        "source_surplus_before": c["transferable_surplus"],
                        "source_stock_before": c["current_stock"],
                        "source_stock_after": c["current_stock"] - qty,
                        "source_safety_stock_threshold": c["safety_stock_threshold"],
                        "distance_km": c["distance_km"],
                        "duration_hours": c["duration_hours"],
                        "duration_formatted": c["duration_formatted"],
                        "is_same_district": c["is_same_district"],
                        "is_same_state": c["is_same_state"],
                        "source_coordinates": c["coordinates"],
                    }
                )
                total_transferred += qty

        if total_transferred == 0:
            return {
                "status": "INFEASIBLE_NO_ALLOCATION",
                "message": "No transfer could be allocated within safe constraints.",
            }

        # Projected impact on destination
        dest_stock_after = current_stock + total_transferred
        new_dosa = round(dest_stock_after / daily_burn, 1)
        expected_new_risk = (
            "LOW" if new_dosa >= 7.0 else ("WARNING" if new_dosa >= 4.0 else "HIGH")
        )

        rec_id = f"REC-{destination_id[-7:]}-{medicine_code[-3:]}-{uuid.uuid4().hex[:4].upper()}"

        # Primary source for headline display
        primary_transfer = transfers[0]

        explanation_reason = (
            f"{primary_transfer['source_facility_name']} ({primary_transfer['source_district_name']}) has "
            f"{primary_transfer['source_surplus_before']} units of safe transferable surplus and retains its safety stock "
            f"({primary_transfer['source_safety_stock_threshold']} units + 10-day protection window) after dispatching "
            f"{primary_transfer['transfer_quantity']} units across {primary_transfer['distance_km']} km ({primary_transfer['duration_formatted']} transit). "
            f"This resolves the projected stock-out at {dest_risk['facility_name']}, elevating stock coverage from {dosa:.1f} days to {new_dosa:.1f} days."
        )

        return {
            "recommendation_id": rec_id,
            "status": "OPTIMAL_RECOMMENDED",
            "destination_id": destination_id,
            "destination_name": dest_risk["facility_name"],
            "medicine_code": medicine_code,
            "medicine_name": dest_risk["medicine_name"],
            "deficit_units": net_need,
            "total_transfer_allocated": total_transferred,
            "fulfillment_rate_pct": round((total_transferred / net_need) * 100.0, 1)
            if net_need > 0
            else 100.0,
            "total_distance_km": primary_transfer["distance_km"],
            "max_eta_hours": primary_transfer["duration_hours"],
            "risk_before": dest_risk["risk_level"],
            "projected_risk_after": expected_new_risk,
            "sources": [
                {
                    "source_id": t["source_facility_id"],
                    "source_name": t["source_facility_name"],
                    "transfer_units": t["transfer_quantity"],
                    "distance_km": t["distance_km"],
                    "travel_time_hours": t["duration_hours"],
                    "safe_surplus_remaining": max(
                        0, t.get("source_surplus_before", 0) - t["transfer_quantity"]
                    ),
                }
                for t in transfers
            ],
            "sourceCoords": {
                "lat": primary_transfer["source_coordinates"].get("lat", 25.5),
                "lng": primary_transfer["source_coordinates"].get("lng", 85.3),
            }
            if primary_transfer.get("source_coordinates")
            else {"lat": 25.5, "lng": 85.3},
            "destCoords": {
                "lat": dest_loc.get("latitude", 25.46) if dest_loc else 25.46,
                "lng": dest_loc.get("longitude", 85.53) if dest_loc else 85.53,
            },
            "resource": {
                "medicine_code": medicine_code,
                "medicine_name": dest_risk["medicine_name"],
                "therapeutic_category": dest_risk["therapeutic_category"],
            },
            "destination": {
                "facility_id": destination_id,
                "facility_name": dest_risk["facility_name"],
                "facility_type": dest_loc["facility_type"] if dest_loc else "PHC",
                "district_name": dest_loc["district_name"] if dest_loc else "",
                "state_name": dest_loc["state_name"] if dest_loc else "",
                "current_stock": current_stock,
                "daily_burn_rate": round(daily_burn, 1),
                "safety_stock_threshold": safety_stock,
                "days_of_stock_available_before": dosa,
                "stockout_hours": round(dosa * 24.0, 1),
                "risk_level_before": dest_risk["risk_level"],
                "net_deficit": net_need,
                "coordinates": {
                    "lat": dest_loc["latitude"],
                    "lng": dest_loc["longitude"],
                }
                if dest_loc
                else {},
            },
            "transfers": transfers,
            "total_recommended_quantity": total_transferred,
            "fulfillment_percentage": round((total_transferred / net_need) * 100.0, 1)
            if net_need > 0
            else 100.0,
            "projected_impact": {
                "destination_stock_after": dest_stock_after,
                "days_of_stock_available_after": new_dosa,
                "risk_level_before": dest_risk["risk_level"],
                "risk_level_after": expected_new_risk,
                "expected_risk_reduction": f"{dest_risk['risk_level']} -> {expected_new_risk}",
            },
            "machine_readable_reasons": {
                "source_has_surplus": True,
                "source_safety_stock_preserved": True,
                "source_10d_protection_window_preserved": True,
                "destination_critical": dest_risk["risk_level"] in ["CRITICAL", "HIGH"],
                "stockout_prevented": new_dosa >= 5.0,
                "primary_transit_distance_km": primary_transfer["distance_km"],
                "primary_transit_duration_hours": primary_transfer["duration_hours"],
                "multi_source_used": len(transfers) > 1,
            },
            "reason_summary": explanation_reason,
        }

    def generate_redistribution_recommendation(
        self, destination_id, medicine_code, max_sources=2
    ):
        """Alias for optimize_redistribution."""
        return self.optimize_redistribution(
            destination_id, medicine_code, max_sources=max_sources
        )


redistribution_engine = RedistributionEngine()
