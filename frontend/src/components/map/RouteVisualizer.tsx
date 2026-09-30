import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Polyline, Popup } from 'react-leaflet';
import { Truck, ArrowRight } from 'lucide-react';
import { RedistributionRecommendation } from '../../types';

interface RouteVisualizerProps {
  recommendation: RedistributionRecommendation;
  sourceCoords?: { lat: number; lng: number };
  destCoords?: { lat: number; lng: number };
}

export const RouteVisualizer: React.FC<RouteVisualizerProps> = ({
  recommendation,
  sourceCoords: propSourceCoords,
  destCoords: propDestCoords
}) => {
  const recAny = recommendation as any;
  const effectiveSourceCoords = propSourceCoords || recommendation.sourceCoords ||
    (recAny.transfers?.[0]?.source_coordinates ? { lat: recAny.transfers[0].source_coordinates.lat, lng: recAny.transfers[0].source_coordinates.lng } : null) ||
    { lat: 25.5, lng: 85.31 };
  const effectiveDestCoords = propDestCoords || recommendation.destCoords ||
    (recAny.destination?.coordinates?.lat ? { lat: recAny.destination.coordinates.lat, lng: recAny.destination.coordinates.lng } : null) ||
    { lat: 25.46, lng: 85.53 };

  const centerLat = (effectiveSourceCoords.lat + effectiveDestCoords.lat) / 2;
  const centerLng = (effectiveSourceCoords.lng + effectiveDestCoords.lng) / 2;

  const primarySource = recommendation.sources?.[0] ||
    (recAny.transfers?.[0] ? {
      source_name: recAny.transfers[0].source_facility_name,
      transfer_units: recAny.transfers[0].transfer_quantity,
      distance_km: recAny.transfers[0].distance_km,
      travel_time_hours: recAny.transfers[0].duration_hours
    } : {
      source_name: 'Primary Source PHC',
      transfer_units: recommendation.total_transfer_allocated ?? recAny.total_recommended_quantity ?? 0,
      distance_km: recommendation.total_distance_km ?? 0,
      travel_time_hours: recommendation.max_eta_hours ?? 0
    });

  const medName = recommendation.medicine_name || recAny.resource?.medicine_name || 'Essential Medicine';
  const totalAllocated = recommendation.total_transfer_allocated ?? recAny.total_recommended_quantity ?? primarySource.transfer_units ?? 0;
  const totalDist = Number(recommendation.total_distance_km ?? primarySource.distance_km ?? 0);
  const etaHours = Number(recommendation.max_eta_hours ?? primarySource.travel_time_hours ?? 0);

  return (
    <div className="space-y-4">
      {/* Route Summary Metric Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3 rounded-lg bg-command-900 border border-slate-200 text-center">
          <p className="text-[10px] uppercase font-bold text-slate-500">Medicine</p>
          <p className="text-sm font-bold text-slate-800 truncate">{medName}</p>
        </div>
        <div className="p-3 rounded-lg bg-command-900 border border-slate-200 text-center">
          <p className="text-[10px] uppercase font-bold text-slate-500">Transfer Allocation</p>
          <p className="text-sm font-bold text-emerald-600 font-mono">
            {totalAllocated} units
          </p>
        </div>
        <div className="p-3 rounded-lg bg-command-900 border border-slate-200 text-center">
          <p className="text-[10px] uppercase font-bold text-slate-500">Total Distance</p>
          <p className="text-sm font-bold text-blue-600 font-mono">
            {totalDist.toFixed(1)} km
          </p>
        </div>
        <div className="p-3 rounded-lg bg-command-900 border border-slate-200 text-center">
          <p className="text-[10px] uppercase font-bold text-slate-500">Estimated Transit</p>
          <p className="text-sm font-bold text-cyan-600 font-mono">
            {etaHours.toFixed(1)} hrs
          </p>
        </div>
      </div>

      {/* Interactive Map Visualizer */}
      <div className="h-64 rounded-xl overflow-hidden border border-slate-200">
        <MapContainer
          center={[centerLat, centerLng]}
          zoom={10}
          scrollWheelZoom={false}
          className="w-full h-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Polyline Route */}
          <Polyline
            positions={[
              [effectiveSourceCoords.lat, effectiveSourceCoords.lng],
              [effectiveDestCoords.lat, effectiveDestCoords.lng]
            ]}
            pathOptions={{
              color: '#3b82f6',
              weight: 4,
              dashArray: '8, 8',
              opacity: 0.85
            }}
          />

          {/* Source Marker (Green) */}
          <CircleMarker
            center={[effectiveSourceCoords.lat, effectiveSourceCoords.lng]}
            radius={8}
            pathOptions={{ fillColor: '#10b981', fillOpacity: 1, color: '#ffffff', weight: 2 }}
          >
            <Popup>
              <div className="text-xs text-slate-800 p-1">
                <span className="font-bold text-emerald-600 uppercase text-[10px]">Surplus Donor Source</span>
                <p className="font-bold">{primarySource.source_name}</p>
                <p className="text-[11px] text-slate-600">Dispatching: {primarySource.transfer_units} units</p>
              </div>
            </Popup>
          </CircleMarker>

          {/* Destination Marker (Red) */}
          <CircleMarker
            center={[effectiveDestCoords.lat, effectiveDestCoords.lng]}
            radius={8}
            pathOptions={{ fillColor: '#ef4444', fillOpacity: 1, color: '#ffffff', weight: 2 }}
          >
            <Popup>
              <div className="text-xs text-slate-800 p-1">
                <span className="font-bold text-red-600 uppercase text-[10px]">Shortage Destination</span>
                <p className="font-bold">{recommendation.destination_name || recAny.destination?.facility_name || 'Destination'}</p>
                <p className="text-[11px] text-slate-600">Receiving: {totalAllocated} units</p>
              </div>
            </Popup>
          </CircleMarker>
        </MapContainer>
      </div>
    </div>
  );
};
