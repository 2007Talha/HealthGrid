"""
Swasthya Records - Emergency Management Service
"""

from backend.app.services.simulation_engine import simulation_engine


class EmergencyService:
    def trigger_emergency_scenario(self, scenario_req):
        return simulation_engine.trigger_emergency(scenario_req)

    def get_active_emergencies(self):
        return list(simulation_engine.active_emergencies.values())

    def clear_emergency(self, scenario_id=None):
        simulation_engine.clear_emergency(scenario_id)
        return {
            "status": "SUCCESS",
            "message": f"Cleared emergency {scenario_id if scenario_id else 'ALL'}",
        }


emergency_service = EmergencyService()
