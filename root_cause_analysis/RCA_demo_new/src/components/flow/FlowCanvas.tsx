import { useCallback, useMemo, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ReactFlow,
  Background,
  Controls,
  addEdge,
  useNodesState,
  useEdgesState,
  useReactFlow,
  Connection,
  Edge,
  Node,
  NodeTypes,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCurrentProjectFlow, useFlowStore, type NodeType, type NodeStatus } from '@/stores/flowStore';

const typeColors: Record<NodeType, { bg: string; border: string; text: string }> = {
  system: { bg: '#8B5CF6', border: '#A78BFA', text: '#C4B5FD' },
  acquisition: { bg: '#3B82F6', border: '#60A5FA', text: '#93C5FD' },
  datapipeline: { bg: '#06B6D4', border: '#22D3EE', text: '#67E8F9' },
  quality: { bg: '#F59E0B', border: '#FBBF24', text: '#FCD34D' },
  dataset: { bg: '#10B981', border: '#34D399', text: '#6EE7B7' },
  ontology: { bg: '#EC4899', border: '#F472B6', text: '#F9A8D4' },
  ontologyExplore: { bg: '#F472B6', border: '#F9A8D4', text: '#FECDD3' },
  analysis: { bg: '#EF4444', border: '#F87171', text: '#FCA5A5' },
  rootCause: { bg: '#7C3AED', border: '#A78BFA', text: '#C4B5FD' },
};

function CustomNode({ data, selected }: { data: { label: string; type: NodeType; status: NodeStatus; detail?: string; config?: Record<string, unknown> }; selected?: boolean }) {
  const colors = typeColors[data.type] || typeColors.system;
  const isConfigured = data.status === 'configured' || data.status === 'completed';
  
  const getSystemLabel = () => {
    if (data.type === 'system' && data.config?._displayName) {
      return data.config._displayName as string;
    }
    if (data.type === 'system' && data.detail) {
      return data.detail as string;
    }
    return data.label;
  };
  
  return (
    <div
      className="w-24 h-24 rounded-xl border-2 flex flex-col items-center justify-center shadow-lg cursor-pointer"
      style={{
        backgroundColor: colors.bg,
        borderColor: selected ? '#FFFFFF' : colors.border,
        borderWidth: selected ? '3px' : '2px',
        boxShadow: selected ? `0 0 15px ${colors.bg}` : 'none',
      }}
    >
      <Handle type="target" position={Position.Left} className="!bg-gray-400 !w-3 !h-3" />
      {data.type === 'system' && (
        <svg className="w-6 h-6 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>
      )}
      {data.type === 'acquisition' && (
        <svg className="w-6 h-6 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      )}
      {data.type === 'datapipeline' && (
        <svg className="w-6 h-6 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
      )}
      {data.type === 'dataset' && (
        <svg className="w-6 h-6 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
        </svg>
      )}
      {data.type === 'ontology' && (
        <svg className="w-6 h-6 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
        </svg>
      )}
      {data.type === 'ontologyExplore' && (
        <svg className="w-6 h-6 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      )}
      {data.type === 'analysis' && (
        <svg className="w-6 h-6 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      )}
      {data.type === 'quality' && (
        <svg className="w-6 h-6 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )}
      {data.type === 'rootCause' && (
        <svg className="w-6 h-6 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      )}
      <span className="text-white text-[10px] font-medium truncate max-w-[70px] text-center">
        {data.type === 'system' ? getSystemLabel() : data.label}
      </span>
      <div 
        className={`mt-1 px-2 py-0.5 rounded text-[8px] font-medium ${isConfigured ? 'bg-green-500/80 text-white' : 'bg-yellow-500/80 text-white'}`}
      >
        {isConfigured ? '已配置' : '未配置'}
      </div>
      <Handle type="source" position={Position.Right} className="!bg-gray-400 !w-3 !h-3" />
    </div>
  );
}

const nodeTypes: NodeTypes = {
  custom: CustomNode,
};

interface FlowCanvasProps {
  onAddSource: () => void;
  onAddOntology: () => void;
  onAddAnalysis: () => void;
}

export default function FlowCanvas({ onAddSource, onAddOntology, onAddAnalysis }: FlowCanvasProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();
  const navigate = useNavigate();
  
  const { nodes: storeNodes, connections: storeConnections } = useCurrentProjectFlow();
  const { currentProjectId, setSelectedNode, addNode, updateNodePosition, addConnection: storeAddConnection } = useFlowStore();

  const initialNodes: Node[] = useMemo(() => {
    return storeNodes.map((node, index) => ({
      id: node.id,
      type: 'custom',
      position: { x: node.x, y: node.y },
      data: { 
        label: node.name, 
        type: node.type, 
        status: node.status,
        detail: node.detail,
      },
      zIndex: 10 + index,
    }));
  }, [storeNodes]);

  const initialEdges: Edge[] = useMemo(() => {
    return storeConnections.map(conn => ({
      id: conn.id,
      source: conn.from,
      target: conn.to,
      type: 'smoothstep',
      animated: true,
      style: { stroke: '#6B7280', strokeWidth: 2 },
      markerEnd: {
        type: 'arrowclosed' as const,
        color: '#6B7280',
      },
    }));
  }, [storeConnections]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    console.log('===== FlowCanvas initialNodes changed =====');
    console.log('initialNodes:', initialNodes);
    console.log('initialNodes.length:', initialNodes?.length);
    setNodes(initialNodes);
  }, [initialNodes, setNodes]);

  const onConnect = useCallback(
    (params: Connection) => {
      if (params.source && params.target) {
        storeAddConnection(params.source, params.target);
        setEdges((eds) => addEdge({ ...params, type: 'smoothstep', animated: true }, eds));
      }
    },
    [setEdges, storeAddConnection]
  );

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const nodeData = storeNodes.find(n => n.id === node.id);
      const config = nodeData?.config as Record<string, unknown> | undefined;
      const originalType = node.data?.type as string | undefined;

      // 如果是本体库节点，直接跳转到本体配置页面
      if (originalType === 'ontology') {
        if (config?.ontologyId) {
          navigate(`/ontology/${currentProjectId}/${config.ontologyId}`);
        } else {
          navigate(`/ontology/${currentProjectId}`);
        }
        return;
      }

      setSelectedNode(node.id);
    },
    [setSelectedNode, navigate, storeNodes, currentProjectId]
  );

  const onNodeDragStop = useCallback(
    (_: React.MouseEvent, node: Node) => {
      updateNodePosition(node.id, node.position.x, node.position.y);
    },
    [updateNodePosition]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    async (event: React.DragEvent) => {
      event.preventDefault();

      let nodeType = event.dataTransfer.getData('application/reactflow') as NodeType;
      if (!nodeType) {
        nodeType = event.dataTransfer.getData('text/plain') as NodeType;
      }

      if (!nodeType || !wrapperRef.current) return;

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      await addNode(nodeType, position.x, position.y);
    },
    [screenToFlowPosition, addNode]
  );

  return (
    <div className="w-full h-full" ref={wrapperRef}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onNodeDragStop={onNodeDragStop}
        onDragOver={onDragOver}
        onDrop={onDrop}
        nodeTypes={nodeTypes}
        fitView
        className="bg-gray-900"
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: true,
        }}
        proOptions={{ hideAttribution: true }}
        minZoom={0.1}
        maxZoom={2}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
      >
        <Background color="#374151" gap={20} />
        <Controls className="!bg-gray-800 !border-gray-700" />
      </ReactFlow>
    </div>
  );
}
