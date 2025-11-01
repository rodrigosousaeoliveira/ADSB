import { MapContainer,TileLayer,Marker,Popup } from 'react-leaflet'
import "leaflet/dist/leaflet.css"
import "../App.css";

interface MapProps {
    acData : any;
}

function MapComponent({acData}: MapProps) {
    let refPos = [46.071389, 14.481111]; // Reference position
  return (
    <div className="map-container">
      <h1>AIRCRAFT IN MY AREA</h1>
      <MapContainer center={refPos} zoom={8} scrollWheelZoom={true}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {acData.map((item) => (
          <Marker position={[item.latitude, item.longitude]}>
          <Popup>
            <ul>
            <li><b>Callsign:</b>{item.callsign}</li>
            <li><b>ICAO:</b>{item.icao}</li>
            <li><b>Altitude:</b>{item.altitude}</li>
            <li><b>Speed:</b>{item.speed}</li>
            </ul>
          </Popup>
        </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default MapComponent;
