import React, { useState } from 'react';

interface Mapping {
  source: string;
  target: string;
}

interface ColumnMappingInterfaceProps {
  sourceColumns: string[];
  targetFields: string[];
  onSubmit: (mappings: { primary: Mapping[]; additional: Mapping[] }) => void;
}

const ColumnMappingInterface: React.FC<ColumnMappingInterfaceProps> = ({
  sourceColumns,
  targetFields,
  onSubmit,
}) => {
  const [primaryMappings, setPrimaryMappings] = useState<Mapping[]>([]);
  const [additionalMappings, setAdditionalMappings] = useState<Mapping[]>([]);

  const handleAddMapping = (type: 'primary' | 'additional') => {
    if (type === 'primary') {
      setPrimaryMappings([...primaryMappings, { source: '', target: '' }]);
    } else {
      setAdditionalMappings([...additionalMappings, { source: '', target: '' }]);
    }
  };

  const handleRemoveMapping = (type: 'primary' | 'additional', index: number) => {
    if (type === 'primary') {
      setPrimaryMappings(primaryMappings.filter((_, i) => i !== index));
    } else {
      setAdditionalMappings(additionalMappings.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ primary: primaryMappings, additional: additionalMappings });
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Column Mapping</h2>
      
      <h3 className="text-lg font-bold mb-2">Primary Mappings</h3>
      {primaryMappings.map((mapping, index) => (
        <div key={index} className="flex items-center mb-2">
          <select className="p-2 border rounded-l-lg" title="Source Column">
            {sourceColumns.map((col) => <option key={col} value={col}>{col}</option>)}
          </select>
          <select className="p-2 border-t border-b" title="Target Field">
            {targetFields.map((field) => <option key={field} value={field}>{field}</option>)}
          </select>
          <button onClick={() => handleRemoveMapping('primary', index)} className="p-2 bg-red-500 text-white rounded-r-lg" aria-label="Remove primary mapping">
            Remove
          </button>
        </div>
      ))}
      <button onClick={() => handleAddMapping('primary')} className="mb-4 p-2 bg-green-500 text-white rounded" aria-label="Add primary mapping">
        Add Primary Mapping
      </button>

      <h3 className="text-lg font-bold mb-2">Additional Mappings</h3>
      {additionalMappings.map((mapping, index) => (
        <div key={index} className="flex items-center mb-2">
          <select className="p-2 border rounded-l-lg" title="Source Column">
            {sourceColumns.map((col) => <option key={col} value={col}>{col}</option>)}
          </select>
          <input type="text" className="p-2 border-t border-b" placeholder="Target Field" title="Target Field" />
          <button onClick={() => handleRemoveMapping('additional', index)} className="p-2 bg-red-500 text-white rounded-r-lg" aria-label="Remove additional mapping">
            Remove
          </button>
        </div>
      ))}
      <button onClick={() => handleAddMapping('additional')} className="mb-4 p-2 bg-green-500 text-white rounded" aria-label="Add additional mapping">
        Add Additional Mapping
      </button>

      <button type="submit" className="w-full p-2 bg-blue-500 text-white rounded" aria-label="Save mapping">
        Save Mapping
      </button>
    </form>
  );
};

export default ColumnMappingInterface;