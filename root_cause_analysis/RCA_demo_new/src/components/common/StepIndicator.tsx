import { motion } from 'framer-motion';

interface Step {
  title: string;
  description?: string;
}

interface StepIndicatorProps {
  steps: Step[];
  currentStep: number;
  onStepClick?: (index: number) => void;
}

export function StepIndicator({ steps, currentStep, onStepClick }: StepIndicatorProps) {
  return (
    <div className="flex items-center justify-between w-full">
      {steps.map((step, index) => (
        <div key={index} className="flex items-center flex-1">
          <div className="flex flex-col items-center relative">
            <motion.div
              initial={false}
              animate={{
                backgroundColor: index <= currentStep ? '#0D7377' : '#DFE1E6',
                borderColor: index <= currentStep ? '#0D7377' : '#DFE1E6',
              }}
              className={`
                w-10 h-10 rounded-full flex items-center justify-center 
                border-2 font-medium text-sm transition-colors duration-300
                ${index < currentStep ? 'text-white' : index === currentStep ? 'text-white' : 'text-gray-400'}
              `}
              onClick={() => onStepClick?.(index)}
            >
              {index < currentStep ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                index + 1
              )}
            </motion.div>
            
            {index === currentStep && (
              <motion.div
                initial={{ scale: 1 }}
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ repeat: Infinity, duration: 2 }}
                className="absolute -inset-1 rounded-full border-2 border-primary/30"
              />
            )}
            
            <div className="absolute top-14 w-32 text-center">
              <p className={`text-xs font-medium ${index <= currentStep ? 'text-primary' : 'text-gray-400'}`}>
                {step.title}
              </p>
            </div>
          </div>
          
          {index < steps.length - 1 && (
            <div className="flex-1 mx-4 h-0.5 bg-gray-200 relative overflow-hidden">
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: index < currentStep ? '100%' : '0%' }}
                transition={{ duration: 0.5 }}
                className="absolute top-0 left-0 h-full bg-primary"
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
