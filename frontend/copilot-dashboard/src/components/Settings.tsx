import React from 'react';

interface SettingsProps {
  maxDevs: number;
  meanSalary: number;
  onMaxDevsChange: (value: number) => void;
  onMeanSalaryChange: (value: number) => void;
}

export const Settings: React.FC<SettingsProps> = ({
  maxDevs,
  meanSalary,
  onMaxDevsChange,
  onMeanSalaryChange,
}) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Settings</h2>
      <div className="space-y-4">
        <div>
          <label htmlFor="maxDevs" className="block text-sm font-medium text-gray-700">
            Maximum Number of Developers
          </label>
          <input
            type="number"
            id="maxDevs"
            value={maxDevs}
            onChange={(e) => onMaxDevsChange(Number(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            min="1"
          />
        </div>
        <div>
          <label htmlFor="meanSalary" className="block text-sm font-medium text-gray-700">
            Mean Developer Salary (USD)
          </label>
          <input
            type="number"
            id="meanSalary"
            value={meanSalary}
            onChange={(e) => onMeanSalaryChange(Number(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            min="0"
            step="1000"
          />
        </div>
      </div>
    </div>
  );
}; 