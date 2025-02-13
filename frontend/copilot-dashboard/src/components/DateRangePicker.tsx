import React from 'react';

interface DateRangePickerProps {
  startDate: Date;
  endDate: Date;
  onStartDateChange: (date: Date) => void;
  onEndDateChange: (date: Date) => void;
}

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
}) => {
  return (
    <div className="flex items-center space-x-4 bg-white p-4 rounded-lg shadow-sm">
      <div className="flex items-center space-x-2">
        <label htmlFor="start-date" className="text-sm font-medium text-gray-600">
          From:
        </label>
        <input
          type="date"
          id="start-date"
          className="border rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={startDate.toISOString().split('T')[0]}
          onChange={(e) => onStartDateChange(new Date(e.target.value))}
        />
      </div>
      <div className="flex items-center space-x-2">
        <label htmlFor="end-date" className="text-sm font-medium text-gray-600">
          To:
        </label>
        <input
          type="date"
          id="end-date"
          className="border rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={endDate.toISOString().split('T')[0]}
          onChange={(e) => onEndDateChange(new Date(e.target.value))}
        />
      </div>
      <div className="flex space-x-2">
        <button
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md"
          onClick={() => {
            const end = new Date();
            const start = new Date();
            start.setDate(end.getDate() - 7);
            onStartDateChange(start);
            onEndDateChange(end);
          }}
        >
          7D
        </button>
        <button
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md"
          onClick={() => {
            const end = new Date();
            const start = new Date();
            start.setDate(end.getDate() - 30);
            onStartDateChange(start);
            onEndDateChange(end);
          }}
        >
          30D
        </button>
        <button
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md"
          onClick={() => {
            const end = new Date();
            const start = new Date();
            start.setDate(end.getDate() - 90);
            onStartDateChange(start);
            onEndDateChange(end);
          }}
        >
          90D
        </button>
      </div>
    </div>
  );
}; 