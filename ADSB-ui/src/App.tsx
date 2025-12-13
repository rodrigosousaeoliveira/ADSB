import ListGroup from './components/ListGroup';
import RealTimeDataComponent from './components/RealTimeDataComponent';

function App() {
      let items =[
          'ICAO: XXXXXX',
          'Callsign: ABC123',
          'Altitude: 30000 ft',
          'Latitude: -23.5475',
          'Longitude: -46.6361',
          'Speed: 450 knots',
      ];
  const handleSelectItem = (item: string) =>{
    console.log(item);
  }
  return <div className='app-container'>
  {/*<ListGroup items={items} heading={'AIRCRAFT DATA'} onSelectItem={handleSelectItem}/>*/}
  <RealTimeDataComponent/>
  </div>
  }

export default App;