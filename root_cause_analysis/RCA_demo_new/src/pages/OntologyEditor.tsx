import { useCallback, useEffect, useMemo, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeChange,
  Node,
} from '@xyflow/react';
import dagre from 'dagre';
import '@xyflow/react/dist/style.css';
import * as api from '@/services/api';
import { useFlowStore } from '@/stores/flowStore';

interface OntologyClass {
  id: number;
  ontology_id: number;
  name: string;
  description: string;
  properties: Array<{
    id: number;
    name: string;
    type: string;
    description: string;
  }>;
}

interface OntologyRelation {
  id: number;
  ontology_id: number;
  source_class_id: number;
  target_class_id: number;
  relation_type: string;
  description: string;
  source_class_name?: string;
  target_class_name?: string;
}

interface Ontology {
  id: number;
  project_id: string;
  name: string;
  description: string;
  canvas_data: any[];
  classes: OntologyClass[];
  relations: OntologyRelation[];
}

export default function OntologyEditor() {
  const { projectId, ontologyId } = useParams<{ projectId: string; ontologyId?: string }>();
  const navigate = useNavigate();
  const { updateNodeOntologyId } = useFlowStore();

  const [ontologies, setOntologies] = useState<Ontology[]>([]);
  const [currentOntology, setCurrentOntology] = useState<Ontology | null>(null);
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddClassModalOpen, setIsAddClassModalOpen] = useState(false);
  const [newClassName, setNewClassName] = useState('');
  const [newClassDescription, setNewClassDescription] = useState('');

  const [isAddRelationModalOpen, setIsAddRelationModalOpen] = useState(false);
  const [newRelationSourceClassId, setNewRelationSourceClassId] = useState<number | null>(null);
  const [newRelationTargetClassId, setNewRelationTargetClassId] = useState<number | null>(null);
  const [newRelationName, setNewRelationName] = useState('');
  const [newRelationType, setNewRelationType] = useState('1:1');

  const [isAddPropertyModalOpen, setIsAddPropertyModalOpen] = useState(false);
  const [newPropertyName, setNewPropertyName] = useState('');
  const [newPropertyType, setNewPropertyType] = useState('string');
  const [newPropertyDescription, setNewPropertyDescription] = useState('');

  const [showLayoutMenu, setShowLayoutMenu] = useState(false);
  const lastOntologyIdRef = useRef<number | null>(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!currentOntology) return;

    if (lastOntologyIdRef.current === currentOntology.id && nodes.length > 0) {
      const selectedNodeIndex = nodes.findIndex((n: any) => n.selected);
      if (selectedNodeIndex !== -1) {
        const updatedNodes = nodes.map((n: any) => ({
          ...n,
          selected: String(n.id) === String(selectedClassId),
        }));
        setNodes(updatedNodes as any);
      }
      return;
    }

    lastOntologyIdRef.current = currentOntology.id;

    const classIds = new Set(currentOntology.classes.map(c => String(c.id)));
    const canvasNodeIds = new Set(currentOntology.canvas_data?.map((n: any) => n.id) || []);
    const isCanvasOutdated = currentOntology.canvas_data?.some((n: any) => !classIds.has(n.id)) ||
                            currentOntology.classes.some(c => !canvasNodeIds.has(String(c.id)));

    let nodesToSet;
    if (currentOntology.canvas_data && currentOntology.canvas_data.length > 0 && !isCanvasOutdated) {
      nodesToSet = currentOntology.canvas_data.map((node: any) => ({
        ...node,
        selected: node.id === String(selectedClassId),
      }));
    } else {
      nodesToSet = currentOntology.classes.map((cls, idx) => ({
        id: String(cls.id),
        position: { x: 100 + (idx % 4) * 200, y: 100 + Math.floor(idx / 4) * 120 },
        data: { label: cls.name },
        style: {
          background: '#fff',
          border: '2px solid #1a192b',
          borderRadius: '12px',
          padding: '16px 24px',
          minWidth: '140px',
          textAlign: 'center',
          fontSize: '14px',
          fontWeight: 500,
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        },
        selected: cls.id === selectedClassId,
      }));
    }

    const edgesToSet = currentOntology.relations.map((rel) => ({
      id: String(rel.id),
      source: String(rel.source_class_id),
      target: String(rel.target_class_id),
      label: rel.relation_type,
      type: 'smoothstep',
      animated: true,
      style: { stroke: '#6366f1', strokeWidth: 2 },
      labelStyle: { fill: '#6366f1', fontWeight: 500 },
      labelBgStyle: { fill: '#fff', fillOpacity: 0.9 },
    }));

    setNodes(nodesToSet as any);
    setEdges(edgesToSet as any);
  }, [currentOntology, selectedClassId, setNodes, setEdges]);

  useEffect(() => {
    loadOntologies();
  }, [projectId]);

  useEffect(() => {
    if (ontologyId && ontologies.length > 0) {
      const ontoId = parseInt(ontologyId);
      const onto = ontologies.find(o => o.id === ontoId);
      if (onto && onto.id !== currentOntology?.id) {
        console.log('Setting current ontology from URL:', onto);
        setCurrentOntology(onto);
        loadOntologyDetail(ontoId);
      }
    }
  }, [ontologyId, ontologies]);

  const loadOntologies = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      let data = await api.getOntologies(projectId);
      console.log('Loaded ontologies:', data);

      if (data.length === 0) {
        console.log('No ontologies found, creating default ontology...');
        const newOntology = await api.createOntology(projectId, {
          name: '默认本体库',
          description: '项目默认本体库'
        });
        data = [newOntology];
        console.log('Created default ontology:', newOntology);
      }

      setOntologies(data);

      if (ontologyId) {
        const ontoId = parseInt(ontologyId);
        const onto = data.find(o => o.id === ontoId);
        if (onto) {
          console.log('Found ontology in URL:', onto);
          setCurrentOntology(onto);
          await loadOntologyDetail(ontoId);
        } else {
          console.log('Ontology not found in list, navigating to first');
          const first = data[0];
          navigate(`/ontology/${projectId}/${first.id}`, { replace: true });
        }
      } else {
        console.log('No ontologyId in URL, navigating to first:', data[0].id);
        navigate(`/ontology/${projectId}/${data[0].id}`, { replace: true });
      }
    } catch (error) {
      console.error('Failed to load ontologies:', error);
    }
    setIsLoading(false);
  };

  const loadOntologyDetail = async (id: number) => {
    if (!projectId) return;
    try {
      const data = await api.getOntology(projectId, id);
      setCurrentOntology(data);
      navigate(`/ontology/${projectId}/${id}`);
    } catch (error) {
      console.error('Failed to load ontology:', error);
    }
  };

  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      onNodesChange(changes);
      const newNodes = nodes.map((n) => ({
        id: n.id,
        position: n.position,
        data: n.data,
        type: n.type,
        style: n.style,
      }));
      if (projectId && currentOntology) {
        api.saveOntologyCanvas(projectId, currentOntology.id, newNodes);
      }
    },
    [nodes, onNodesChange, projectId, currentOntology]
  );

  const handleConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const handleNodeClick = useCallback((_: React.MouseEvent, node: any) => {
    setSelectedClassId(parseInt(node.id));
    setIsRightPanelOpen(true);
  }, []);

  const applyLayout = useCallback((layoutType: 'TB' | 'LR' | 'RL' | 'radial') => {
    if (layoutType === 'radial') {
      const centerX = 400;
      const centerY = 300;
      const radius = 200;

      const newNodes = nodes.map((node: any, index: number) => {
        const angle = (2 * Math.PI * index) / nodes.length;
        return {
          ...node,
          position: {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle),
          },
        };
      });

      setNodes(newNodes as any);
    } else {
      const dagreGraph = new dagre.graphlib.Graph();
      dagreGraph.setDefaultEdgeLabel(() => ({}));

      const nodeWidth = 172;
      const nodeHeight = 50;

      dagreGraph.setGraph({
        rankdir: layoutType,
        nodesep: 80,
        ranksep: 120,
        marginx: 50,
        marginy: 50,
      });

      nodes.forEach((node: any) => {
        dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
      });

      edges.forEach((edge: any) => {
        dagreGraph.setEdge(edge.source, edge.target);
      });

      dagre.layout(dagreGraph);

      const newNodes = nodes.map((node: any) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        return {
          ...node,
          position: {
            x: nodeWithPosition.x - nodeWidth / 2,
            y: nodeWithPosition.y - nodeHeight / 2,
          },
        };
      });

      setNodes(newNodes as any);
    }
  }, [nodes, setNodes]);

  const handleOpenAddClassModal = () => {
    setNewClassName('');
    setNewClassDescription('');
    setIsAddClassModalOpen(true);
  };

  const handleAddClass = async () => {
    console.log('===== handleAddClass CALLED =====');
    console.log('newClassName:', newClassName);
    console.log('projectId:', projectId);
    console.log('ontologyId:', ontologyId);
    console.log('currentOntology:', currentOntology);
    console.log('ontologies:', ontologies);
    
    if (!newClassName.trim()) {
      alert('请输入类名称');
      return;
    }
    if (!projectId) {
      console.log('Error: projectId is missing');
      return;
    }
    
    let targetOntologyId: number | null = null;
    
    if (ontologyId) {
      const parsed = parseInt(ontologyId);
      if (!isNaN(parsed)) {
        targetOntologyId = parsed;
      }
    }
    
    if (!targetOntologyId && currentOntology) {
      targetOntologyId = currentOntology.id;
    }
    
    if (!targetOntologyId && ontologies.length > 0) {
      targetOntologyId = ontologies[0].id;
    }
    
    if (!targetOntologyId) {
      console.log('Error: Could not determine ontology ID');
      alert('无法确定本体库 ID，请刷新页面重试');
      return;
    }
    
    try {
      console.log('Calling API with ontologyId:', targetOntologyId);
      await api.createOntologyClass(projectId, targetOntologyId, { 
        name: newClassName.trim(), 
        description: newClassDescription 
      });
      console.log('API call successful');
      setIsAddClassModalOpen(false);
      loadOntologyDetail(targetOntologyId);
    } catch (error) {
      console.error('Failed to add class:', error);
      alert('添加类失败: ' + (error as Error).message);
    }
  };

  const handleDeleteClass = async (classId: number) => {
    if (!projectId || !currentOntology || !confirm('确定要删除此类吗？')) return;
    try {
      await api.deleteOntologyClass(projectId, currentOntology.id, classId);
      setSelectedClassId(null);
      setIsRightPanelOpen(false);
      loadOntologyDetail(currentOntology.id);
    } catch (error) {
      console.error('Failed to delete class:', error);
    }
  };

  const handleOpenAddPropertyModal = () => {
    if (!selectedClassId) {
      alert('请先选择一个类');
      return;
    }
    setNewPropertyName('');
    setNewPropertyType('string');
    setNewPropertyDescription('');
    setIsAddPropertyModalOpen(true);
  };

  const handleAddProperty = async () => {
    console.log('===== handleAddProperty CALLED =====');
    console.log('projectId:', projectId);
    console.log('currentOntology:', currentOntology);
    console.log('selectedClassId:', selectedClassId);
    console.log('newPropertyName:', newPropertyName);
    console.log('newPropertyType:', newPropertyType);
    console.log('newPropertyDescription:', newPropertyDescription);

    if (!projectId) {
      console.log('Error: projectId is missing');
      return;
    }

    let targetOntologyId: number | null = null;

    if (ontologyId) {
      const parsed = parseInt(ontologyId);
      if (!isNaN(parsed)) {
        targetOntologyId = parsed;
      }
    }

    if (!targetOntologyId && currentOntology) {
      targetOntologyId = currentOntology.id;
    }

    if (!targetOntologyId && ontologies.length > 0) {
      targetOntologyId = ontologies[0].id;
    }

    if (!targetOntologyId) {
      console.log('Error: Could not determine ontology ID');
      alert('无法确定本体库 ID');
      return;
    }

    if (!selectedClassId) {
      alert('请先选择一个类');
      return;
    }

    if (!newPropertyName.trim()) {
      alert('请输入属性名称');
      return;
    }

    try {
      console.log('Calling API to add property...');
      await api.addClassProperty(projectId, targetOntologyId, selectedClassId, {
        name: newPropertyName.trim(),
        type: newPropertyType,
        description: newPropertyDescription.trim()
      });
      console.log('API call successful');
      setIsAddPropertyModalOpen(false);
      loadOntologyDetail(targetOntologyId);
    } catch (error) {
      console.error('Failed to add property:', error);
      alert('添加属性失败: ' + (error as Error).message);
    }
  };

  const handleDeleteProperty = async (propId: number) => {
    if (!projectId || !currentOntology || !selectedClassId || !confirm('确定要删除此属性吗？')) return;
    try {
      await api.deleteClassProperty(projectId, currentOntology.id, selectedClassId, propId);
      loadOntologyDetail(currentOntology.id);
    } catch (error) {
      console.error('Failed to delete property:', error);
    }
  };

  const handleOpenAddRelationModal = () => {
    if (currentOntology && currentOntology.classes.length < 2) {
      alert('需要至少两个类才能创建关系');
      return;
    }
    setNewRelationSourceClassId(currentOntology?.classes[0]?.id || null);
    setNewRelationTargetClassId(currentOntology?.classes.length > 1 ? currentOntology.classes[1].id : null);
    setNewRelationName('');
    setNewRelationType('1:1');
    setIsAddRelationModalOpen(true);
  };

  const handleAddRelation = async () => {
    console.log('===== handleAddRelation CALLED =====');
    console.log('projectId:', projectId);
    console.log('currentOntology:', currentOntology);
    console.log('newRelationSourceClassId:', newRelationSourceClassId);
    console.log('newRelationTargetClassId:', newRelationTargetClassId);
    console.log('newRelationName:', newRelationName);
    console.log('newRelationType:', newRelationType);

    if (!projectId) {
      console.log('Error: projectId is missing');
      return;
    }

    let targetOntologyId: number | null = null;

    if (ontologyId) {
      const parsed = parseInt(ontologyId);
      if (!isNaN(parsed)) {
        targetOntologyId = parsed;
      }
    }

    if (!targetOntologyId && currentOntology) {
      targetOntologyId = currentOntology.id;
    }

    if (!targetOntologyId && ontologies.length > 0) {
      targetOntologyId = ontologies[0].id;
    }

    if (!targetOntologyId) {
      console.log('Error: Could not determine ontology ID');
      alert('无法确定本体库 ID');
      return;
    }

    if (!newRelationSourceClassId || !newRelationTargetClassId) {
      alert('请选择源类和目标类');
      return;
    }

    if (!newRelationName.trim()) {
      alert('请输入关系名称');
      return;
    }

    try {
      console.log('Calling API to create relation...');
      await api.createOntologyRelation(projectId, targetOntologyId, {
        source_class_id: newRelationSourceClassId,
        target_class_id: newRelationTargetClassId,
        relation_type: `${newRelationName} (${newRelationType})`,
      });
      console.log('API call successful');
      setIsAddRelationModalOpen(false);
      loadOntologyDetail(targetOntologyId);
    } catch (error) {
      console.error('Failed to add relation:', error);
      alert('添加关系失败: ' + (error as Error).message);
    }
  };

  const handleDeleteRelation = async (relationId: number) => {
    if (!projectId || !currentOntology || !confirm('确定要删除此关系吗？')) return;
    try {
      await api.deleteOntologyRelation(projectId, currentOntology.id, relationId);
      loadOntologyDetail(currentOntology.id);
    } catch (error) {
      console.error('Failed to delete relation:', error);
    }
  };

  const selectedClass = currentOntology?.classes.find(c => c.id === selectedClassId);

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Add Class Modal */}
      {isAddClassModalOpen && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={(e) => {
            console.log('Background clicked, closing modal');
            setIsAddClassModalOpen(false);
          }}
        >
          <div 
            className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 transform transition-all"
            onClick={(e) => {
              console.log('Modal content clicked, stopping propagation');
              e.stopPropagation();
            }}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">添加新类</h3>
              <button
                onClick={() => setIsAddClassModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">类名称</label>
                <input
                  type="text"
                  value={newClassName}
                  onChange={(e) => setNewClassName(e.target.value)}
                  placeholder="请输入类名称"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">描述（可选）</label>
                <textarea
                  value={newClassDescription}
                  onChange={(e) => setNewClassDescription(e.target.value)}
                  placeholder="请输入类描述"
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  console.log('Cancel button clicked');
                  setIsAddClassModalOpen(false);
                }}
                className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
                type="button"
              >
                取消
              </button>
              <button
                onClick={(e) => {
                  console.log('===== ADD BUTTON CLICKED =====');
                  e.preventDefault();
                  e.stopPropagation();
                  handleAddClass();
                }}
                className="flex-1 px-4 py-3 bg-primary text-white rounded-xl hover:bg-primary-dark transition-colors cursor-pointer active:scale-95"
                type="button"
                style={{ pointerEvents: 'auto' }}
              >
                添加
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Relation Modal */}
      {isAddRelationModalOpen && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setIsAddRelationModalOpen(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 transform transition-all"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">添加新关系</h3>
              <button
                onClick={() => setIsAddRelationModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">源类</label>
                <select
                  value={newRelationSourceClassId || ''}
                  onChange={(e) => setNewRelationSourceClassId(e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                >
                  <option value="">选择源类</option>
                  {currentOntology?.classes.map(cls => (
                    <option key={cls.id} value={cls.id}>{cls.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">目标类</label>
                <select
                  value={newRelationTargetClassId || ''}
                  onChange={(e) => setNewRelationTargetClassId(e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                >
                  <option value="">选择目标类</option>
                  {currentOntology?.classes.map(cls => (
                    <option key={cls.id} value={cls.id}>{cls.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">关系名称</label>
                <input
                  type="text"
                  value={newRelationName}
                  onChange={(e) => setNewRelationName(e.target.value)}
                  placeholder="例如：包含、属于、继承"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">关系类型</label>
                <select
                  value={newRelationType}
                  onChange={(e) => setNewRelationType(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                >
                  <option value="1:1">1 对 1</option>
                  <option value="1:n">1 对 N</option>
                  <option value="n:m">N 对 M</option>
                </select>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setIsAddRelationModalOpen(false)}
                className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
                type="button"
              >
                取消
              </button>
              <button
                onClick={() => handleAddRelation()}
                className="flex-1 px-4 py-3 bg-primary text-white rounded-xl hover:bg-primary-dark transition-colors cursor-pointer active:scale-95"
                type="button"
              >
                添加
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Property Modal */}
      {isAddPropertyModalOpen && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setIsAddPropertyModalOpen(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 transform transition-all"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">添加属性</h3>
              <button
                onClick={() => setIsAddPropertyModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">属性名称</label>
                <input
                  type="text"
                  value={newPropertyName}
                  onChange={(e) => setNewPropertyName(e.target.value)}
                  placeholder="例如：名称、年龄、地址"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">属性类型</label>
                <select
                  value={newPropertyType}
                  onChange={(e) => setNewPropertyType(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                >
                  <option value="string">字符串 (string)</option>
                  <option value="number">数字 (number)</option>
                  <option value="boolean">布尔值 (boolean)</option>
                  <option value="date">日期 (date)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">描述（可选）</label>
                <textarea
                  value={newPropertyDescription}
                  onChange={(e) => setNewPropertyDescription(e.target.value)}
                  placeholder="请输入属性描述"
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setIsAddPropertyModalOpen(false)}
                className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
                type="button"
              >
                取消
              </button>
              <button
                onClick={() => handleAddProperty()}
                className="flex-1 px-4 py-3 bg-primary text-white rounded-xl hover:bg-primary-dark transition-colors cursor-pointer active:scale-95"
                type="button"
              >
                添加
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="h-14 bg-white border-b flex items-center px-6 justify-between shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={() => {
              console.log('===== 返回项目按钮 clicked =====');
              console.log('projectId:', projectId);
              console.log('currentOntology:', currentOntology);
              console.log('ontologies:', ontologies);
              console.log('navigating to:', `/flow/${projectId}`);
              navigate(`/flow/${projectId}`);
            }}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            返回项目
          </button>
          <div className="h-6 w-px bg-gray-200" />
          <h1 className="text-lg font-semibold text-gray-900">本体库配置</h1>
          {currentOntology && (
            <button
              onClick={() => {
                const newName = prompt('请输入本体库名称:', currentOntology.name);
                if (newName && newName.trim() && projectId) {
                  updateNodeOntologyId(currentOntology.id, currentOntology.id, newName.trim());
                  api.updateOntology(projectId, currentOntology.id, { name: newName.trim() })
                    .then(() => {
                      const { nodes, connections } = useFlowStore.getState().projectsData[projectId] || { nodes: [], connections: [] };
                      return api.saveCanvas(projectId, { nodes, connections });
                    })
                    .then(() => {
                      loadOntologies();
                    })
                    .catch(err => console.error('Failed to update ontology name:', err));
                }
              }}
              className="p-1 hover:bg-gray-200 rounded transition-colors"
              title="修改本体库名称"
            >
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
          )}
        </div>
        <div className="flex items-center gap-3">
          <select
            value={currentOntology?.id || ''}
            onChange={(e) => {
              const selectedId = parseInt(e.target.value);
              const selectedOntology = ontologies.find(o => o.id === selectedId);
              if (selectedId && selectedOntology && currentOntology) {
                console.log('===== Switching ontology =====');
                console.log('old ontologyId:', currentOntology.id);
                console.log('new ontologyId:', selectedId);
                console.log('new ontology name:', selectedOntology.name);
                updateNodeOntologyId(currentOntology.id, selectedId, selectedOntology.name);
                const { nodes, connections } = useFlowStore.getState().projectsData[projectId] || { nodes: [], connections: [] };
                api.saveCanvas(projectId, { nodes, connections }).catch(err => console.error('Failed to save canvas:', err));
                loadOntologyDetail(selectedId);
              }
            }}
            className="px-4 py-2 border rounded-lg bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary/20 border-gray-300"
          >
            <option value="">选择本体库</option>
            {ontologies.map(o => (
              <option key={o.id} value={o.id}>{o.name}</option>
            ))}
          </select>
          <button
            onClick={loadOntologies}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
            title="刷新"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          {currentOntology && ontologies.length > 1 && (
            <button
              onClick={() => {
                if (confirm(`确定要删除本体库"${currentOntology.name}"吗？此操作不可恢复。`)) {
                  api.deleteOntology(projectId, currentOntology.id)
                    .then(() => {
                      const remainingOntologies = ontologies.filter(o => o.id !== currentOntology.id);
                      if (remainingOntologies.length > 0) {
                        loadOntologyDetail(remainingOntologies[0].id);
                      }
                      loadOntologies();
                    })
                    .catch(err => {
                      console.error('Failed to delete ontology:', err);
                      alert('删除失败: ' + (err as Error).message);
                    });
                }
              }}
              className="px-4 py-2 text-red-600 hover:text-red-900 transition-colors"
              title="删除本体库"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Classes & Relations */}
        <div className="w-72 bg-white border-r flex flex-col shrink-0">
          {/* Classes */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="p-4 border-b flex items-center justify-between">
              <h2 className="font-semibold text-gray-900">类列表</h2>
              <button
                onClick={handleOpenAddClassModal}
                className="text-sm px-3 py-1 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
              >
                + 添加
              </button>
            </div>
            <div className="flex-1 overflow-auto p-3 space-y-2">
              {currentOntology?.classes.map(cls => (
                <div
                  key={cls.id}
                  onClick={() => { setSelectedClassId(cls.id); setIsRightPanelOpen(true); }}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedClassId === cls.id
                      ? 'border-primary bg-primary/5 shadow-sm'
                      : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                  }`}
                >
                  <div className="font-medium text-gray-900">{cls.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{cls.properties.length} 个属性</div>
                </div>
              ))}
              {currentOntology?.classes.length === 0 && (
                <div className="text-center text-gray-400 py-8">暂无类，请添加</div>
              )}
            </div>
          </div>

          {/* Relations */}
          <div className="h-1/3 border-t flex flex-col">
            <div className="p-4 border-b flex items-center justify-between">
              <h2 className="font-semibold text-gray-900">关系列表</h2>
              <button
                onClick={handleOpenAddRelationModal}
                className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                + 添加
              </button>
            </div>
            <div className="flex-1 overflow-auto p-3 space-y-2">
              {currentOntology?.relations.map(rel => (
                <div
                  key={rel.id}
                  className="p-2 rounded-lg border border-gray-200 bg-gray-50 flex items-center justify-between"
                >
                  <div className="text-sm">
                    <span className="text-gray-900">{rel.source_class_name}</span>
                    <span className="mx-2 text-gray-400">→</span>
                    <span className="text-gray-900">{rel.relation_type}</span>
                    <span className="mx-2 text-gray-400">→</span>
                    <span className="text-gray-900">{rel.target_class_name}</span>
                  </div>
                  <button
                    onClick={() => handleDeleteRelation(rel.id)}
                    className="text-red-500 hover:text-red-700 text-xs"
                  >
                    删除
                  </button>
                </div>
              ))}
              {currentOntology?.relations.length === 0 && (
                <div className="text-center text-gray-400 py-4">暂无关系</div>
              )}
            </div>
          </div>
        </div>

        {/* Middle - Canvas */}
        <div className="flex-1 bg-gray-100">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={handleNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={handleConnect}
            onNodeClick={handleNodeClick}
            fitView
            className="bg-gray-100"
          >
            <Background gap={20} color="#e5e7eb" />
            <Controls className="bg-white rounded-lg shadow-md border" />
            <div className="absolute top-4 right-4 z-10">
              <div className="relative">
                <button
                  onClick={() => setShowLayoutMenu(!showLayoutMenu)}
                  className="px-4 py-2 bg-white text-gray-700 rounded-lg shadow-md border hover:bg-gray-50 transition-colors flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5h16M4 12h16M4 19h16" />
                  </svg>
                  布局
                </button>
                {showLayoutMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border overflow-hidden">
                    <button
                      onClick={() => {
                        applyLayout('LR');
                        setShowLayoutMenu(false);
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors"
                    >
                      从左到右
                    </button>
                    <button
                      onClick={() => {
                        applyLayout('TB');
                        setShowLayoutMenu(false);
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors"
                    >
                      从上到下
                    </button>
                    <button
                      onClick={() => {
                        applyLayout('radial');
                        setShowLayoutMenu(false);
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors"
                    >
                      径向布局
                    </button>
                    <button
                      onClick={() => {
                        const newNodes = nodes.map((node: any, i: number) => ({
                          ...node,
                          position: {
                            x: (i % 4) * 220 + 100,
                            y: Math.floor(i / 4) * 150 + 100
                          }
                        }));
                        setNodes(newNodes as any);
                        setShowLayoutMenu(false);
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors"
                    >
                      网格布局
                    </button>
                  </div>
                )}
              </div>
            </div>
          </ReactFlow>
        </div>

        {/* Right Panel - Class Details */}
        {isRightPanelOpen && selectedClass && (
          <div className="w-80 bg-white border-l flex flex-col shrink-0 animate-slide-in-right">
            <div className="p-4 border-b flex items-center justify-between">
              <h2 className="font-semibold text-gray-900">{selectedClass.name}</h2>
              <button
                onClick={() => setIsRightPanelOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-auto p-4">
              <div className="text-sm text-gray-500 mb-4">
                {selectedClass.description || '暂无描述'}
              </div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-gray-900">属性</h3>
                <button
                  onClick={handleOpenAddPropertyModal}
                  className="text-sm px-3 py-1 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
                >
                  + 添加属性
                </button>
              </div>
              <div className="space-y-2">
                {selectedClass.properties.map(prop => (
                  <div
                    key={prop.id}
                    className="p-3 rounded-lg border border-gray-200 bg-gray-50"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-medium text-gray-900">{prop.name}</span>
                        <span className="ml-2 text-xs text-gray-500">({prop.type})</span>
                      </div>
                      <button
                        onClick={() => handleDeleteProperty(prop.id)}
                        className="text-red-500 hover:text-red-700 text-xs"
                      >
                        删除
                      </button>
                    </div>
                    {prop.description && (
                      <div className="text-xs text-gray-500 mt-1">{prop.description}</div>
                    )}
                  </div>
                ))}
                {selectedClass.properties.length === 0 && (
                  <div className="text-center text-gray-400 py-4">暂无属性</div>
                )}
              </div>
              <div className="mt-6 pt-4 border-t">
                <button
                  onClick={() => handleDeleteClass(selectedClass.id)}
                  className="w-full py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
                >
                  删除此类
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
