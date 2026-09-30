"""
Swasthya Records - BigQuery Redistribution Layer Ingestion Script
Generates and batch-loads redistribution recommendations, candidate source matrices,
simulation lifecycle audits, and geo-routing transit pairs into BigQuery dataset arcadeaiagent.swasthyagrid.
"""

import os
import json
import uuid
import datetime
import pandas as pd

from backend.app.core.config import settings
from backend.app.services.geo_routing import geo_routing_service
from backend.app.services.redistribution_engine import redistribution_engine
from backend.app.services.simulation_manager import simulation_manager

def export_and_load_redistribution():
    print("[BIGQUERY EXPORT] Batch generating redistribution decisions and routes for BigQuery...")
    
    out_dir = os.path.join(settings.DATA_DIR, "processed", "redistribution")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Geo-Routing Table (All Pairwise Facility Routes)
    fac_df = geo_routing_service.facilities_df
    route_rows = []
    if fac_df is not None and not fac_df.empty:
        for i, row_a in fac_df.iterrows():
            for j, row_b in fac_df.iterrows():
                if row_a["facility_id"] != row_b["facility_id"]:
                    route_info = geo_routing_service.calculate_route(row_a["facility_id"], row_b["facility_id"])
                    route_rows.append({
                        "route_id": f"RT-{row_a['facility_id']}-{row_b['facility_id']}",
                        "source_id": row_a["facility_id"],
                        "source_name": row_a["facility_name"],
                        "destination_id": row_b["facility_id"],
                        "destination_name": row_b["facility_name"],
                        "origin_lat": route_info["source_coordinates"]["lat"],
                        "origin_lng": route_info["source_coordinates"]["lng"],
                        "destination_lat": route_info["destination_coordinates"]["lat"],
                        "destination_lng": route_info["destination_coordinates"]["lng"],
                        "distance_km": route_info["distance_km"],
                        "duration_hours": route_info["duration_hours"],
                        "route_type": route_info.get("routing_engine", "ROAD_NETWORK")
                    })
    routes_df = pd.DataFrame(route_rows)
    routes_path = os.path.join(out_dir, "redistribution_routes.csv")
    routes_df.to_csv(routes_path, index=False)
    
    # 2. Shortages, Candidate Sources, and Recommendations
    shortages = redistribution_engine.identify_all_shortages()
    rec_rows = []
    candidate_rows = []
    simulation_rows = []
    
    for s in shortages:
        dest_id = s["facility_id"]
        med_code = s["medicine_code"]
        
        # Discover candidates
        candidates = redistribution_engine.find_candidate_sources(dest_id, med_code)
        for idx, c in enumerate(candidates):
            candidate_rows.append({
                "candidate_id": f"CND-{dest_id}-{c['source_facility_id']}-{med_code}-{idx+1}",
                "destination_facility_id": dest_id,
                "destination_facility_name": s["facility_name"],
                "source_facility_id": c["source_facility_id"],
                "source_facility_name": c["source_facility_name"],
                "medicine_code": med_code,
                "medicine_name": s["medicine_name"],
                "current_stock": c["current_stock"],
                "protected_reserve": c["protected_reserve"],
                "transferable_surplus": c["transferable_surplus"],
                "distance_km": c["distance_km"],
                "duration_hours": c["duration_hours"],
                "priority_rank": idx + 1
            })
            
        # Run optimizer
        rec = redistribution_engine.optimize_redistribution(dest_id, med_code, max_sources=2)
        if rec["status"] == "OPTIMAL_RECOMMENDED":
            rec_id = rec["recommendation_id"]
            transfers_json = json.dumps(rec["transfers"])
            impact = rec["projected_impact"]
            
            primary_t = rec["transfers"][0]
            rec_rows.append({
                "recommendation_id": rec_id,
                "destination_facility_id": dest_id,
                "destination_facility_name": rec["destination"]["facility_name"],
                "medicine_code": med_code,
                "medicine_name": rec.get("resource", {}).get("medicine_name", med_code),
                "status": rec["status"],
                "net_deficit": rec["destination"]["net_deficit"],
                "total_recommended_quantity": rec["total_recommended_quantity"],
                "transfers_json": transfers_json,
                "source_count": len(rec["transfers"]),
                "estimated_transit_hours": primary_t["duration_hours"],
                "estimated_distance_km": primary_t["distance_km"],
                "dosa_before": rec["destination"]["days_of_stock_available_before"],
                "dosa_after": impact["days_of_stock_available_after"],
                "risk_before": rec["destination"]["risk_level_before"],
                "risk_after": impact.get("risk_level_after") or impact.get("projected_risk_after", "LOW"),
                "generated_at": rec.get("generated_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
            })
            
            # Create a sample simulation record
            sim_rows_entry = {
                "simulation_id": f"SIM-{uuid.uuid4().hex[:8].upper()}",
                "recommendation_id": rec_id,
                "destination_facility_id": dest_id,
                "medicine_code": med_code,
                "total_transferred": rec["total_recommended_quantity"],
                "before_stock": rec["destination"]["current_stock"],
                "before_dosa": rec["destination"]["days_of_stock_available_before"],
                "before_risk": rec["destination"]["risk_level_before"],
                "after_stock": impact.get("destination_stock_after") or impact.get("projected_stock_after", 0),
                "after_dosa": impact["days_of_stock_available_after"],
                "after_risk": impact.get("risk_level_after") or impact.get("projected_risk_after", "LOW"),
                "state": "PROPOSED",
                "simulated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            simulation_rows.append(sim_rows_entry)
            
    rec_df = pd.DataFrame(rec_rows) if rec_rows else pd.DataFrame(columns=[
        "recommendation_id", "destination_facility_id", "destination_facility_name", "medicine_code",
        "medicine_name", "status", "net_deficit", "total_recommended_quantity", "transfers_json",
        "source_count", "estimated_transit_hours", "estimated_distance_km", "dosa_before", "dosa_after",
        "risk_before", "risk_after", "generated_at"
    ])
    rec_path = os.path.join(out_dir, "redistribution_recommendations.csv")
    rec_df.to_csv(rec_path, index=False)
    
    cand_df = pd.DataFrame(candidate_rows) if candidate_rows else pd.DataFrame(columns=[
        "candidate_id", "destination_facility_id", "destination_facility_name", "source_facility_id",
        "source_facility_name", "medicine_code", "medicine_name", "current_stock", "protected_reserve",
        "transferable_surplus", "distance_km", "duration_hours", "priority_rank"
    ])
    cand_path = os.path.join(out_dir, "redistribution_candidates.csv")
    cand_df.to_csv(cand_path, index=False)
    
    sim_df = pd.DataFrame(simulation_rows) if simulation_rows else pd.DataFrame(columns=[
        "simulation_id", "recommendation_id", "destination_facility_id", "medicine_code",
        "total_transferred", "before_stock", "before_dosa", "before_risk",
        "after_stock", "after_dosa", "after_risk", "state", "simulated_at"
    ])
    sim_path = os.path.join(out_dir, "redistribution_simulations.csv")
    sim_df.to_csv(sim_path, index=False)
    
    print(f"[EXPORT COMPLETE] Generated Phase 4 Tables:\n - {routes_path} ({len(routes_df)} rows)\n - {rec_path} ({len(rec_df)} rows)\n - {cand_path} ({len(cand_df)} rows)\n - {sim_path} ({len(sim_df)} rows)")

    # 3. Load into BigQuery
    tables = [
        ("redistribution_routes", routes_path),
        ("redistribution_recommendations", rec_path),
        ("redistribution_candidates", cand_path),
        ("redistribution_simulations", sim_path)
    ]
    
    for table_name, csv_file in tables:
        cmd = f'bq load --autodetect --replace --source_format=CSV --skip_leading_rows=1 {settings.GCP_PROJECT_ID}:{settings.BIGQUERY_DATASET}.{table_name} "{csv_file}"'
        print(f"[BQ LOAD] Loading {table_name} into {settings.GCP_PROJECT_ID}:{settings.BIGQUERY_DATASET}...")
        os.system(cmd)

if __name__ == "__main__":
    export_and_load_redistribution()
