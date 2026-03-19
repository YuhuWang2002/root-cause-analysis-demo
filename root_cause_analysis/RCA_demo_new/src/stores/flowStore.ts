import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import * as api from '@/services/api';

export type NodeType = 'system' | 'acquisition' | 'datapipeline' | 'quality' | 'dataset' | 'ontology' | 'ontologyExplore' | 'analysis' | 'rootCause';
export type NodeStatus = 'pending' | 'running' | 'completed' | 'configured' | 'unconfigured';

export interface FlowNodeData {
  id: string;
  name: string;
  type: NodeType;
  status: NodeStatus;
  description?: string;
  detail?: string;
  x: number;
  y: number;
  parentId?: string;
  config?: Record<string, unknown>;
}

export interface FlowConnection {
  id: string;
  from: string;
  to: string;
}

export interface ProjectFlowData {
  nodes: FlowNodeData[];
  connections: FlowConnection[];
  automation?: {
    enabled: boolean;
    frequency: 'manual' | 'hourly' | 'daily' | 'weekly';
    time?: string;
    notifyOnComplete: boolean;
    notifyEmail?: string;
  };
  permissions?: {
    roles: Array<{
      id: string;
      name: string;
      description: string;
      permissions: {
        create: boolean;
        edit: boolean;
        delete: boolean;
        view: boolean;
        export: boolean;
      };
    }>;
  };
}

interface FlowState {
  projectsData: Record<string, ProjectFlowData>;
  currentProjectId: string | null;
  selectedNodeId: string | null;
  isConfigPanelOpen: boolean;
  isPlaying: boolean;
  isAddModalOpen: boolean;
  addModalType: 'system' | 'dataset' | 'ontology' | 'analysis' | null;
  
  loadProject: (projectId: string, scenario?: string) => void;
  setSelectedNode: (id: string | null) => void;
  toggleConfigPanel: (open?: boolean) => void;
  togglePlay: () => void;
  openAddModal: (type: 'system' | 'dataset' | 'ontology' | 'analysis') => void;
  closeAddModal: () => void;
  addNode: (type: NodeType, x: number, y: number, name?: string) => void;
  addDataSource: (name: string, description: string, connection: string) => void;
  addOntology: (name: string, datasetId?: string) => void;
  addAnalysis: (name: string, type: 'ontology_explore' | 'data_analysis' | 'root_cause', ontologyId?: string) => void;
  removeNode: (id: string) => void;
  removeDataSource: (id: string) => void;
  addDataset: (name: string, sourceIds: string[]) => void;
  removeDataset: (id: string) => void;
  updateNodeStatus: (id: string, status: NodeStatus) => void;
  updateNodeConfig: (id: string, config: Record<string, unknown>) => void;
  updateNodePosition: (id: string, x: number, y: number) => void;
  updateNodeName: (id: string, name: string) => void;
  updateNodeNameByOntologyId: (ontologyId: number, name: string) => void;
  updateNodeOntologyId: (oldOntologyId: number, newOntologyId: number, newName: string) => void;
  addConnection: (from: string, to: string) => void;
  updateProjectAutomation: (projectId: string, config: Record<string, unknown>) => void;
  updateProjectPermissions: (projectId: string, permissions: Record<string, unknown>) => void;
}

const COLUMN_WIDTH = 220;
const ROW_HEIGHT = 120;
const START_X = 0;
const START_Y = 60;

const getInitialNodes = () => [

];

const getInitialConnections = () => [
  { id: 'c1', from: 'src-1', to: 'acq-1' },
  { id: 'c2', from: 'src-2', to: 'acq-2' },
  { id: 'c3', from: 'src-3', to: 'acq-3' },
  
  { id: 'c4', from: 'acq-1', to: 'proc-1' },
  { id: 'c5', from: 'acq-2', to: 'proc-2' },
  { id: 'c6', from: 'acq-3', to: 'proc-3' },
  
  { id: 'c7', from: 'proc-1', to: 'qual-1' },
  { id: 'c8', from: 'proc-2', to: 'qual-2' },
  { id: 'c9', from: 'proc-3', to: 'qual-3' },
  
  { id: 'c10', from: 'qual-1', to: 'ds-1' },
  { id: 'c11', from: 'qual-2', to: 'ds-1' },
  { id: 'c12', from: 'qual-3', to: 'ds-1' },
  
  { id: 'c13', from: 'ds-1', to: 'onto-1' },
  
  { id: 'c14', from: 'onto-1', to: 'ana-1' },
  { id: 'c15', from: 'onto-1', to: 'ana-2' },
  { id: 'c16', from: 'onto-1', to: 'ana-3' },
];

const defaultProjectData: ProjectFlowData = {
  nodes: [],
  connections: [],
};

export const useFlowStore = create<FlowState>()(
  persist(
    (set, get) => ({
      projectsData: {},
      currentProjectId: null,
      selectedNodeId: null,
      isConfigPanelOpen: false,
      isPlaying: true,
      isAddModalOpen: false,
      addModalType: null,

      loadProject: async (projectId: string, scenario?: string) => {
        const state = get();
        const projectData = state.projectsData[projectId];

        const isAnalysisScenario = scenario === 'inventory';

        console.log('===== loadProject called =====');
        console.log('projectId:', projectId);
        console.log('scenario:', scenario);
        console.log('existing projectData:', projectData);

        try {
          const canvasData = await api.getCanvas(projectId);
          console.log('canvasData from API:', canvasData);
          console.log('canvasData.nodes:', canvasData?.nodes);
          console.log('canvasData.connections:', canvasData?.connections);

          let nodesToUse;
          if (canvasData.nodes && canvasData.nodes.length > 0) {
            nodesToUse = canvasData.nodes;
            console.log('Using nodes from API:', nodesToUse);
          } else if (isAnalysisScenario) {
            nodesToUse = getInitialNodes();
            console.log('Using initial nodes for analysis scenario');
          } else {
            nodesToUse = [];
            console.log('No nodes to use, empty array');
          }

          set({
            currentProjectId: projectId,
            projectsData: {
              ...state.projectsData,
              [projectId]: {
                nodes: nodesToUse,
                connections: canvasData.connections || []
              },
            },
          });
          console.log('State updated with nodes:', nodesToUse);
        } catch (error) {
          console.error('Failed to load canvas from API:', error);
          
          if (projectData && projectData.nodes.length > 0) {
            set({ currentProjectId: projectId });
          } else if (isAnalysisScenario) {
            set({
              currentProjectId: projectId,
              projectsData: {
                ...state.projectsData,
                [projectId]: { nodes: getInitialNodes(), connections: [] },
              },
            });
          } else {
            set({
              currentProjectId: projectId,
              projectsData: {
                ...state.projectsData,
                [projectId]: { nodes: [], connections: [] },
              },
            });
          }
        }
      },

      setSelectedNode: (id) => set({ 
        selectedNodeId: id,
        isConfigPanelOpen: id !== null 
      }),
      
      toggleConfigPanel: (open) => set((state) => ({ 
        isConfigPanelOpen: open !== undefined ? open : !state.isConfigPanelOpen,
        selectedNodeId: open === false ? null : state.selectedNodeId
      })),
      
      togglePlay: () => set((state) => ({ isPlaying: !state.isPlaying })),
      
      openAddModal: (type) => set({ isAddModalOpen: true, addModalType: type }),
      closeAddModal: () => set({ isAddModalOpen: false, addModalType: null }),
      
      addNode: async (type, x, y, name) => {
        const state = get();
        const projectId = state.currentProjectId;
        if (!projectId) return;

        const projectData = state.projectsData[projectId] || defaultProjectData;
        const typeNodes = projectData.nodes.filter(n => n.type === type);
        const typeIndex = typeNodes.length;

        const typeLabels: Record<NodeType, string> = {
          system: '源系统',
          acquisition: '数据表',
          datapipeline: 'DataPipeline',
          quality: '质量约束',
          dataset: '数据集',
          ontology: '本体库',
          ontologyExplore: '本体探索',
          analysis: '数据分析',
          rootCause: '根因分析',
        };

        let newNodeConfig: Record<string, unknown> = {};

        if (type === 'ontology') {
          try {
            const ontology = await api.createOntology(projectId, {
              name: name || `${typeLabels[type]} ${typeIndex + 1}`,
              description: ''
            });
            console.log('Created new ontology:', ontology);
            newNodeConfig = { ontologyId: ontology.id };
          } catch (error) {
            console.error('Failed to create ontology:', error);
          }
        }

        const newNode: FlowNodeData = {
          id: `${type}-${Date.now()}`,
          name: name || `${typeLabels[type]} ${typeIndex + 1}`,
          type,
          status: 'pending',
          x,
          y,
          config: Object.keys(newNodeConfig).length > 0 ? newNodeConfig : undefined,
        };

        const updatedNodes = [...projectData.nodes, newNode];
        const updatedConnections = projectData.connections;

        console.log('===== addNode: saving to backend =====');
        console.log('projectId:', projectId);
        console.log('updatedNodes:', updatedNodes);

        set({
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              nodes: updatedNodes,
              connections: updatedConnections,
            },
          },
        });

        set({ selectedNodeId: newNode.id, isConfigPanelOpen: true });

        try {
          await api.saveCanvas(projectId, {
            nodes: updatedNodes,
            connections: updatedConnections
          });
          console.log('===== addNode: saved successfully =====');
        } catch (error) {
          console.error('===== addNode: failed to save =====', error);
        }
      },
      
      addDataSource: (name, description, connection) => {
        const state = get();
        const projectId = state.currentProjectId;
        if (!projectId) return;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        const nodes = projectData.nodes;
        const connections = projectData.connections;
        
        const sourceNodes = nodes.filter(n => n.type === 'system');
        const sourceIndex = sourceNodes.length;
        const y = START_Y + ROW_HEIGHT * (sourceIndex * 1.5);
        
        const newSource: FlowNodeData = {
          id: `src-${Date.now()}`,
          name,
          type: 'system',
          status: 'unconfigured',
          description,
          detail: connection,
          x: START_X,
          y,
        };
        
        const newAcq: FlowNodeData = {
          id: `acq-${Date.now()}`,
          name: '数据表',
          type: 'acquisition',
          status: 'unconfigured',
          x: START_X + COLUMN_WIDTH,
          y,
        };
        
        const newProc: FlowNodeData = {
          id: `proc-${Date.now()}`,
          name: 'DataPipeline',
          type: 'datapipeline',
          status: 'unconfigured',
          x: START_X + COLUMN_WIDTH * 2,
          y,
        };
        
        const newQual: FlowNodeData = {
          id: `qual-${Date.now()}`,
          name: '质量约束',
          type: 'quality',
          status: 'unconfigured',
          x: START_X + COLUMN_WIDTH * 3,
          y,
        };
        
        const existingDataset = nodes.find(n => n.type === 'dataset');
        let newDataset: FlowNodeData | null = null;
        let newConnections: FlowConnection[] = [
          { id: `c-${Date.now()}-1`, from: newSource.id, to: newAcq.id },
          { id: `c-${Date.now()}-2`, from: newAcq.id, to: newProc.id },
          { id: `c-${Date.now()}-3`, from: newProc.id, to: newQual.id },
        ];
        
        if (existingDataset) {
          newConnections.push({ id: `c-${Date.now()}-4`, from: newQual.id, to: existingDataset.id });
        } else {
          newDataset = {
            id: `ds-${Date.now()}`,
            name: '数据集 A',
            type: 'dataset',
            status: 'pending',
            x: START_X + COLUMN_WIDTH * 4,
            y: START_Y + ROW_HEIGHT * 1.5,
          };
          newConnections.push({ id: `c-${Date.now()}-4`, from: newQual.id, to: newDataset.id });
        }
        
        const newNodes = newDataset 
          ? [newSource, newAcq, newProc, newQual, newDataset]
          : [newSource, newAcq, newProc, newQual];
        
        set({
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              nodes: [...nodes, ...newNodes],
              connections: [...connections, ...newConnections],
            },
          },
        });
      },
      
      removeDataSource: (id) => {
        const state = get();
        const projectId = state.currentProjectId;
        if (!projectId) return;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        const nodes = projectData.nodes;
        const connections = projectData.connections;
        
        const nodesToRemove = new Set<string>([id]);
        
        nodes.forEach(node => {
          if (node.type === 'acquisition' || node.type === 'datapipeline' || node.type === 'quality') {
            const sourceId = `src-${id.split('-')[1]}`;
            if (sourceId === id) {
              nodesToRemove.add(node.id);
            }
          }
        });
        
        set({
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              nodes: nodes.filter(n => !nodesToRemove.has(n.id)),
              connections: connections.filter(c => !nodesToRemove.has(c.from) && !nodesToRemove.has(c.to)),
            },
          },
        });
      },
      
      addDataset: (name: string, sourceIds: string[]) => {
        const state = get();
        const projectId = state.currentProjectId;
        if (!projectId) return;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        
        const newDataset: FlowNodeData = {
          id: `ds-${Date.now()}`,
          name,
          type: 'dataset',
          status: 'pending',
          x: START_X + COLUMN_WIDTH * 4,
          y: START_Y + ROW_HEIGHT * 1.5,
        };
        
        set({
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              nodes: [...projectData.nodes, newDataset],
              connections: projectData.connections,
            },
          },
        });
      },
      
      addOntology: (name: string, datasetId?: string) => {
        const state = get();
        const projectId = state.currentProjectId;
        if (!projectId) return;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        const ontologyNodes = projectData.nodes.filter(n => n.type === 'ontology');
        const ontologyIndex = ontologyNodes.length;
        
        const datasetNode = projectData.nodes.find(n => n.type === 'dataset') || 
          projectData.nodes.find(n => n.type === 'quality');
        
        const newOntology: FlowNodeData = {
          id: `onto-${Date.now()}`,
          name: name || `本体库 ${ontologyIndex + 1}`,
          type: 'ontology',
          status: 'pending',
          x: START_X + COLUMN_WIDTH * 5,
          y: START_Y + ROW_HEIGHT * (ontologyIndex * 1.5),
        };
        
        const newConnections: FlowConnection[] = [];
        if (datasetNode) {
          newConnections.push({
            id: `c-${Date.now()}-onto`,
            from: datasetNode.id,
            to: newOntology.id,
          });
        }
        
        set({
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              nodes: [...projectData.nodes, newOntology],
              connections: [...projectData.connections, ...newConnections],
            },
          },
        });
      },
      
      addAnalysis: (name, type, ontologyId) => {
        const state = get();
        const projectId = state.currentProjectId;
        if (!projectId) return;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        const analysisNodes = projectData.nodes.filter(n => n.type === 'analysis');
        const analysisIndex = analysisNodes.length;
        
        const ontologyNode = ontologyId 
          ? projectData.nodes.find(n => n.id === ontologyId)
          : projectData.nodes.find(n => n.type === 'ontology');
        
        const typeLabels = {
          ontology_explore: '本体探索',
          data_analysis: '数据分析',
          root_cause: '根因分析',
        };
        
        const newAnalysis: FlowNodeData = {
          id: `ana-${Date.now()}`,
          name: name || typeLabels[type] || '分析',
          type: 'analysis',
          status: 'pending',
          detail: type,
          x: START_X + COLUMN_WIDTH * 6,
          y: START_Y + ROW_HEIGHT * (analysisIndex * 1.5),
        };
        
        const newConnections: FlowConnection[] = [];
        if (ontologyNode) {
          newConnections.push({
            id: `c-${Date.now()}-ana`,
            from: ontologyNode.id,
            to: newAnalysis.id,
          });
        }
        
        set({
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              nodes: [...projectData.nodes, newAnalysis],
              connections: [...projectData.connections, ...newConnections],
            },
          },
        });
      },
      
      removeDataset: (id) => {
        const state = get();
        const projectId = state.currentProjectId;
        if (!projectId) return;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        
        set({
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              nodes: projectData.nodes.filter(n => n.id !== id),
              connections: projectData.connections.filter(c => c.from !== id && c.to !== id),
            },
          },
        });
      },
      
      removeNode: (id) => {
        const state = get();
        const projectId = state.currentProjectId;
        if (!projectId) return;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        
        const nodesToRemove = new Set<string>([id]);
        
        if (id.startsWith('src-')) {
          const timestamp = id.split('-')[1];
          projectData.nodes.forEach(node => {
            if (node.id.startsWith('acq-') && node.id.includes(timestamp)) {
              nodesToRemove.add(node.id);
            }
            if (node.id.startsWith('proc-') && node.id.includes(timestamp)) {
              nodesToRemove.add(node.id);
            }
            if (node.id.startsWith('qual-') && node.id.includes(timestamp)) {
              nodesToRemove.add(node.id);
            }
          });
        }
        
        set({
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              nodes: projectData.nodes.filter(n => !nodesToRemove.has(n.id)),
              connections: projectData.connections.filter(c => !nodesToRemove.has(c.from) && !nodesToRemove.has(c.to)),
            },
          },
          selectedNodeId: state.selectedNodeId === id ? null : state.selectedNodeId,
          isConfigPanelOpen: state.selectedNodeId === id ? false : state.isConfigPanelOpen,
        });
      },
      
      updateNodeStatus: (id, status) => set((state) => {
        const projectId = state.currentProjectId;
        if (!projectId) return state;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        
        return {
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              nodes: projectData.nodes.map(n => 
                n.id === id ? { ...n, status } : n
              ),
            },
          },
        };
      }),
      
      updateNodeConfig: (id, config) => set((state) => {
        const projectId = state.currentProjectId;
        if (!projectId) return state;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        
        const configWithoutDisplayName = { ...config };
        const displayName = configWithoutDisplayName._displayName as string | undefined;
        delete configWithoutDisplayName._displayName;
        
        const updatedNodes = projectData.nodes.map(n => {
          if (n.id !== id) return n;
          
          const updatedNode: FlowNodeData = {
            ...n,
            config: { ...n.config, ...configWithoutDisplayName },
            status: 'configured' as NodeStatus,
          };
          
          if (displayName) {
            updatedNode.name = displayName;
            updatedNode.detail = displayName;
          }
          
          return updatedNode;
        });
        
        return {
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              nodes: updatedNodes,
            },
          },
        };
      }),
      
      updateNodePosition: (id, x, y) => set((state) => {
        const projectId = state.currentProjectId;
        if (!projectId) return state;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        
        return {
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              nodes: projectData.nodes.map(n => 
                n.id === id ? { ...n, x, y } : n
              ),
            },
          },
        };
      }),
      
      updateNodeName: (id, name) => set((state) => {
        const projectId = state.currentProjectId;
        if (!projectId) return state;

        const projectData = state.projectsData[projectId] || defaultProjectData;

        return {
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              nodes: projectData.nodes.map(n =>
                n.id === id ? { ...n, name } : n
              ),
            },
          },
        };
      }),

      updateNodeNameByOntologyId: (ontologyId, name) => set((state) => {
        const projectId = state.currentProjectId;
        if (!projectId) return state;

        const projectData = state.projectsData[projectId] || defaultProjectData;

        const updatedNodes = projectData.nodes.map(n => {
          if (n.config?.ontologyId === ontologyId) {
            return { ...n, name, detail: name };
          }
          return n;
        });

        return {
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              nodes: updatedNodes,
            },
          },
        };
      }),

      updateNodeOntologyId: (oldOntologyId, newOntologyId, newName) => set((state) => {
        const projectId = state.currentProjectId;
        if (!projectId) return state;

        const projectData = state.projectsData[projectId] || defaultProjectData;

        const updatedNodes = projectData.nodes.map(n => {
          if (n.config?.ontologyId === oldOntologyId) {
            return { ...n, name: newName, detail: newName, config: { ...n.config, ontologyId: newOntologyId } };
          }
          return n;
        });

        return {
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              nodes: updatedNodes,
            },
          },
        };
      }),

      addConnection: (from, to) => set((state) => {
        const projectId = state.currentProjectId;
        if (!projectId) return {};
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        
        const exists = projectData.connections.some(c => c.from === from && c.to === to);
        if (exists) return {};
        
        const newConnection: FlowConnection = {
          id: `conn-${Date.now()}`,
          from,
          to,
        };
        
        return {
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              connections: [...projectData.connections, newConnection],
            },
          },
        };
      }),
      
      updateProjectAutomation: (projectId, config) => set((state) => {
        const projectData = state.projectsData[projectId] || defaultProjectData;
        
        return {
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              automation: config as any,
            },
          },
        };
      }),
      
      updateProjectPermissions: (projectId, permissions) => set((state) => {
        const projectData = state.projectsData[projectId] || defaultProjectData;
        
        return {
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              permissions: permissions as any,
            },
          },
        };
      }),
    }),
    {
      name: 'rca-flow',
    }
  )
);

export const useCurrentProjectFlow = () => {
  const projectId = useFlowStore(state => state.currentProjectId);
  const projectsData = useFlowStore(state => state.projectsData);

  console.log('===== useCurrentProjectFlow =====');
  console.log('projectId:', projectId);
  console.log('projectsData:', projectsData);
  console.log('projectsData[projectId]:', projectsData[projectId]);

  if (!projectId) {
    console.log('No projectId, returning initial nodes');
    return { nodes: getInitialNodes(), connections: [] };
  }

  const projectData = projectsData[projectId];
  if (!projectData || projectData.nodes.length === 0) {
    console.log('No projectData or empty nodes, returning initial nodes');
    return { nodes: getInitialNodes(), connections: [] };
  }

  console.log('Returning projectData:', projectData);
  return projectData;
};
