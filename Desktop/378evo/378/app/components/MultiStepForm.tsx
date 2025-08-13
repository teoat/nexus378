import React, { useState } from 'react';

interface MultiStepFormProps {
  steps: React.ReactNode[];
}

const MultiStepForm: React.FC<MultiStepFormProps> = ({ steps }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const next = () => {
    setCurrentStep(prev => (prev < steps.length - 1 ? prev + 1 : prev));
  };

  const prev = () => {
    setCurrentStep(prev => (prev > 0 ? prev - 1 : prev));
  };

  return (
    <div className="p-4">
      {steps[currentStep]}
      <div className="mt-4 flex justify-between">
        {currentStep > 0 && (
          <button onClick={prev} className="px-4 py-2 bg-gray-300 rounded" aria-label="Previous step">
            Previous
          </button>
        )}
        {currentStep < steps.length - 1 && (
          <button onClick={next} className="px-4 py-2 bg-blue-500 text-white rounded" aria-label="Next step">
            Next
          </button>
        )}
        {currentStep === steps.length - 1 && (
          <button className="px-4 py-2 bg-green-500 text-white rounded" aria-label="Submit form">
            Submit
          </button>
        )}
      </div>
    </div>
  );
};

export default MultiStepForm;