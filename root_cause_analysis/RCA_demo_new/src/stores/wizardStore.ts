import { create } from 'zustand';
import type { 
  DataSource, 
  DataPermission, 
  DataTransform, 
  QualityConstraint, 
  Ontology, 
  AnalysisConfig 
} from '@/types';

interface WizardState {
  currentStep: number;
  totalSteps: number;
  projectName: string;
  projectDescription: string;
  scenario: string;
  dataSources: DataSource[];
  dataPermissions: DataPermission;
  dataTransform: DataTransform;
  qualityConstraints: QualityConstraint[];
  ontology: Ontology;
  analysisConfig: AnalysisConfig;
  
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  setProjectName: (name: string) => void;
  setProjectDescription: (description: string) => void;
  setScenario: (scenario: string) => void;
  addDataSource: (source: DataSource) => void;
  removeDataSource: (id: string) => void;
  updateDataSource: (id: string, updates: Partial<DataSource>) => void;
  setDataPermissions: (permissions: DataPermission) => void;
  setDataTransform: (transform: DataTransform) => void;
  addQualityConstraint: (constraint: QualityConstraint) => void;
  removeQualityConstraint: (id: string) => void;
  setOntology: (ontology: Ontology) => void;
  setAnalysisConfig: (config: AnalysisConfig) => void;
  reset: () => void;
}

const initialData = {
  currentStep: 0,
  totalSteps: 7,
  projectName: '',
  projectDescription: '',
  scenario: '',
  dataSources: [] as DataSource[],
  dataPermissions: { tables: [] } as DataPermission,
  dataTransform: {
    outputFormat: 'json' as const,
    storageLocation: '',
    rules: [],
    schedule: 'manual' as const,
  },
  qualityConstraints: [] as QualityConstraint[],
  ontology: {
    id: '',
    type: 'causal' as const,
    entities: [],
    relations: [],
  },
  analysisConfig: {
    methods: ['causal_analysis', 'root_cause'] as ("causal_analysis" | "root_cause" | "correlation")[],
    algorithm: 'pc' as const,
    parameters: {
      confidenceThreshold: 0.95,
      maxPathLength: 3,
    },
    outputFormat: 'json' as const,
  },
};

export const useWizardStore = create<WizardState>()((set) => ({
  ...initialData,

  setStep: (step) => set({ currentStep: step }),
  
  nextStep: () => set((state) => ({
    currentStep: Math.min(state.currentStep + 1, state.totalSteps - 1)
  })),
  
  prevStep: () => set((state) => ({
    currentStep: Math.max(state.currentStep - 1, 0)
  })),
  
  setProjectName: (name) => set({ projectName: name }),
  setProjectDescription: (description) => set({ projectDescription: description }),
  setScenario: (scenario) => set({ scenario }),
  
  addDataSource: (source) => set((state) => ({
    dataSources: [...state.dataSources, source]
  })),
  
  removeDataSource: (id) => set((state) => ({
    dataSources: state.dataSources.filter((s) => s.id !== id)
  })),
  
  updateDataSource: (id, updates) => set((state) => ({
    dataSources: state.dataSources.map((s) =>
      s.id === id ? { ...s, ...updates } : s
    )
  })),
  
  setDataPermissions: (permissions) => set({ dataPermissions: permissions }),
  setDataTransform: (transform) => set({ dataTransform: transform }),
  
  addQualityConstraint: (constraint) => set((state) => ({
    qualityConstraints: [...state.qualityConstraints, constraint]
  })),
  
  removeQualityConstraint: (id) => set((state) => ({
    qualityConstraints: state.qualityConstraints.filter((c) => c.id !== id)
  })),
  
  setOntology: (ontology) => set({ ontology }),
  setAnalysisConfig: (config) => set({ analysisConfig: config }),
  
  reset: () => set(initialData),
}));
