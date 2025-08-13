import React, { useState } from 'react';
import RGL, { WidthProvider } from 'react-grid-layout';

const ReactGridLayout = WidthProvider(RGL);

const DashboardGrid: React.FC = () => {
  const [items, setItems] = useState([
    { i: 'a', x: 0, y: 0, w: 1, h: 2 },
    { i: 'b', x: 1, y: 0, w: 3, h: 2 },
    { i: 'c', x: 4, y: 0, w: 1, h: 2 },
  ]);

  const onLayoutChange = (layout) => {
    // This is where you would save the layout to the backend
  };

  const onRemoveItem = (i) => {
    setItems(items.filter((item) => item.i !== i));
  };

  const onAddItem = () => {
    setItems([
      ...items,
      {
        i: 'n' + items.length,
        x: (items.length * 2) % 12,
        y: Infinity, // puts it at the bottom
        w: 2,
        h: 2,
      },
    ]);
  };

  return (
    <div>
      <button onClick={onAddItem} className="mb-4 p-2 bg-blue-500 text-white rounded" aria-label="Add widget">Add Widget</button>
      <ReactGridLayout
        className="layout"
        layout={items}
        cols={12}
        rowHeight={30}
        onLayoutChange={onLayoutChange}
      >
        {items.map((item) => (
          <div key={item.i} className="bg-gray-200 rounded-lg p-4">
            <span className="text-xl">{item.i}</span>
            <span
              className="absolute top-2 right-2 cursor-pointer"
              onClick={() => onRemoveItem(item.i)}
            >
              x
            </span>
          </div>
        ))}
      </ReactGridLayout>
    </div>
  );
};

export default DashboardGrid;