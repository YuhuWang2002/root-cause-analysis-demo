import { create } from 'zustand';
import * as api from '@/services/api';

interface OntologyState {
  ontologies: api.Ontology[];
  currentOntology: api.Ontology | null;
  selectedClassId: number | null;
  isLoading: boolean;
  isPanelOpen: boolean;
  
  fetchOntologies: (projectId: string) => Promise<void>;
  createOntology: (projectId: string, name: string, description: string) => Promise<api.Ontology>;
  updateOntology: (projectId: string, ontologyId: number, data: Partial<api.Ontology>) => Promise<void>;
  deleteOntology: (projectId: string, ontologyId: number) => Promise<void>;
  selectOntology: (ontology: api.Ontology | null) => void;
  
  createClass: (projectId: string, ontologyId: number, name: string, description: string) => Promise<api.OntologyClass>;
  updateClass: (projectId: string, ontologyId: number, classId: number, data: Partial<api.OntologyClass>) => Promise<void>;
  deleteClass: (projectId: string, ontologyId: number, classId: number) => Promise<void>;
  selectClass: (classId: number | null) => void;
  
  addProperty: (projectId: string, ontologyId: number, classId: number, name: string, type: string, description: string) => Promise<void>;
  updateProperty: (projectId: string, ontologyId: number, classId: number, propId: number, data: { name?: string; type?: string; description?: string }) => Promise<void>;
  deleteProperty: (projectId: string, ontologyId: number, classId: number, propId: number) => Promise<void>;
  
  addRelation: (projectId: string, ontologyId: number, sourceClassId: number, targetClassId: number, relationType: string, description?: string) => Promise<void>;
  deleteRelation: (projectId: string, ontologyId: number, relationId: number) => Promise<void>;
  
  saveCanvas: (projectId: string, ontologyId: number, canvasData: any[]) => Promise<void>;
  
  openPanel: () => void;
  closePanel: () => void;
}

export const useOntologyStore = create<OntologyState>((set, get) => ({
  ontologies: [],
  currentOntology: null,
  selectedClassId: null,
  isLoading: false,
  isPanelOpen: false,

  fetchOntologies: async (projectId: string) => {
    set({ isLoading: true });
    try {
      const ontologies = await api.getOntologies(projectId);
      set({ ontologies, isLoading: false });
    } catch (error) {
      console.error('Failed to fetch ontologies:', error);
      set({ isLoading: false });
    }
  },

  createOntology: async (projectId, name, description) => {
    const ontology = await api.createOntology(projectId, { name, description });
    set((state) => ({ ontologies: [...state.ontologies, ontology] }));
    return ontology;
  },

  updateOntology: async (projectId, ontologyId, data) => {
    const updated = await api.updateOntology(projectId, ontologyId, data);
    set((state) => ({
      ontologies: state.ontologies.map((o) => (o.id === ontologyId ? updated : o)),
      currentOntology: state.currentOntology?.id === ontologyId ? updated : state.currentOntology,
    }));
  },

  deleteOntology: async (projectId, ontologyId) => {
    await api.deleteOntology(projectId, ontologyId);
    set((state) => ({
      ontologies: state.ontologies.filter((o) => o.id !== ontologyId),
      currentOntology: state.currentOntology?.id === ontologyId ? null : state.currentOntology,
    }));
  },

  selectOntology: (ontology) => {
    set({ currentOntology: ontology, selectedClassId: null });
  },

  createClass: async (projectId, ontologyId, name, description) => {
    const ontologyClass = await api.createOntologyClass(projectId, ontologyId, { name, description });
    const { currentOntology } = get();
    if (currentOntology && currentOntology.id === ontologyId) {
      set({
        currentOntology: {
          ...currentOntology,
          classes: [...currentOntology.classes, ontologyClass],
        },
      });
    }
    return ontologyClass;
  },

  updateClass: async (projectId, ontologyId, classId, data) => {
    const updated = await api.updateOntologyClass(projectId, ontologyId, classId, data);
    const { currentOntology } = get();
    if (currentOntology && currentOntology.id === ontologyId) {
      set({
        currentOntology: {
          ...currentOntology,
          classes: currentOntology.classes.map((c) => (c.id === classId ? { ...c, ...updated } : c)),
        },
      });
    }
  },

  deleteClass: async (projectId, ontologyId, classId) => {
    await api.deleteOntologyClass(projectId, ontologyId, classId);
    const { currentOntology, selectedClassId } = get();
    if (currentOntology && currentOntology.id === ontologyId) {
      set({
        currentOntology: {
          ...currentOntology,
          classes: currentOntology.classes.filter((c) => c.id !== classId),
        },
        selectedClassId: selectedClassId === classId ? null : selectedClassId,
      });
    }
  },

  selectClass: (classId) => {
    set({ selectedClassId: classId });
  },

  addProperty: async (projectId, ontologyId, classId, name, type, description) => {
    const properties = await api.addClassProperty(projectId, ontologyId, classId, { name, type, description });
    const { currentOntology } = get();
    if (currentOntology && currentOntology.id === ontologyId) {
      set({
        currentOntology: {
          ...currentOntology,
          classes: currentOntology.classes.map((c) =>
            c.id === classId ? { ...c, properties } : c
          ),
        },
      });
    }
  },

  updateProperty: async (projectId, ontologyId, classId, propId, data) => {
    const properties = await api.updateClassProperty(projectId, ontologyId, classId, propId, data);
    const { currentOntology } = get();
    if (currentOntology && currentOntology.id === ontologyId) {
      set({
        currentOntology: {
          ...currentOntology,
          classes: currentOntology.classes.map((c) =>
            c.id === classId ? { ...c, properties } : c
          ),
        },
      });
    }
  },

  deleteProperty: async (projectId, ontologyId, classId, propId) => {
    const properties = await api.deleteClassProperty(projectId, ontologyId, classId, propId);
    const { currentOntology } = get();
    if (currentOntology && currentOntology.id === ontologyId) {
      set({
        currentOntology: {
          ...currentOntology,
          classes: currentOntology.classes.map((c) =>
            c.id === classId ? { ...c, properties } : c
          ),
        },
      });
    }
  },

  addRelation: async (projectId, ontologyId, sourceClassId, targetClassId, relationType, description) => {
    const relation = await api.createOntologyRelation(projectId, ontologyId, {
      source_class_id: sourceClassId,
      target_class_id: targetClassId,
      relation_type: relationType,
      description,
    });
    const { currentOntology } = get();
    if (currentOntology && currentOntology.id === ontologyId) {
      set({
        currentOntology: {
          ...currentOntology,
          relations: [...currentOntology.relations, relation],
        },
      });
    }
  },

  deleteRelation: async (projectId, ontologyId, relationId) => {
    await api.deleteOntologyRelation(projectId, ontologyId, relationId);
    const { currentOntology } = get();
    if (currentOntology && currentOntology.id === ontologyId) {
      set({
        currentOntology: {
          ...currentOntology,
          relations: currentOntology.relations.filter((r) => r.id !== relationId),
        },
      });
    }
  },

  saveCanvas: async (projectId, ontologyId, canvasData) => {
    const updated = await api.saveOntologyCanvas(projectId, ontologyId, canvasData);
    set((state) => ({
      ontologies: state.ontologies.map((o) => (o.id === ontologyId ? updated : o)),
      currentOntology: state.currentOntology?.id === ontologyId ? updated : state.currentOntology,
    }));
  },

  openPanel: () => set({ isPanelOpen: true }),
  closePanel: () => set({ isPanelOpen: false, currentOntology: null, selectedClassId: null }),
}));
