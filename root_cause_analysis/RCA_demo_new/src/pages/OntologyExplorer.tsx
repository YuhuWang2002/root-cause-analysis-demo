import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  NodeTypes,
  Handle,
} from 'reactflow';
import dagre from 'dagre';
import 'reactflow/dist/style.css';
import { useOntologyStore } from '@/stores/ontologyStore';
import * as api from '@/services/api';

// 自定义节点组件
function CustomOntologyNode({ data, selected, isConnectable }: { data: { id: string; name: string; icon: string }; selected?: boolean; isConnectable?: boolean }) {
  return (
    <div
      className={`w-40 h-32 border-2 ${selected ? 'border-blue-600' : 'border-blue-500'} rounded-lg p-3 bg-white shadow-sm cursor-move`}
    >
      {/* 输入 handle */}
      <Handle
        type="target"
        position="left"
        style={{ background: '#555' }}
        isConnectable={isConnectable}
      />
      
      <div className="flex items-center mb-2">
        <span className="mr-2">{data.icon}</span>
        <h4 className="font-medium text-blue-600">{data.name}</h4>
      </div>
      <div className="space-y-1 text-xs">
        <div className="flex justify-between">
          <span className="text-gray-500">{data.id.toLowerCase()}_id:</span>
          <span className="font-medium">{data.id.substring(0, 2).toUpperCase()}1234</span>
        </div>
        {data.id === 'Flight' && (
          <>
            <div className="flex justify-between">
              <span className="text-gray-500">passenger_count:</span>
              <span className="font-medium">186</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">fuel_consumption:</span>
              <span className="font-medium">42.5 LM</span>
            </div>
          </>
        )}
        {data.id === 'Airport' && (
          <>
            <div className="flex justify-between">
              <span className="text-gray-500">name:</span>
              <span className="font-medium">肯尼迪机场</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">city:</span>
              <span className="font-medium">纽约</span>
            </div>
          </>
        )}
        {data.id === 'Passenger' && (
          <>
            <div className="flex justify-between">
              <span className="text-gray-500">name:</span>
              <span className="font-medium">张三</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">age:</span>
              <span className="font-medium">30</span>
            </div>
          </>
        )}
      </div>
      
      {/* 输出 handle */}
      <Handle
        type="source"
        position="right"
        style={{ background: '#555' }}
        isConnectable={isConnectable}
      />
    </div>
  );
}

const nodeTypes: NodeTypes = {
  custom: CustomOntologyNode,
};

const OntologyExplorer: React.FC = () => {
  const { projectId, ontologyId } = useParams<{ projectId: string; ontologyId: string }>();
  const navigate = useNavigate();
  const { ontologies, fetchOntologies, selectedOntology, selectOntology } = useOntologyStore();
  
  const [selectedEntity, setSelectedEntity] = useState('Flight');
  const [searchTerm, setSearchTerm] = useState('');
  const [showRightPanel, setShowRightPanel] = useState(false);
  const [selectedCanvasEntity, setSelectedCanvasEntity] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [relatedEntities, setRelatedEntities] = useState<any[]>([]);
  const [selectedOntologyId, setSelectedOntologyId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ontologyClasses, setOntologyClasses] = useState<any[]>([]);
  
  // 过滤条件状态
  const [filters, setFilters] = useState<any[]>([]);
  const [currentFilter, setCurrentFilter] = useState({
    classId: '',
    property: '',
    operator: '=',
    value: ''
  });
  
  // 聚合操作状态
  const [aggregations, setAggregations] = useState<any[]>([]);
  const [currentAggregation, setCurrentAggregation] = useState({
    classId: '',
    property: '',
    aggregationType: 'avg',
    dimension: 'day'
  });
  
  // 直接使用 ReactFlow 的状态管理
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  // 使用 ref 来追踪最新的节点和边，用于自动布局
  const nodesRef = React.useRef(nodes);
  const edgesRef = React.useRef(edges);
  nodesRef.current = nodes;
  edgesRef.current = edges;

  // 自动布局函数（从左到右）
  const getLayoutedElements = useCallback((nodes: Node[], edges: Edge[]) => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));

    const nodeWidth = 176;
    const nodeHeight = 140;

    dagreGraph.setGraph({
      rankdir: 'LR',
      nodesep: 80,
      ranksep: 120,
      marginx: 50,
      marginy: 50,
    });

    nodes.forEach((node) => {
      dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    edges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    const layoutedNodes = nodes.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      if (!nodeWithPosition) {
        return {
          ...node,
        };
      }
      return {
        ...node,
        position: {
          x: nodeWithPosition.x - nodeWidth / 2,
          y: nodeWithPosition.y - nodeHeight / 2,
        },
      };
    });

    return { nodes: layoutedNodes, edges };
  }, []);

  // 触发自动布局（使用 ref 获取最新状态）
  const triggerAutoLayout = useCallback(() => {
    const currentNodes = nodesRef.current;
    const currentEdges = edgesRef.current;
    if (currentNodes.length === 0) return;
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(currentNodes, currentEdges);
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  }, [getLayoutedElements, setNodes, setEdges]);

  // 使用 useEffect 监听节点数量变化，自动触发布局
  useEffect(() => {
    if (nodes.length > 0) {
      const timer = setTimeout(() => {
        const currentNodes = nodesRef.current;
        const currentEdges = edgesRef.current;
        if (currentNodes.length > 0) {
          const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(currentNodes, currentEdges);
          setNodes(layoutedNodes);
          setEdges(layoutedEdges);
        }
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [nodes.length]);

  // 保存本体探索配置
  const handleSave = async () => {
    if (!projectId || !selectedOntologyId || !selectedCanvasEntity) {
      alert('请选择本体类');
      return;
    }
    
    setIsSaving(true);
    try {
      // 准备画布数据
      const canvasData = {
        nodes: nodes.map(node => ({
          id: node.id,
          name: node.data.name,
          type: 'ontology',
          position: node.position,
          data: node.data,
          // 为每个节点添加配置
          config: node.id === selectedCanvasEntity ? {
            filters: filters,
            aggregations: aggregations
          } : node.data.config
        })),
        edges: edges.map(edge => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type,
          style: edge.style
        }))
      };
      
      // 调用 API 保存画布数据
      await api.saveOntologyCanvas(projectId, parseInt(selectedOntologyId), canvasData);
      
      setIsSaving(false);
      alert('保存成功');
    } catch (error) {
      console.error('保存失败:', error);
      setIsSaving(false);
      alert('保存失败: ' + (error as Error).message);
    }
  };

  // 加载实体配置
  const loadEntityConfig = (entityId: string) => {
    // 从当前节点中查找配置
    const node = nodes.find(n => n.id === entityId);
    if (node && node.data.config) {
      const config = node.data.config;
      if (config.filters) {
        setFilters(config.filters);
      }
      if (config.aggregations) {
        setAggregations(config.aggregations);
      }
    }
  };



  // 加载本体库数据
  useEffect(() => {
    if (projectId) {
      setIsLoading(true);
      setError(null);
      fetchOntologies(projectId).catch(err => {
        console.error('Failed to fetch ontologies:', err);
        setError('加载本体库失败');
      }).finally(() => {
        setIsLoading(false);
      });
    }
  }, [projectId, fetchOntologies]);

  // 当本体库列表加载完成后，优先使用 URL 参数中的 ontologyId，否则选择第一个本体库
  useEffect(() => {
    if (ontologies.length > 0) {
      if (ontologyId && ontologies.some(o => o.id.toString() === ontologyId)) {
        setSelectedOntologyId(ontologyId);
      } else if (!selectedOntologyId) {
        setSelectedOntologyId(ontologies[0].id.toString());
      }
    }
  }, [ontologies, selectedOntologyId, ontologyId]);

  // 当选择不同的本体库时，加载对应的本体类和画布数据
  useEffect(() => {
    if (projectId && selectedOntologyId) {
      setIsLoading(true);
      setError(null);
      api.getOntology(projectId, parseInt(selectedOntologyId))
        .then(ontology => {
          setOntologyClasses(ontology.classes || []);
          
          // 加载画布数据
          if (ontology.canvas_data && ontology.canvas_data.length > 0) {
            const canvasData = ontology.canvas_data[0];
            if (canvasData.nodes && canvasData.edges) {
              const loadedNodes = canvasData.nodes.map((node: any) => ({
                ...node,
                type: 'custom',
                zIndex: 10
              }));
              const loadedEdges = canvasData.edges.map((edge: any) => ({
                ...edge,
                type: 'smoothstep',
                animated: true
              }));
              // 应用自动布局
              const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                loadedNodes as Node[],
                loadedEdges as Edge[]
              );
              setNodes(layoutedNodes);
              setEdges(layoutedEdges);
            }
          } else {
            // 重置画布数据
            setNodes([]);
            setEdges([]);
          }
        })
        .catch(err => {
          console.error('Failed to fetch ontology classes:', err);
          setError('加载本体类失败');
          setOntologyClasses([]);
          setNodes([]);
          setEdges([]);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [projectId, selectedOntologyId]);

  // 过滤本体目录
  const filteredCatalog = ontologyClasses.filter(item => 
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 为本体类生成图标
  const getClassIcon = (className: string) => {
    const iconMap: Record<string, string> = {
      'Flight': '✈️',
      'Airport': '🏛️',
      'Passenger': '🧑‍✈️',
      'Doctor': '👨‍⚕️',
      'Patient': '👤',
      'Bank': '🏦',
      'Account': '💳',
      'User': '👥',
      'Product': '📦',
      'Order': '📋',
      'Payment': '💸',
      'Address': '📍',
      'Email': '📧',
      'Phone': '📱'
    };
    return iconMap[className] || '📦';
  };

  // 添加实体到画布
  const addEntityToCanvas = (entity: { id: number; name: string }) => {
    const newNode: Node = {
      id: entity.id.toString(),
      type: 'custom',
      position: { 
        x: 100 + Math.random() * 400, 
        y: 100 + Math.random() * 200 
      },
      data: { 
        id: entity.id.toString(), 
        name: entity.name, 
        icon: getClassIcon(entity.name) 
      },
      zIndex: 10 + nodes.length,
    };
    
    // 先获取当前的节点列表
    const currentNodes = [...nodes];
    
    setNodes(prevNodes => [...prevNodes, newNode]);
    
    // 检查与画布上已有实体的关系并添加连线
    if (projectId && selectedOntologyId) {
      api.getOntology(projectId, parseInt(selectedOntologyId))
        .then(ontology => {
          const relations = ontology.relations || [];
          console.log('Relations:', relations);
          
          // 检查新实体与已有节点的关系
          currentNodes.forEach(existingNode => {
            const existingEntityId = parseInt(existingNode.id);
            const newEntityId = entity.id;
            console.log('Checking relations between', existingEntityId, 'and', newEntityId);
            
            // 检查是否有从已有实体到新实体的关系
            const relationFromExisting = relations.find(r => 
              r.source_class_id === existingEntityId && r.target_class_id === newEntityId
            );
            
            if (relationFromExisting) {
              console.log('Found relation from existing to new:', relationFromExisting);
              const newEdge: Edge = {
                id: `edge-${existingNode.id}-${newNode.id}`,
                source: existingNode.id,
                target: newNode.id,
                type: 'smoothstep',
                animated: true,
                label: relationFromExisting.relation_type,
                style: { 
                  stroke: '#94a3b8', 
                  strokeWidth: 2,
                  strokeDasharray: '4,2'
                },
                labelStyle: {
                  fill: '#666',
                  fontSize: 12
                }
              };
              setEdges(prevEdges => {
                // 检查边是否已存在
                if (!prevEdges.some(e => e.id === newEdge.id)) {
                  console.log('Adding edge:', newEdge);
                  return [...prevEdges, newEdge];
                }
                return prevEdges;
              });
            }
            
            // 检查是否有从新实体到已有实体的关系
            const relationToExisting = relations.find(r => 
              r.source_class_id === newEntityId && r.target_class_id === existingEntityId
            );
            
            if (relationToExisting) {
              console.log('Found relation from new to existing:', relationToExisting);
              const newEdge: Edge = {
                id: `edge-${newNode.id}-${existingNode.id}`,
                source: newNode.id,
                target: existingNode.id,
                type: 'smoothstep',
                animated: true,
                label: relationToExisting.relation_type,
                style: { 
                  stroke: '#94a3b8', 
                  strokeWidth: 2,
                  strokeDasharray: '4,2'
                },
                labelStyle: {
                  fill: '#666',
                  fontSize: 12
                }
              };
              setEdges(prevEdges => {
                // 检查边是否已存在
                if (!prevEdges.some(e => e.id === newEdge.id)) {
                  console.log('Adding edge:', newEdge);
                  return [...prevEdges, newEdge];
                }
                return prevEdges;
              });
            }
          });
        })
        .catch(err => {
          console.error('Failed to fetch relations:', err);
        });
    }
  };

  // 获取与选中实体有关系的相邻实体
  const fetchRelatedEntities = (entityId: string) => {
    if (!projectId || !selectedOntologyId) {
      console.log('Missing projectId or selectedOntologyId');
      return;
    }
    
    console.log('Fetching related entities for entityId:', entityId);
    console.log('ProjectId:', projectId);
    console.log('SelectedOntologyId:', selectedOntologyId);
    
    // 从当前本体库中获取关系数据
    api.getOntology(projectId, parseInt(selectedOntologyId))
      .then(ontology => {
        console.log('Received ontology data:', ontology);
        const relations = ontology.relations || [];
        const classes = ontology.classes || [];
        
        console.log('Relations found:', relations.length);
        console.log('Classes found:', classes.length);
        
        // 找到与选中实体相关的关系
        const related = [];
        
        relations.forEach(relation => {
          console.log('Checking relation:', relation);
          if (relation.source_class_id.toString() === entityId) {
            // 找到目标类
            const targetClass = classes.find(c => c.id === relation.target_class_id);
            if (targetClass) {
              related.push({
                ...targetClass,
                relationType: relation.relation_type,
                relationDirection: 'outgoing'
              });
              console.log('Found outgoing relation:', targetClass);
            }
          } else if (relation.target_class_id.toString() === entityId) {
            // 找到源类
            const sourceClass = classes.find(c => c.id === relation.source_class_id);
            if (sourceClass) {
              related.push({
                ...sourceClass,
                relationType: relation.relation_type,
                relationDirection: 'incoming'
              });
              console.log('Found incoming relation:', sourceClass);
            }
          }
        });
        
        console.log('Related entities found:', related.length);
        console.log('Related entities:', related);
        setRelatedEntities(related);
      })
      .catch(err => {
        console.error('Failed to fetch related entities:', err);
        setRelatedEntities([]);
      });
  };

  // 处理节点点击
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      // 先保存当前节点的配置
      if (selectedCanvasEntity) {
        const updatedNodes = nodes.map(n => {
          if (n.id === selectedCanvasEntity) {
            return {
              ...n,
              data: {
                ...n.data,
                config: {
                  filters: filters,
                  aggregations: aggregations
                }
              }
            };
          }
          return n;
        });
        setNodes(updatedNodes);
      }
      
      setSelectedCanvasEntity(node.id);
      setShowRightPanel(true);
      // 重置过滤条件和聚合操作
      setFilters([]);
      setCurrentFilter({
        property: '',
        operator: '=',
        value: ''
      });
      setAggregations([]);
      setCurrentAggregation({
        property: '',
        aggregationType: 'avg',
        dimension: 'day'
      });
      // 获取与选中实体有关系的相邻实体
      console.log('Node clicked, fetching related entities for:', node.id);
      fetchRelatedEntities(node.id);
      // 加载该实体的保存配置
      loadEntityConfig(node.id);
    },
    [setSelectedCanvasEntity, setShowRightPanel, fetchRelatedEntities, loadEntityConfig, selectedCanvasEntity, nodes, filters, aggregations]
  );

  // 处理搜索
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    
    // 从本体类中搜索
    const results = ontologyClasses.filter(item => 
      item.name.toLowerCase().includes(query.toLowerCase())
    );
    setSearchResults(results);
  };

  // 处理节点拖动结束
  const onNodeDragStop = useCallback(
    (_: React.MouseEvent, node: Node) => {
      // 节点位置会通过 onNodesChange 自动更新
    },
    []
  );

  // 获取选中实体的名称
  const getSelectedEntityName = (entityId: string | null) => {
    if (!entityId) return '';
    const node = nodes.find(n => n.id === entityId);
    if (node) {
      return node.data.name || '';
    }
    // 从本体类中查找
    const ontologyClass = ontologyClasses.find(c => c.id.toString() === entityId);
    return ontologyClass?.name || '';
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* 返回项目栏 */}
      <div className="h-14 bg-white border-b flex items-center px-6 justify-between shrink-0">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(`/flow/${projectId}`)} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            返回项目
          </button>
          <div className="h-6 w-px bg-gray-200" />
          <h1 className="text-lg font-semibold text-gray-900">本体探索</h1>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={handleSave} disabled={isSaving} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            {isSaving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* 左侧导航栏 */}
        <div className="w-64 border-r border-gray-200 bg-white flex-shrink-0">
          <div className="p-4 border-b border-gray-200">
            <div className="mb-4">
            <label className="block text-xs font-medium text-gray-500 mb-1">选择本体库</label>
            <select
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={selectedOntologyId}
              onChange={(e) => setSelectedOntologyId(e.target.value)}
              disabled={isLoading || ontologies.length === 0}
            >
              {isLoading ? (
                <option value="">加载中...</option>
              ) : ontologies.length === 0 ? (
                <option value="">无本体库</option>
              ) : (
                ontologies.map((lib) => (
                  <option key={lib.id} value={lib.id}>{lib.name}</option>
                ))
              )}
            </select>
          </div>
          {error && (
            <div className="mb-4 p-2 bg-red-50 border border-red-200 rounded-md text-red-600 text-xs">
              {error}
            </div>
          )}
            
            <div className="relative mb-4">
              <input
                type="text"
                placeholder="搜索本体类..."
                className="w-full px-3 py-2 pr-8 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div className="p-4">
            <h3 className="mb-2 text-sm font-medium text-gray-700">本体目录</h3>
            <div className="space-y-1 max-h-[calc(100vh-200px)] overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-8 text-gray-500 text-sm">
                  加载中...
                </div>
              ) : filteredCatalog.length === 0 ? (
                <div className="flex items-center justify-center py-8 text-gray-500 text-sm">
                  无本体类
                </div>
              ) : (
                filteredCatalog.map((entity) => (
                  <div
                    key={entity.id}
                    className={`flex items-center p-2 rounded-md cursor-pointer hover:bg-gray-100`}
                    onClick={() => {
                      setSelectedCanvasEntity(entity.id.toString());
                      setShowRightPanel(true);
                    }}
                  >
                    <span className="mr-2">{getClassIcon(entity.name)}</span>
                    <span className="text-sm flex-1">{entity.name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        addEntityToCanvas(entity);
                      }}
                      className="text-gray-400 hover:text-blue-600"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* 中间画布区域 */}
        <div className={`flex-1 p-6 transition-all duration-300 ${showRightPanel ? '' : 'mr-0'}`}>
          <div className="h-full bg-white border border-gray-200 rounded-lg overflow-hidden">
            {isLoading ? (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                  <p className="text-sm text-gray-500">加载中...</p>
                </div>
              </div>
            ) : (
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={onNodeClick}
                onNodeDragStop={onNodeDragStop}
                nodeTypes={nodeTypes}
                fitView
                className="bg-white"
                defaultEdgeOptions={{
                  type: 'smoothstep',
                  animated: true,
                  style: { stroke: '#94a3b8', strokeWidth: 2 },
                }}
                proOptions={{ hideAttribution: true }}
                minZoom={0.1}
                maxZoom={2}
                defaultViewport={{ x: 0, y: 0, zoom: 1 }}
              >
                <Background color="#f0f4ff" gap={20} />
                <Controls className="!bg-white !border-gray-200" />
              </ReactFlow>
            )}
          </div>
        </div>

        {/* 右侧控制面板 */}
        <motion.div
          initial={{ x: 320 }}
          animate={{ x: showRightPanel ? 0 : 320 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="w-80 border-l border-gray-200 bg-white flex-shrink-0 fixed right-0 top-16 bottom-0 z-50 shadow-lg overflow-y-auto">
          {/* 数据分析面板 */}
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-700">
              {getSelectedEntityName(selectedCanvasEntity)} - 数据浏览
            </h3>
            <button
              onClick={() => setShowRightPanel(false)}
              className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 border border-gray-200"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="space-y-4 p-4">
            <div>
              <h4 className="mb-2 text-xs font-medium text-gray-500">总览 (最近30天)</h4>
              <div className="flex items-end justify-between">
                <span className="text-2xl font-bold text-gray-800">1,247</span>
                <span className="text-xs text-green-600">+12.5%</span>
              </div>
            </div>
            
            <div className="h-20 bg-gray-50 rounded-md flex items-center justify-center">
              <div className="text-center">
                <div className="text-xs text-gray-500">趋势图表</div>
              </div>
            </div>
          </div>
          
          {/* 过滤条件面板 */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-700">过滤条件 (Filters)</h3>
              <button 
                className="text-xs text-blue-600 hover:text-blue-800"
                onClick={() => {
                  if (selectedCanvasEntity && currentFilter.property && currentFilter.value) {
                    setFilters([...filters, {
                      ...currentFilter,
                      classId: selectedCanvasEntity
                    }]);
                    setCurrentFilter({
                      property: '',
                      operator: '=',
                      value: ''
                    });
                  }
                }}
              >
                添加条件
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">属性</label>
                  <select
                    className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    value={currentFilter.property}
                    onChange={(e) => setCurrentFilter({ ...currentFilter, property: e.target.value })}
                  >
                    <option value="">-- 选择属性 --</option>
                    {selectedCanvasEntity && (
                      ontologyClasses
                        .find(cls => cls.id.toString() === selectedCanvasEntity)
                        ?.properties.map((prop: any) => (
                          <option key={prop.id} value={prop.name}>{prop.name}</option>
                        ))
                    )}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">操作符</label>
                  <select
                    className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    value={currentFilter.operator}
                    onChange={(e) => setCurrentFilter({ ...currentFilter, operator: e.target.value })}
                  >
                    <option value="=">等于</option>
                    <option value="!=">不等于</option>
                    <option value=">">大于</option>
                    <option value="<">小于</option>
                    <option value=">=">大于等于</option>
                    <option value="<=">小于等于</option>
                    <option value="contains">包含</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">值</label>
                  <input
                    type="text"
                    placeholder="输入值"
                    className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    value={currentFilter.value}
                    onChange={(e) => setCurrentFilter({ ...currentFilter, value: e.target.value })}
                  />
                </div>
              </div>
              
              {/* 已添加的过滤条件 */}
              {filters.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-gray-500">已添加的条件</h4>
                  <div className="space-y-1">
                    {filters.map((filter, index) => {
                      const cls = ontologyClasses.find(c => c.id.toString() === filter.classId);
                      return (
                        <div key={index} className="flex items-center justify-between p-2 bg-gray-100 rounded-md">
                          <span className="text-xs">
                            {cls?.name}.{filter.property} {filter.operator} {filter.value}
                          </span>
                          <button
                            onClick={() => setFilters(filters.filter((_, i) => i !== index))}
                            className="text-xs text-red-600 hover:text-red-800"
                          >
                            删除
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              
              <div className="flex space-x-2">
                <button className="flex-1 px-2 py-1 text-xs font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
                  应用
                </button>
                <button 
                  className="flex-1 px-2 py-1 text-xs font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-100"
                  onClick={() => {
                    setFilters([]);
                    setCurrentFilter({
                      classId: '',
                      property: '',
                      operator: '=',
                      value: ''
                    });
                  }}
                >
                  重置
                </button>
              </div>
            </div>
          </div>
          
          {/* 聚合操作面板 */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-700">2. 聚合组 (Aggregation)</h3>
              <button 
                className="text-xs text-blue-600 hover:text-blue-800"
                onClick={() => {
                  if (selectedCanvasEntity && currentAggregation.property) {
                    setAggregations([...aggregations, {
                      ...currentAggregation,
                      classId: selectedCanvasEntity
                    }]);
                    setCurrentAggregation({
                      property: '',
                      aggregationType: 'avg',
                      dimension: 'day'
                    });
                  }
                }}
              >
                添加聚合
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">聚合属性</label>
                  <select
                    className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    value={currentAggregation.property}
                    onChange={(e) => setCurrentAggregation({ ...currentAggregation, property: e.target.value })}
                  >
                    <option value="">-- 选择属性 --</option>
                    {selectedCanvasEntity && (
                      ontologyClasses
                        .find(cls => cls.id.toString() === selectedCanvasEntity)
                        ?.properties.map((prop: any) => (
                          <option key={prop.id} value={prop.name}>{prop.name}</option>
                        ))
                    )}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">聚合类型</label>
                  <select
                    className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    value={currentAggregation.aggregationType}
                    onChange={(e) => setCurrentAggregation({ ...currentAggregation, aggregationType: e.target.value })}
                  >
                    <option value="avg">平均值</option>
                    <option value="sum">总和</option>
                    <option value="count">计数</option>
                    <option value="min">最小值</option>
                    <option value="max">最大值</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">维度</label>
                  <select
                    className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    value={currentAggregation.dimension}
                    onChange={(e) => setCurrentAggregation({ ...currentAggregation, dimension: e.target.value })}
                  >
                    <option value="day">每日</option>
                    <option value="week">每周</option>
                    <option value="month">每月</option>
                    <option value="quarter">每季度</option>
                    <option value="year">每年</option>
                  </select>
                </div>
              </div>
              
              {/* 已添加的聚合项 */}
              {aggregations.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-gray-500">已添加的聚合项</h4>
                  <div className="space-y-1">
                    {aggregations.map((agg, index) => {
                      const cls = ontologyClasses.find(c => c.id.toString() === agg.classId);
                      const aggTypeMap: Record<string, string> = {
                        avg: '平均值',
                        sum: '总和',
                        count: '计数',
                        min: '最小值',
                        max: '最大值'
                      };
                      const dimensionMap: Record<string, string> = {
                        day: '每日',
                        week: '每周',
                        month: '每月',
                        quarter: '每季度',
                        year: '每年'
                      };
                      return (
                        <div key={index} className="flex items-center justify-between p-2 bg-gray-100 rounded-md">
                          <span className="text-xs">
                            {aggTypeMap[agg.aggregationType]}({cls?.name}.{agg.property}) 按 {dimensionMap[agg.dimension]}
                          </span>
                          <button
                            onClick={() => setAggregations(aggregations.filter((_, i) => i !== index))}
                            className="text-xs text-red-600 hover:text-red-800"
                          >
                            删除
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* 搜索周围面板 */}
          <div className="p-4">
            <h3 className="mb-3 text-sm font-medium text-gray-700">4. 搜索周围 (Search Around)</h3>
            <div className="space-y-3">
              <input
                type="text"
                placeholder="搜索本体..."
                className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
              />
              
              {/* 搜索结果 */}
              {searchQuery && searchResults.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-gray-500">搜索结果</h4>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {searchResults.map((entity) => (
                      <div
                        key={entity.id}
                        className="flex items-center p-2 rounded-md hover:bg-gray-100"
                      >
                        <span className="mr-2">{getClassIcon(entity.name)}</span>
                        <span className="text-sm flex-1">{entity.name}</span>
                        <button
                          onClick={() => addEntityToCanvas(entity)}
                          className="text-gray-400 hover:text-blue-600"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* 相邻实体 */}
              {selectedCanvasEntity && relatedEntities.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-gray-500">相邻实体</h4>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {relatedEntities.map((entity) => (
                      <div
                        key={entity.id}
                        className="flex items-center p-2 rounded-md hover:bg-gray-100"
                      >
                        <span className="mr-2">{getClassIcon(entity.name)}</span>
                        <div className="flex-1">
                          <div className="text-sm">{entity.name}</div>
                          <div className="text-xs text-gray-500">
                            {entity.relationDirection === 'outgoing' ? '→' : '←'} {entity.relationType}
                          </div>
                        </div>
                        <button
                          onClick={() => addEntityToCanvas(entity)}
                          className="text-gray-400 hover:text-blue-600"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <button className="w-full flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
                搜索
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default OntologyExplorer;