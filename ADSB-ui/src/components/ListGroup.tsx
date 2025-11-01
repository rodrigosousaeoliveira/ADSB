import { useState } from "react";
import '../App.css';

interface ListGroupProps {
    items: string[];
    heading: string;
    onSelectItem: (item: string) => void;
}

function ListGroup({items, heading, onSelectItem}: ListGroupProps) {

    const [selectedIndex, setSelectedIndex] = useState(-1);

    return (<div className = "list-group-container">
      <h1>{heading}</h1>
      {items.length === 0 && <p>There are no items in the list.</p>}
      <ul className="list-group list-group2">
        {items.map((item, index) => (
          <li key={index} onClick={() => {
            setSelectedIndex(index); 
            onSelectItem(item);
        }} 
          className = {selectedIndex === index ? "list-group-item active" : "list-group-item"}>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
export default ListGroup;
