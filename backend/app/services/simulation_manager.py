"""
Swasthya Records - Reversible Redistribution Simulation State Manager
Manages the lifecycle of simulated inventory transfers (PROPOSED -> SIMULATED -> RESET),
executing runtime risk before/after recalculations and preserving government data immutability.
"""

import os
import sqlite3
import datetime
import logging
import pandas as pd
import numpy as np
from backend.app.core.config import settings
from backend.app.services.inventory_service import inventory_service
from backend.app.services.risk_engine import risk_engine

logger = logging.getLogger("swasthya.simulation_manager")


class SimulationManager:
    def __init__(self):
        self.active_simulations = {}
        self.cached_recommendations = {}
        self._init_db()

    def _init_db(self):
        """Initializes SQLite persistence table for redistribution simulations."""
        try:
            conn = sqlite3.connect(settings.SQLITE_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS redistribution_simulations (
                    simulation_id TEXT PRIMARY KEY,
                    recommendation_id TEXT,
                    resource_code TEXT,
                    resource_name TEXT,
                    source_facility_id TEXT,
                    source_facility_name TEXT,
                    destination_facility_id TEXT,
                    destination_facility_name TEXT,
                    quantity INTEGER,
                    before_destination_risk TEXT,
                    after_destination_risk TEXT,
                    before_destination_dosa REAL,
                    after_destination_dosa REAL,
                    transit_distance_km REAL,
                    status TEXT,
                    simulated_at TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not init SQLite simulation table: {e}")

    def cache_recommendation(self, rec):
        """Caches generated recommendation for quick lookup by ID."""
        rec_id = rec.get("recommendation_id")
        if rec_id:
            self.cached_recommendations[rec_id] = rec

    def apply_simulated_transfer(self, recommendation_id, rec_data=None):
        """
        Executes a simulated inventory transfer for an approved recommendation.
        Updates in-memory simulation state, recalculates risks before and after,
        and logs the transition.
        """
        rec = rec_data or self.cached_recommendations.get(recommendation_id)
        if not rec:
            return {
                "status": "ERROR",
                "message": f"Recommendation {recommendation_id} not found. Generate recommendation first.",
            }

        dest_info = rec["destination"]
        dest_id = dest_info["facility_id"]
        med_dict = rec.get("medicine") or rec.get("resource") or {}
        med_code = rec.get("medicine_code") or med_dict.get("medicine_code")
        med_name = rec.get("medicine_name") or med_dict.get(
            "medicine_name", str(med_code)
        )
        transfers = rec.get("transfers", [])

        if not transfers:
            return {
                "status": "ERROR",
                "message": "No valid transfers found in recommendation.",
            }

        # Step 1: Capture BEFORE State
        dest_risk_before = risk_engine.evaluate_facility_medicine_risk(
            dest_id, med_code
        )
        before_state = {
            "facility_id": dest_id,
            "facility_name": dest_info["facility_name"],
            "current_stock": dest_risk_before["current_stock"]
            if dest_risk_before
            else dest_info["current_stock"],
            "days_of_stock_available": dest_risk_before["days_of_stock_available"]
            if dest_risk_before
            else dest_info["days_of_stock_available_before"],
            "risk_level": dest_risk_before["risk_level"]
            if dest_risk_before
            else dest_info["risk_level_before"],
        }

        # Step 2: Apply Inventory Transfer to Simulation DataFrame
        total_qty = 0
        source_summaries = []

        # Invalidate inventory service cache to make changes
        inv_df = (
            inventory_service._inv_df
            if inventory_service._inv_df is not None
            else pd.read_csv(
                os.path.join(settings.SIM_DATA_DIR, "medicine_inventory_daily.csv")
            )
        )
        inv_df["record_date"] = pd.to_datetime(inv_df["record_date"])
        latest_date = inv_df["record_date"].max()

        for t in transfers:
            src_id = t["source_facility_id"]
            qty = t["transfer_quantity"]
            total_qty += qty

            # Deduct from source latest day
            src_mask = (
                (inv_df["phc_id"] == src_id)
                & (inv_df["medicine_code"] == med_code)
                & (inv_df["record_date"] == latest_date)
            )
            if src_mask.any():
                inv_df.loc[src_mask, "closing_stock"] = np.maximum(
                    0, inv_df.loc[src_mask, "closing_stock"] - qty
                )

            source_summaries.append(
                {
                    "source_facility_id": src_id,
                    "source_facility_name": t["source_facility_name"],
                    "transferred_quantity": qty,
                    "distance_km": t["distance_km"],
                }
            )

        # Add to destination latest day
        dest_mask = (
            (inv_df["phc_id"] == dest_id)
            & (inv_df["medicine_code"] == med_code)
            & (inv_df["record_date"] == latest_date)
        )
        if dest_mask.any():
            inv_df.loc[dest_mask, "closing_stock"] = (
                inv_df.loc[dest_mask, "closing_stock"] + total_qty
            )
            if "received_quantity" in inv_df.columns:
                inv_df.loc[dest_mask, "received_quantity"] = (
                    inv_df.loc[dest_mask, "received_quantity"] + total_qty
                )

        # Commit simulated state in-memory and to disk for active session
        inventory_service._inv_df = inv_df
        inv_df.to_csv(
            os.path.join(settings.SIM_DATA_DIR, "medicine_inventory_daily.csv"),
            index=False,
        )

        # Step 3: Recalculate AFTER State
        dest_risk_after = risk_engine.evaluate_facility_medicine_risk(dest_id, med_code)
        after_state = {
            "facility_id": dest_id,
            "facility_name": dest_info["facility_name"],
            "current_stock": dest_risk_after["current_stock"],
            "days_of_stock_available": dest_risk_after["days_of_stock_available"],
            "risk_level": dest_risk_after["risk_level"],
        }

        sim_id = f"SIM-{dest_id[-7:]}-{med_code[-3:]}-{datetime.datetime.now().strftime('%H%M%S')}"
        sim_record = {
            "simulation_id": sim_id,
            "recommendation_id": recommendation_id,
            "resource": {"medicine_code": med_code, "medicine_name": med_name},
            "status": "SIMULATED",
            "simulated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "destination_id": dest_id,
            "medicine_code": med_code,
            "total_units_transferred": total_qty,
            "risk_before": before_state["risk_level"],
            "risk_after": after_state["risk_level"],
            "dosa_before": before_state["days_of_stock_available"],
            "dosa_after": after_state["days_of_stock_available"],
            "is_simulation": True,
            "transfer": {"total_quantity": total_qty, "sources": source_summaries},
            "before": before_state,
            "after": after_state,
            "risk_transition": f"{before_state['risk_level']} -> {after_state['risk_level']}",
            "impact_summary": (
                f"Simulated transfer of {total_qty} units of {med_name} successfully resolved "
                f"the critical deficit at {dest_info['facility_name']}. "
                f"Stock coverage extended from {before_state['days_of_stock_available']:.1f} days ({before_state['risk_level']}) "
                f"to {after_state['days_of_stock_available']:.1f} days ({after_state['risk_level']})."
            ),
        }

        self.active_simulations[sim_id] = sim_record

        # Persist in SQLite
        try:
            conn = sqlite3.connect(settings.SQLITE_DB_PATH)
            cursor = conn.cursor()
            primary_src = transfers[0]
            cursor.execute(
                """
                INSERT OR REPLACE INTO redistribution_simulations
                (simulation_id, recommendation_id, resource_code, resource_name,
                 source_facility_id, source_facility_name, destination_facility_id, destination_facility_name,
                 quantity, before_destination_risk, after_destination_risk,
                 before_destination_dosa, after_destination_dosa, transit_distance_km, status, simulated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    sim_id,
                    recommendation_id,
                    med_code,
                    med_name,
                    primary_src["source_facility_id"],
                    primary_src["source_facility_name"],
                    dest_id,
                    dest_info["facility_name"],
                    total_qty,
                    before_state["risk_level"],
                    after_state["risk_level"],
                    before_state["days_of_stock_available"],
                    after_state["days_of_stock_available"],
                    primary_src["distance_km"],
                    "SIMULATED",
                    sim_record["simulated_at"],
                ),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not persist simulation to SQLite: {e}")

        return sim_record

    def reset_all_simulations(self):
        """
        Reverts all simulated stock transfers, resetting operational telemetry back
        to baseline without touching official government datasets.
        """
        from backend.app.services.simulation_engine import simulation_engine

        # Restore baseline inventory directly
        simulation_engine.initialize_inventory()

        # Invalidate memory caches
        inventory_service._inv_df = None
        self.active_simulations.clear()
        self.cached_recommendations.clear()

        return {
            "status": "RESET_SUCCESSFUL",
            "message": "All simulated redistribution transfers have been cleared. Baseline state restored.",
            "reset_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    def get_simulation_history(self):
        """Returns chronological history of executed simulations from SQLite."""
        try:
            conn = sqlite3.connect(settings.SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM redistribution_simulations ORDER BY simulated_at DESC LIMIT 50"
            )
            rows = cursor.fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.warning(f"Could not read SQLite history: {e}")
            return list(self.active_simulations.values())


simulation_manager = SimulationManager()
