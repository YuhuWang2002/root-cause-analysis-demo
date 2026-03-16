import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type NodeType = 'source' | 'acquisition' | 'process' | 'quality' | 'dataset' | 'ontology' | 'analysis';
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
  addModalType: 'source' | 'dataset' | 'ontology' | 'analysis' | null;
  
  loadProject: (projectId: string) => void;
  setSelectedNode: (id: string | null) => void;
  toggleConfigPanel: (open?: boolean) => void;
  togglePlay: () => void;
  openAddModal: (type: 'source' | 'dataset' | 'ontology' | 'analysis') => void;
  closeAddModal: () => void;
  addDataSource: (name: string, description: string, connection: string) => void;
  addOntology: (name: string, datasetId?: string) => void;
  addAnalysis: (name: string, type: 'ontology_explore' | 'data_analysis' | 'root_cause', ontologyId?: string) => void;
  removeNode: (id: string) => void;
  removeDataSource: (id: string) => void;
  addDataset: (name: string, sourceIds: string[]) => void;
  removeDataset: (id: string) => void;
  updateNodeStatus: (id: string, status: NodeStatus) => void;
  updateNodeConfig: (id: string, config: Record<string, unknown>) => void;
  updateProjectAutomation: (projectId: string, config: Record<string, unknown>) => void;
  updateProjectPermissions: (projectId: string, permissions: Record<string, unknown>) => void;
}

const COLUMN_WIDTH = 220;
const ROW_HEIGHT = 120;
const START_X = 0;
const START_Y = 60;

const getInitialNodes = () => [
  { id: 'src-1', name: '采购数据', type: 'source' as NodeType, status: 'configured' as NodeStatus, description: '企业采购管理数据库', detail: 'MySQL', x: START_X, y: START_Y },
  { id: 'src-2', name: '生产数据', type: 'source' as NodeType, status: 'configured' as NodeStatus, description: '生产制造数据库', detail: 'PostgreSQL', x: START_X, y: START_Y + ROW_HEIGHT * 1.5 },
  { id: 'src-3', name: '销售数据', type: 'source' as NodeType, status: 'configured' as NodeStatus, description: 'CRM 销售管理', detail: 'MongoDB', x: START_X, y: START_Y + ROW_HEIGHT * 3 },
  
  { id: 'acq-1', name: '数据表 1', type: 'acquisition' as NodeType, status: 'configured' as NodeStatus, x: START_X + COLUMN_WIDTH, y: START_Y },
  { id: 'acq-2', name: '数据表 2', type: 'acquisition' as NodeType, status: 'configured' as NodeStatus, x: START_X + COLUMN_WIDTH, y: START_Y + ROW_HEIGHT * 1.5 },
  { id: 'acq-3', name: '数据表 3', type: 'acquisition' as NodeType, status: 'configured' as NodeStatus, x: START_X + COLUMN_WIDTH, y: START_Y + ROW_HEIGHT * 3 },
  
  { id: 'proc-1', name: '数据转换', type: 'process' as NodeType, status: 'configured' as NodeStatus, x: START_X + COLUMN_WIDTH * 2, y: START_Y },
  { id: 'proc-2', name: '数据转换', type: 'process' as NodeType, status: 'configured' as NodeStatus, x: START_X + COLUMN_WIDTH * 2, y: START_Y + ROW_HEIGHT * 1.5 },
  { id: 'proc-3', name: '数据转换', type: 'process' as NodeType, status: 'configured' as NodeStatus, x: START_X + COLUMN_WIDTH * 2, y: START_Y + ROW_HEIGHT * 3 },
  
  { id: 'qual-1', name: '质量约束', type: 'quality' as NodeType, status: 'configured' as NodeStatus, x: START_X + COLUMN_WIDTH * 3, y: START_Y },
  { id: 'qual-2', name: '质量约束', type: 'quality' as NodeType, status: 'configured' as NodeStatus, x: START_X + COLUMN_WIDTH * 3, y: START_Y + ROW_HEIGHT * 1.5 },
  { id: 'qual-3', name: '质量约束', type: 'quality' as NodeType, status: 'configured' as NodeStatus, x: START_X + COLUMN_WIDTH * 3, y: START_Y + ROW_HEIGHT * 3 },
  
  { id: 'ds-1', name: '数据集 A', type: 'dataset' as NodeType, status: 'pending' as NodeStatus, description: '汇总数据集', x: START_X + COLUMN_WIDTH * 4, y: START_Y + ROW_HEIGHT * 1.5 },
  
  { id: 'onto-1', name: '本体库 A', type: 'ontology' as NodeType, status: 'pending' as NodeStatus, x: START_X + COLUMN_WIDTH * 5, y: START_Y + ROW_HEIGHT * 1.5 },
  
  { id: 'ana-1', name: '本体探索', type: 'analysis' as NodeType, status: 'pending' as NodeStatus, x: START_X + COLUMN_WIDTH * 6, y: START_Y },
  { id: 'ana-2', name: '数据分析', type: 'analysis' as NodeType, status: 'pending' as NodeStatus, x: START_X + COLUMN_WIDTH * 6, y: START_Y + ROW_HEIGHT * 1.5 },
  { id: 'ana-3', name: '根因分析', type: 'analysis' as NodeType, status: 'pending' as NodeStatus, x: START_X + COLUMN_WIDTH * 6, y: START_Y + ROW_HEIGHT * 3 },
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

      loadProject: (projectId: string) => {
        const state = get();
        const projectData = state.projectsData[projectId];
        
        if (projectData) {
          set({ currentProjectId: projectId });
        } else {
          set({
            currentProjectId: projectId,
            projectsData: {
              ...state.projectsData,
              [projectId]: { nodes: [], connections: [] },
            },
          });
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
      
      addDataSource: (name, description, connection) => {
        const state = get();
        const projectId = state.currentProjectId;
        if (!projectId) return;
        
        const projectData = state.projectsData[projectId] || defaultProjectData;
        const nodes = projectData.nodes;
        const connections = projectData.connections;
        
        const sourceNodes = nodes.filter(n => n.type === 'source');
        const sourceIndex = sourceNodes.length;
        const y = START_Y + ROW_HEIGHT * (sourceIndex * 1.5);
        
        const newSource: FlowNodeData = {
          id: `src-${Date.now()}`,
          name,
          type: 'source',
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
          name: '数据转换',
          type: 'process',
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
          if (node.type === 'acquisition' || node.type === 'process' || node.type === 'quality') {
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
        
        return {
          projectsData: {
            ...state.projectsData,
            [projectId]: {
              ...projectData,
              nodes: projectData.nodes.map(n => 
                n.id === id ? { ...n, config: { ...n.config, ...config }, status: 'configured' as NodeStatus } : n
              ),
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
  
  if (!projectId) {
    return { nodes: [], connections: [] };
  }
  
  return projectsData[projectId] || { nodes: [], connections: [] };
};
