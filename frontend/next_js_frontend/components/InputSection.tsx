import React, { Dispatch, SetStateAction, useState } from 'react';

interface InputSectionProps {
    title: string;
    placeholder: string;
    data: string;
    setData: (value: string) => void;
    crewType: string;  // NEW PROP for crew type selection
    setCrewType: (value: string) => void; // NEW PROP function to update crew type
}

function InputSection({ setData, title, placeholder, data, crewType, setCrewType }: InputSectionProps) {
    const [inputValue, setInputValue] = useState("");

    const handleAddClick = () => {
        if (inputValue.trim() !== "") {
            setData(inputValue);  // Set `data` to `inputValue`
            setInputValue("");    // Clear input after setting
        }
    };

    return (
        <div className="mb-4">
            <h2 className="text-xl font-bold">{title}</h2>

            {/* Dropdown for selecting Crew Type */}
            <div className="mb-2">
                <label className="block text-gray-700">Select Crew Type:</label>
                <select
                    value={crewType}
                    onChange={(e) => setCrewType(e.target.value)}
                    className="p-2 border border-gray-300 rounded w-full"
                >
                    <option value="analysis">Analysis Crew</option>
                    <option value="summary">Summary Crew</option>
                </select>
            </div>

            {/* Query Input Field */}
            <div className="flex items-center mt-2">
                <input 
                    type="text"
                    placeholder={placeholder}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    className="p-2 border border-gray-300 rounded mr-2 flex-grow"
                />
                <button
                    onClick={handleAddClick}
                    className="bg-green-600 hover:bg-green-800 text-white font-bold py-2 px-4 rounded"
                >
                    Upload Query
                </button>
            </div>
            
            {/* Display the current data */}
            {data && (
                <div className="mt-4 p-2 border border-gray-300 rounded">
                    <span>{data}</span>
                </div>
            )}
        </div>
    );
}

export default InputSection;
