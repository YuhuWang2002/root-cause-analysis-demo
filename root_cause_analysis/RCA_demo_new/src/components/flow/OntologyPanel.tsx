import { useCallback, useEffect, useMemo } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeChange,
  EdgeChange,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useOntologyStore } from '@/stores/ontologyStore';
import { useProjectStore } from '@/stores/projectStore';

interface OntologyCanvasProps {
  ontologyId: number;
  projectId: string;
}

const nodeDefaults = {
  type: 'default' as const,
  style: {
    background: '#fff',
    border: '1px solid #1a192b',
    borderRadius: '8px',
    padding: '10px',
    minWidth: '120px',
    textAlign: 'center' as const,
  },
};

export function OntologyCanvas({ ontologyId, projectId }: OntologyCanvasProps) {
  const { currentOntology, selectClass, selectedClassId, saveCanvas } = useOntologyStore();
  
  const initialNodes: Node[] = useMemo(() => {
    if (!currentOntology?.canvas_data || currentOntology.canvas_data.length === 0) {
      return currentOntology?.classes.map((cls, idx) => ({
        id: String(cls.id),
        position: { x: 100 + (idx % 3) * 200, y: 100 + Math.floor(idx / 3) * 100 },
        data: { label: cls.name },
        ...nodeDefaults,
        selected: cls.id === selectedClassId,
      })) || [];
    }
    return currentOntology.canvas_data.map((node: any) => ({
      ...node,
      selected: node.id === String(selectedClassId),
    }));
  }, [currentOntology, selectedClassId]);

  const initialEdges: Edge[] = useMemo(() => {
    if (!currentOntology?.relations) return [];
    return currentOntology.relations.map((rel) => ({
      id: String(rel.id),
      source: String(rel.source_class_id),
      target: String(rel.target_class_id),
      label: rel.relation_type,
      animated: true,
    }));
  }, [currentOntology]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const classId = parseInt(node.id);
      selectClass(classId);
    },
    [selectClass]
  );

  const onNodesChangeHandler = useCallback(
    (changes: NodeChange[]) => {
      onNodesChange(changes);
      const newNodes = nodes.map((n) => ({
        id: n.id,
        position: n.position,
        data: n.data,
        type: n.type,
        style: n.style,
      }));
      saveCanvas(projectId, ontologyId, newNodes);
    },
    [nodes, onNodesChange, saveCanvas, projectId, ontologyId]
  );

  return (
    <div style={{ width: '100%', height: '400px', border: '1px solid #e5e7eb', borderRadius: '8px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChangeHandler}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        fitView
      >
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
}

export function OntologyPanel() {
  const { currentOntology, selectedClassId, isPanelOpen, closePanel, selectClass, createClass, deleteClass, addProperty, deleteProperty, addRelation, deleteRelation, ontologies, fetchOntologies, createOntology } = useOntologyStore();
  const { projects } = useProjectStore();
  
  const currentProject = projects[0];
  const projectId = currentProject?.id;

  useEffect(() => {
    if (projectId) {
      fetchOntologies(projectId);
    }
  }, [projectId, fetchOntologies]);

  if (!isPanelOpen) return null;

  const selectedClass = currentOntology?.classes.find((c) => c.id === selectedClassId);

  const handleCreateClass = async () => {
    if (!projectId || !currentOntology) return;
    const name = prompt('请输入类名称:');
    if (name) {
      await createClass(projectId, currentOntology.id, name, '');
    }
  };

  const handleAddProperty = async () => {
    if (!projectId || !currentOntology || !selectedClassId) return;
    const name = prompt('请输入属性名称:');
    const type = prompt('请输入属性类型 (string/number/boolean):', 'string');
    const description = prompt('请输入属性描述:', '');
    if (name && type) {
      await addProperty(projectId, currentOntology.id, selectedClassId, name, type, description || '');
    }
  };

  const handleAddRelation = async () => {
    if (!projectId || !currentOntology || currentOntology.classes.length < 2) return;
    const sourceId = prompt(`请输入源类ID (可选: ${currentOntology.classes.map(c => `${c.id}:${c.name}`).join(', ')}):`);
    const targetId = prompt(`请输入目标类ID:`);
    const relationType = prompt('请输入关系类型 (如: hasProperty, dependsOn):', 'has_relation');
    if (sourceId && targetId && relationType) {
      await addRelation(projectId, currentOntology.id, parseInt(sourceId), parseInt(targetId), relationType);
    }
  };

  const handleCreateOntology = async () => {
    if (!projectId) return;
    const name = prompt('请输入本体库名称:');
    const description = prompt('请输入本体库描述:', '');
    if (name) {
      await createOntology(projectId, name, description || '');
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-[600px] bg-white shadow-lg z-50 flex flex-col">
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold">本体库配置</h2>
        <button onClick={closePanel} className="text-gray-500 hover:text-gray-700">
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {!currentOntology ? (
          <div>
            <p className="text-gray-600 mb-4">请选择一个本体库或创建新的本体库：</p>
            <div className="space-y-2 mb-4">
              {ontologies.map((onto) => (
                <div
                  key={onto.id}
                  className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
                  onClick={() => useOntologyStore.getState().selectOntology(onto)}
                >
                  <div className="font-medium">{onto.name}</div>
                  <div className="text-sm text-gray-500">{onto.description}</div>
                  <div className="text-xs text-gray-400">{onto.classes.length} 个类</div>
                </div>
              ))}
            </div>
            <button
              onClick={handleCreateOntology}
              className="w-full py-2 bg-primary text-white rounded-lg hover:bg-primary-dark"
            >
              创建新本体库
            </button>
          </div>
        ) : (
          <div>
            <div className="mb-4">
              <h3 className="font-medium mb-2">{currentOntology.name}</h3>
              <p className="text-sm text-gray-500">{currentOntology.description}</p>
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">本体可视化画布</h4>
                <button
                  onClick={handleCreateClass}
                  className="text-sm px-3 py-1 bg-primary text-white rounded hover:bg-primary-dark"
                >
                  添加类
                </button>
              </div>
              <OntologyCanvas ontologyId={currentOntology.id} projectId={projectId!} />
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">关系管理</h4>
                <button
                  onClick={handleAddRelation}
                  className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                >
                  添加关系
                </button>
              </div>
              <div className="space-y-1">
                {currentOntology.relations.map((rel) => (
                  <div key={rel.id} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                    <span>{rel.source_class_name} → {rel.relation_type} → {rel.target_class_name}</span>
                    <button
                      onClick={() => deleteRelation(projectId!, currentOntology.id, rel.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      删除
                    </button>
                  </div>
                ))}
                {currentOntology.relations.length === 0 && (
                  <p className="text-gray-400 text-sm">暂无关系</p>
                )}
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-2">类列表（点击选择）</h4>
              <div className="space-y-2">
                {currentOntology.classes.map((cls) => (
                  <div
                    key={cls.id}
                    className={`p-3 border rounded-lg cursor-pointer ${
                      cls.id === selectedClassId ? 'border-primary bg-primary/5' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => selectClass(cls.id)}
                  >
                    <div className="font-medium">{cls.name}</div>
                    <div className="text-sm text-gray-500">{cls.description}</div>
                    <div className="text-xs text-gray-400">{cls.properties.length} 个属性</div>
                  </div>
                ))}
              </div>
            </div>

            {selectedClass && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">属性: {selectedClass.name}</h4>
                  <button
                    onClick={handleAddProperty}
                    className="text-sm px-3 py-1 bg-primary text-white rounded hover:bg-primary-dark"
                  >
                    添加属性
                  </button>
                </div>
                <div className="space-y-2">
                  {selectedClass.properties.map((prop) => (
                    <div key={prop.id} className="flex items-center justify-between p-2 bg-white rounded border">
                      <div>
                        <span className="font-medium">{prop.name}</span>
                        <span className="text-xs text-gray-500 ml-2">({prop.type})</span>
                        {prop.description && <div className="text-xs text-gray-400">{prop.description}</div>}
                      </div>
                      <button
                        onClick={() => deleteProperty(projectId!, currentOntology.id, selectedClassId!, prop.id)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        删除
                      </button>
                    </div>
                  ))}
                  {selectedClass.properties.length === 0 && (
                    <p className="text-gray-400 text-sm">暂无属性</p>
                  )}
                </div>
                <div className="mt-3 pt-3 border-t">
                  <button
                    onClick={() => deleteClass(projectId!, currentOntology.id, selectedClassId!)}
                    className="text-sm text-red-500 hover:text-red-700"
                  >
                    删除此类
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
