import { MapContainer,TileLayer,Marker,Popup } from 'react-leaflet'
import "leaflet/dist/leaflet.css"
import "../App.css";
import L from 'leaflet';
interface MapProps {
    acData : any;
}

const createImageIcon = (imageUrl:any) => {
  return L.divIcon({
    html: `
      <div style="
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-image: url('${imageUrl}');
        background-size: cover;
        background-position: center;
        border: 3px solid white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
      "></div>
    `,
    className: 'image-marker',
    iconSize: [20, 20],
    iconAnchor: [20, 0],
  });
};


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
          <Marker position={[item.latitude, item.longitude]} icon = {createImageIcon("./src/assets/plane_64px.png")}>
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
