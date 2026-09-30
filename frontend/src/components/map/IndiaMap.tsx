import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Facility } from '../../types';
import { SeverityBadge } from '../common/SeverityBadge';
import { ArrowRight, Building2, Bed, Users, AlertTriangle } from 'lucide-react';

// Fix default Leaflet icon assets
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface IndiaMapProps {
  facilities: Facility[];
  selectedFacilityId?: string;
  onSelectFacility?: (id: string) => void;
  filterRisk?: string;
  filterState?: string;
  className?: string;
}

const ChangeMapView: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
};

export const IndiaMap: React.FC<IndiaMapProps> = ({
  facilities,
  selectedFacilityId,
  onSelectFacility,
  filterRisk,
  filterState,
  className = 'h-[500px]'
}) => {
  const [mapCenter, setMapCenter] = useState<[number, number]>([22.5937, 78.9629]); // India geographic center
  const [mapZoom, setMapZoom] = useState<number>(5);

  const filtered = facilities.filter((f) => {
    if (filterRisk && filterRisk !== 'ALL') {
      if ((f.overall_risk || 'NORMAL') !== filterRisk) return false;
    }
    if (filterState && filterState !== 'ALL') {
      if (f.state_code !== filterState && f.state_name !== filterState) return false;
    }
    return true;
  });

  const getMarkerColor = (risk?: string) => {
    switch (risk?.toUpperCase()) {
      case 'CRITICAL':
        return '#ef4444';
      case 'HIGH':
        return '#f97316';
      case 'WARNING':
        return '#eab308';
      case 'NORMAL':
      default:
        return '#10b981';
    }
  };

  return (
    <div className={`relative rounded-xl overflow-hidden border border-slate-200 bg-command-950 ${className}`}>
      {/* Map Legend */}
      <div className="absolute top-3 right-3 z-[1000] p-2.5 rounded-lg bg-command-900/90 border border-slate-200/80 backdrop-blur-md text-[11px] space-y-1.5 shadow-xl">
        <p className="font-bold text-slate-600 uppercase tracking-wider text-[10px]">Resource Risk Level</p>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-sm shadow-red-500/50"></span>
          <span className="text-slate-600">Critical Shortage (🔴)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
          <span className="text-slate-600">High Risk (🟠)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
          <span className="text-slate-600">Warning (🟡)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          <span className="text-slate-600">Normal / Safe (🟢)</span>
        </div>
      </div>

      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <ChangeMapView center={mapCenter} zoom={mapZoom} />
        {/* OpenStreetMap basemap — 100% free and open, zero API key required */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {filtered.map((fac) => {
          const isSelected = fac.facility_id === selectedFacilityId;
          const color = getMarkerColor(fac.overall_risk);

          return (
            <CircleMarker
              key={fac.facility_id}
              center={[fac.latitude || 25.0, fac.longitude || 85.0]}
              radius={isSelected ? 10 : 7}
              pathOptions={{
                fillColor: color,
                fillOpacity: 0.9,
                color: isSelected ? '#ffffff' : '#0f172a',
                weight: isSelected ? 3 : 1.5
              }}
              eventHandlers={{
                click: () => {
                  if (onSelectFacility) onSelectFacility(fac.facility_id);
                }
              }}
            >
              <Popup>
                <div className="p-1 space-y-2 text-slate-800 min-w-[220px]">
                  <div className="flex items-start justify-between gap-2 border-b border-slate-200 pb-1.5">
                    <div>
                      <h4 className="text-xs font-bold text-slate-800">{fac.facility_name}</h4>
                      <span className="text-[10px] font-mono text-slate-500">({fac.facility_id})</span>
                    </div>
                    <SeverityBadge severity={fac.overall_risk || 'NORMAL'} size="sm" />
                  </div>

                  <div className="text-[11px] space-y-1 text-slate-600">
                    <p>
                      <strong className="text-slate-500">District:</strong> {fac.district_name}, {fac.state_name}
                    </p>
                    <p>
                      <strong className="text-slate-500">Type:</strong> {fac.facility_type}
                    </p>
                    <p>
                      <strong className="text-slate-500">Beds:</strong> {fac.sanctioned_beds || 6}
                    </p>
                  </div>

                  {onSelectFacility && (
                    <button
                      onClick={() => onSelectFacility(fac.facility_id)}
                      className="w-full mt-2 py-1.5 px-3 rounded bg-blue-600 hover:bg-blue-500 text-slate-900 text-[11px] font-bold flex items-center justify-center gap-1 transition-colors"
                    >
                      <span>Open Facility Command</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
};
