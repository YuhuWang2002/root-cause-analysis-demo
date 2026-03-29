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
  MarkerType,
} from 'reactflow';
import dagre from 'dagre';
import 'reactflow/dist/style.css';
import { useOntologyStore } from '@/stores/ontologyStore';
import * as api from '@/services/api';

// 自定义节点组件
function CustomOntologyNode({ data, selected, isConnectable }: { 
  data: { id: string; name: string; icon: string; queryCount?: number; class_id?: string | number }; 
  selected?: boolean; 
  isConnectable?: boolean 
}) {
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
          <span className="text-gray-500">class_id:</span>
          <span className="font-medium">{data.class_id ?? data.id}</span>
        </div>
        {data.queryCount !== undefined && (
          <div className="flex justify-between">
            <span className="text-gray-500">总数:</span>
            <span className="font-medium text-green-600">{data.queryCount}</span>
          </div>
        )}
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
  const [ontology, setOntology] = useState<any>(null);
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
  
  // 图查询结果状态
  const [graphQueryResult, setGraphQueryResult] = useState<any>(null);
  const [nodeResults, setNodeResults] = useState<{ [nodeId: string]: { count: number; results: string[] } }>({});
  const [aggregationResults, setAggregationResults] = useState<{
    [nodeId: string]: {
      [aggKey: string]: number;
    };
  }>({});
  const [isQueryLoading, setIsQueryLoading] = useState(false);
  
  // 直接使用 ReactFlow 的状态管理
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  // 使用 ref 来保存查询函数，避免依赖循环
  const executeGraphQueryRef = React.useRef<() => Promise<void>>();
  const projectIdRef = React.useRef(projectId);
  const selectedOntologyIdRef = React.useRef(selectedOntologyId);
  const nodesRefForQuery = React.useRef(nodes);
  const edgesRefForQuery = React.useRef(edges);
  const filtersRef = React.useRef(filters);
  const queryDebounceTimerRef = React.useRef<NodeJS.Timeout | null>(null);
  
  // 使用 ref 来追踪最新的节点和边，用于自动布局
  const nodesRef = React.useRef(nodes);
  const edgesRef = React.useRef(edges);
  nodesRef.current = nodes;
  edgesRef.current = edges;
  
  // 更新查询用的 refs
  useEffect(() => {
    projectIdRef.current = projectId;
    selectedOntologyIdRef.current = selectedOntologyId;
    nodesRefForQuery.current = nodes;
    edgesRefForQuery.current = edges;
    filtersRef.current = filters;
  }, [projectId, selectedOntologyId, nodes, edges, filters]);

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

  // 立即保存当前选中实体的配置
  const saveCurrentEntityConfig = useCallback(() => {
    if (!selectedCanvasEntity) return;
    
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
  }, [selectedCanvasEntity, nodes, filters, aggregations, setNodes]);



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

  // 同步更新 nodes/edges refs，确保 executeGraphQuery 获取到最新配置
  useEffect(() => {
    nodesRefForQuery.current = [...nodes];
  }, [nodes]);

  useEffect(() => {
    edgesRefForQuery.current = [...edges];
  }, [edges]);

  // 当选择不同的本体库时，加载对应的本体类和画布数据
  useEffect(() => {
    if (projectId && selectedOntologyId) {
      setIsLoading(true);
      setError(null);
      api.getOntology(projectId, parseInt(selectedOntologyId))
        .then(ontology => {
          setOntology(ontology);
          setOntologyClasses(ontology.classes || []);
          
          // 加载画布数据
          if (ontology.canvas_data && ontology.canvas_data.length > 0) {
            const canvasData = ontology.canvas_data[0];
            if (canvasData.nodes && canvasData.edges) {
              const loadedNodes = canvasData.nodes.map((node: any) => {
                const cls = ontologyClasses.find(c => c.id.toString() === node.id);
                return {
                  ...node,
                  type: 'custom',
                  zIndex: 10,
                  data: {
                    ...node.data,
                    class_id: cls?.class_id
                  }
                };
              });
              const loadedEdges = canvasData.edges.map((edge: any) => ({
                ...edge,
                type: 'straight',
                animated: true,
                markerEnd: {
                  type: MarkerType.ArrowClosed,
                  color: '#94a3b8',
                },
                label: edge.label?.split('___')[0] || undefined,
                labelStyle: {
                  fill: '#666',
                  fontWeight: 500,
                  fontSize: 11,
                },
                labelBgStyle: {
                  fill: '#fff',
                  fillOpacity: 0.9,
                },
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
  const addEntityToCanvas = (entity: { id: number; name: string; class_id?: string }) => {
    console.log('addEntityToCanvas called with entity:', entity);
    
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
        class_id: entity.class_id,
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
                type: 'straight',
                animated: true,
                markerEnd: {
                  type: MarkerType.ArrowClosed,
                  color: '#94a3b8',
                },
                style: { 
                  stroke: '#94a3b8', 
                  strokeWidth: 2,
                },
                label: relationFromExisting.relation_type,
                labelStyle: {
                  fill: '#666',
                  fontWeight: 500,
                  fontSize: 11,
                },
                labelBgStyle: {
                  fill: '#fff',
                  fillOpacity: 0.9,
                },
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
                type: 'straight',
                animated: true,
                markerEnd: {
                  type: MarkerType.ArrowClosed,
                  color: '#94a3b8',
                },
                style: { 
                  stroke: '#94a3b8', 
                  strokeWidth: 2,
                },
                label: relationToExisting.relation_type,
                labelStyle: {
                  fill: '#666',
                  fontWeight: 500,
                  fontSize: 11,
                },
                labelBgStyle: {
                  fill: '#fff',
                  fillOpacity: 0.9,
                },
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

  // 构建多根节点查询结构（使用 ref 获取最新状态）
  const buildQueryTrees = () => {
    const currentNodes = nodesRefForQuery.current;
    const currentEdges = edgesRefForQuery.current;
    
    console.log('=== buildQueryTrees debug info ===');
    console.log('currentNodes:', currentNodes);
    console.log('currentEdges:', currentEdges);
    
    if (currentNodes.length === 0) {
      console.log('buildQueryTrees: no nodes');
      return [];
    }
    
    // 找到所有根节点（没有入边的节点）
    const rootNodes = currentNodes.filter(n => !currentEdges.some(e => e.target === n.id));
    console.log('rootNodes:', rootNodes);
    
    // 构建节点ID到节点的映射
    const nodeMap = new Map(currentNodes.map(n => [n.id, n]));
    
    // 递归构建单个树
    const buildNodeTree = (nodeId: string): any => {
      const node = nodeMap.get(nodeId);
      if (!node) return null;
      
      // 从 node.data.config.filters 获取过滤条件
      const nodeFilters = node.data.config?.filters || [];
      
      const outgoingEdges = currentEdges.filter(e => e.source === nodeId);
      
      const children = outgoingEdges.map(edge => {
        const targetNode = nodeMap.get(edge.target);
        if (!targetNode) return null;
        
        // 从子节点的 data.config.filters 获取过滤条件
        const targetFilters = targetNode.data.config?.filters || [];
        
        // 递归构建子节点的树
        const childTree = buildNodeTree(edge.target);
        
        return {
          relation: edge.label || '',
          node_type: targetNode.data.class_id || targetNode.data.name,
          filters: targetFilters,
          children: childTree ? childTree.children : []
        };
      }).filter(Boolean);
      
      return {
        node_type: node.data.class_id || node.data.name,
        filters: nodeFilters,
        children
      };
    };
    
    // 为每个根节点构建树
    const queryTrees = rootNodes.map(rootNode => buildNodeTree(rootNode.id)).filter(Boolean);
    
    console.log('buildQueryTrees result:', queryTrees);
    console.log('=== end buildQueryTrees debug info ===');
    
    return queryTrees;
  };

  // 递归遍历查询结果，将结果映射到节点
  const mapResultsToNodes = (treeResult: any, nodes: any[], edges: any[], nodeResults: any, currentNodeId: string) => {
    const nodeType = nodes.find(n => (n.data.class_id || n.data.name) === treeResult.node_type) || nodes.find(n => n.id === currentNodeId);
    
    if (!nodeType) {
      // 找到匹配的节点
      const matchingNode = nodes.find(n => 
        (n.data.class_id === treeResult.node_type || n.data.name === treeResult.node_type) && !nodeResults[n.id]
      );
      
      if (matchingNode) {
        nodeResults[matchingNode.id] = {
          count: treeResult.count,
          results: treeResult.results
        };
        
        // 处理子节点
        if (treeResult.children && treeResult.children.length > 0) {
          treeResult.children.forEach((childResult: any) => {
            // 找到对应关系边
            const edge = edges.find(e => 
              e.source === matchingNode.id && e.label === childResult.relation
            );
            if (edge) {
              mapResultsToNodes(childResult, nodes, edges, nodeResults, edge.target);
            }
          });
        }
      }
    }
  };

  // 执行查询函数（使用 ref 获取最新状态，避免依赖循环）
  const executeGraphQuery = async () => {
    const currentProjectId = projectIdRef.current;
    const currentSelectedOntologyId = selectedOntologyIdRef.current;
    const currentNodes = nodesRefForQuery.current;
    const currentEdges = edgesRefForQuery.current;
    
    console.log('executeGraphQuery called, nodes:', currentNodes.length);
    
    if (!currentProjectId || !currentSelectedOntologyId || currentNodes.length === 0) {
      console.log('executeGraphQuery skipped: no projectId, selectedOntologyId, or nodes');
      return;
    }
    
    if (isQueryLoading) {
      console.log('executeGraphQuery skipped: already loading');
      return;
    }
    
    const queryTrees = buildQueryTrees();
    console.log('executeGraphQuery queryTrees:', queryTrees);
    
    if (!queryTrees || queryTrees.length === 0) {
      console.log('executeGraphQuery skipped: no queryTrees');
      return;
    }
    
    setIsQueryLoading(true);
    
    try {
      const result = await api.queryGraphTrees(
        currentProjectId,
        parseInt(currentSelectedOntologyId),
        ontology?.name || 'server_manufacturing_cog_graph',
        queryTrees
      );
      
      console.log('executeGraphQuery result:', result);
      
      setGraphQueryResult(result);
      
      const newNodeResults: { [nodeId: string]: { count: number; results: string[] } } = {};
      
      // 处理多个查询结果
      const queryResults = result.query_results || [];
      
      // 递归遍历单个树结果
      const traverseAndMap = (treeNode: any, parentNodeId?: string) => {
        // 找到匹配的节点
        let targetNodeId: any;
        if (parentNodeId) {
          // 从父节点通过边找到
          const edge = currentEdges.find(e => 
            e.source === parentNodeId && e.label === treeNode.relation
          );
          if (edge) {
            targetNodeId = edge.target;
          }
        } else {
          // 根节点 - 在当前根节点中找到匹配的
          const rootNode = currentNodes.find(n => 
            !currentEdges.some(e => e.target === n.id) &&
            ((n.data.class_id === treeNode.node_type) || (n.data.name === treeNode.node_type))
          );
          targetNodeId = rootNode?.id;
        }
        
        if (targetNodeId) {
          // 确认节点类型匹配
          const node = currentNodes.find(n => n.id === targetNodeId);
          if (node && (node.data.class_id === treeNode.node_type || node.data.name === treeNode.node_type)) {
            newNodeResults[targetNodeId] = {
              count: treeNode.count,
              results: treeNode.results
            };
            
            // 处理子节点
            if (treeNode.children && treeNode.children.length > 0) {
              treeNode.children.forEach((child: any) => {
                traverseAndMap(child, targetNodeId);
              });
            }
          }
        }
      };
      
      // 遍历每个查询结果树
      queryResults.forEach((treeResult: any) => {
        traverseAndMap(treeResult);
      });
      
      console.log('newNodeResults:', newNodeResults);
      
      setNodeResults(newNodeResults);
      
      // 计算聚合结果
      const newAggregationResults: {
        [nodeId: string]: {
          [aggKey: string]: number;
        };
      } = {};
      
      console.log('=== 开始计算聚合 ===');
      console.log('currentNodes:', currentNodes);
      console.log('newNodeResults:', newNodeResults);
      
      // 遍历所有节点，计算聚合
      currentNodes.forEach(node => {
        const nodeResult = newNodeResults[node.id];
        const nodeAggregations = node.data.config?.aggregations || [];
        
        console.log(`处理节点 ${node.id}:`, {
          hasResult: !!nodeResult,
          aggregations: nodeAggregations
        });
        
        if (nodeResult && nodeAggregations.length > 0) {
          newAggregationResults[node.id] = {};
          
          nodeAggregations.forEach((agg: any) => {
            const aggKey = `${agg.property}_${agg.aggregationType}`;
            
            console.log(`计算聚合 ${aggKey}:`, agg);
            
            // 简单聚合框架
            if (agg.aggregationType === 'count') {
              // count 聚合：直接使用节点结果的 count
              newAggregationResults[node.id][aggKey] = nodeResult.count;
            } else {
              // 其他聚合（sum/avg/min/max）暂时用模拟数据演示
              // 后续需要从图数据库获取实体属性后再计算
              newAggregationResults[node.id][aggKey] = 0;
            }
          });
        }
      });
      
      console.log('newAggregationResults:', newAggregationResults);
      setAggregationResults(newAggregationResults);
      
      setNodes(prevNodes => prevNodes.map(node => {
        const result = newNodeResults[node.id];
        if (result) {
          return {
            ...node,
            data: {
              ...node.data,
              queryCount: result.count
            }
          };
        }
        return node;
      }));
      
    } catch (error) {
      console.error('Failed to execute graph query:', error);
    } finally {
      setIsQueryLoading(false);
    }
  };

  // 把函数赋给 ref
  executeGraphQueryRef.current = executeGraphQuery;

  // 监听节点或边变化，自动触发查询（带防抖）
  useEffect(() => {
    console.log('nodes or edges changed, nodes:', nodes.length, 'edges:', edges.length);
    
    // 清除之前的 timer
    if (queryDebounceTimerRef.current) {
      clearTimeout(queryDebounceTimerRef.current);
    }
    
    // 设置新的 timer，300ms 后执行
    if (nodes.length > 0 && executeGraphQueryRef.current) {
      queryDebounceTimerRef.current = setTimeout(() => {
        console.log('Debounce timer expired, executing query...');
        executeGraphQueryRef.current!();
      }, 300);
    }
    
    // 组件卸载时清除 timer
    return () => {
      if (queryDebounceTimerRef.current) {
        clearTimeout(queryDebounceTimerRef.current);
      }
    };
  }, [nodes.length, edges.length]);

  // 监听过滤条件变化，自动触发查询（带防抖）
  useEffect(() => {
    console.log('filters changed, filters:', filters);
    
    // 清除之前的 timer
    if (queryDebounceTimerRef.current) {
      clearTimeout(queryDebounceTimerRef.current);
    }
    
    // 设置新的 timer，300ms 后执行
    if (nodes.length > 0 && executeGraphQueryRef.current) {
      queryDebounceTimerRef.current = setTimeout(() => {
        console.log('Debounce timer expired, executing query...');
        executeGraphQueryRef.current!();
      }, 300);
    }
    
    // 组件卸载时清除 timer
    return () => {
      if (queryDebounceTimerRef.current) {
        clearTimeout(queryDebounceTimerRef.current);
      }
    };
  }, [filters.length, nodes.length]);

  // 监听聚合条件变化，自动触发查询（带防抖）
  useEffect(() => {
    console.log('aggregations changed, aggregations:', aggregations);
    
    // 清除之前的 timer
    if (queryDebounceTimerRef.current) {
      clearTimeout(queryDebounceTimerRef.current);
    }
    
    // 设置新的 timer，300ms 后执行
    if (nodes.length > 0 && executeGraphQueryRef.current) {
      queryDebounceTimerRef.current = setTimeout(() => {
        console.log('Debounce timer expired, executing query...');
        executeGraphQueryRef.current!();
      }, 300);
    }
    
    // 组件卸载时清除 timer
    return () => {
      if (queryDebounceTimerRef.current) {
        clearTimeout(queryDebounceTimerRef.current);
      }
    };
  }, [aggregations.length, nodes.length]);

  // 获取与选中实体有关系的相邻实体
  const fetchRelatedEntities = (entityId: string) => {
    if (!projectId || !selectedOntologyId) {
      return;
    }
    
    // 从当前本体库中获取关系数据
    api.getOntology(projectId, parseInt(selectedOntologyId))
      .then(ontology => {
        const relations = ontology.relations || [];
        const classes = ontology.classes || [];
        
        // 找到与选中实体相关的关系并去重
        const related = [];
        const addedIds = new Set(); // 用于去重
        
        relations.forEach(relation => {
          if (relation.source_class_id.toString() === entityId) {
            // 找到目标类
            const targetClass = classes.find(c => c.id === relation.target_class_id);
            if (targetClass && !addedIds.has(targetClass.id)) {
              addedIds.add(targetClass.id);
              related.push({
                ...targetClass,
                relationType: relation.relation_type,
                relationDirection: 'outgoing'
              });
            }
          } else if (relation.target_class_id.toString() === entityId) {
            // 找到源类
            const sourceClass = classes.find(c => c.id === relation.source_class_id);
            if (sourceClass && !addedIds.has(sourceClass.id)) {
              addedIds.add(sourceClass.id);
              related.push({
                ...sourceClass,
                relationType: relation.relation_type,
                relationDirection: 'incoming'
              });
            }
          }
        });
        
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
                  type: 'straight',
                  animated: true,
                  style: { stroke: '#94a3b8', strokeWidth: 2 },
                  markerEnd: {
                    type: MarkerType.ArrowClosed,
                    color: '#94a3b8',
                  },
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
            <div className="flex items-center space-x-2">
              <button
                onClick={() => {
                  if (selectedCanvasEntity && window.confirm(`确定要删除节点 "${getSelectedEntityName(selectedCanvasEntity)}" 吗？`)) {
                    setNodes(prevNodes => prevNodes.filter(n => n.id !== selectedCanvasEntity));
                    setEdges(prevEdges => prevEdges.filter(e => e.source !== selectedCanvasEntity && e.target !== selectedCanvasEntity));
                    setSelectedCanvasEntity(null);
                    setShowRightPanel(false);
                  }
                }}
                className="p-2 rounded-md bg-red-50 hover:bg-red-100 border border-red-200"
                title="删除节点"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
              <button
                onClick={() => setShowRightPanel(false)}
                className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 border border-gray-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <div className="space-y-4 p-4">
            <div>
              <h4 className="mb-2 text-xs font-medium text-gray-500">总数</h4>
              <div className="flex items-end justify-between">
                <span className="text-2xl font-bold text-gray-800">
                  {selectedCanvasEntity && nodeResults[selectedCanvasEntity] 
                    ? nodeResults[selectedCanvasEntity].count 
                    : 0}
                </span>
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
                    const newFilter = {
                      property: currentFilter.property,
                      operator: currentFilter.operator,
                      value: currentFilter.value
                    };
                    const newFilters = [...filters, newFilter];
                    setFilters(newFilters);
                    setCurrentFilter({
                      property: '',
                      operator: '=',
                      value: ''
                    });
                    // 立即保存配置到节点
                    const updatedNodes = nodes.map(n => {
                      if (n.id === selectedCanvasEntity) {
                        return {
                          ...n,
                          data: {
                            ...n.data,
                            config: {
                              filters: newFilters,
                              aggregations: aggregations
                            }
                          }
                        };
                      }
                      return n;
                    });
                    setNodes(updatedNodes);
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
                      const cls = selectedCanvasEntity ? ontologyClasses.find(c => c.id.toString() === selectedCanvasEntity) : null;
                      return (
                        <div key={index} className="flex items-center justify-between p-2 bg-gray-100 rounded-md">
                          <span className="text-xs">
                            {cls?.name}.{filter.property} {filter.operator} {filter.value}
                          </span>
                          <button
                            onClick={() => {
                              const newFilters = filters.filter((_, i) => i !== index);
                              setFilters(newFilters);
                              // 立即保存配置到节点
                              const updatedNodes = nodes.map(n => {
                                if (n.id === selectedCanvasEntity) {
                                  return {
                                    ...n,
                                    data: {
                                      ...n.data,
                                      config: {
                                        filters: newFilters,
                                        aggregations: aggregations
                                      }
                                    }
                                  };
                                }
                                return n;
                              });
                              setNodes(updatedNodes);
                            }}
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
                <button 
                  className="flex-1 px-2 py-1 text-xs font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  onClick={() => executeGraphQuery()}
                >
                  应用
                </button>
                <button 
                  className="flex-1 px-2 py-1 text-xs font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-100"
                  onClick={() => {
                    setFilters([]);
                    setCurrentFilter({
                      property: '',
                      operator: '=',
                      value: ''
                    });
                    // 立即保存配置到节点
                    if (selectedCanvasEntity) {
                      const updatedNodes = nodes.map(n => {
                        if (n.id === selectedCanvasEntity) {
                          return {
                            ...n,
                            data: {
                              ...n.data,
                              config: {
                                filters: [],
                                aggregations: aggregations
                              }
                            }
                          };
                        }
                        return n;
                      });
                      setNodes(updatedNodes);
                    }
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
                    const newAggregation = {
                      property: currentAggregation.property,
                      aggregationType: currentAggregation.aggregationType,
                      dimension: currentAggregation.dimension
                    };
                    const newAggregations = [...aggregations, newAggregation];
                    setAggregations(newAggregations);
                    setCurrentAggregation({
                      property: '',
                      aggregationType: 'avg',
                      dimension: 'day'
                    });
                    // 立即保存配置到节点
                    const updatedNodes = nodes.map(n => {
                      if (n.id === selectedCanvasEntity) {
                        return {
                          ...n,
                          data: {
                            ...n.data,
                            config: {
                              filters: n.data.config?.filters || [],
                              aggregations: newAggregations
                            }
                          }
                        };
                      }
                      return n;
                    });
                    setNodes(updatedNodes);
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
                      const cls = selectedCanvasEntity ? ontologyClasses.find(c => c.id.toString() === selectedCanvasEntity) : null;
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
                            onClick={() => {
                              const newAggregations = aggregations.filter((_, i) => i !== index);
                              setAggregations(newAggregations);
                              // 立即保存配置到节点
                              const updatedNodes = nodes.map(n => {
                                if (n.id === selectedCanvasEntity) {
                                  return {
                                    ...n,
                                    data: {
                                      ...n.data,
                                      config: {
                                        filters: n.data.config?.filters || [],
                                        aggregations: newAggregations
                                      }
                                    }
                                  };
                                }
                                return n;
                              });
                              setNodes(updatedNodes);
                            }}
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
              <div className="flex space-x-2 mt-3">
                <button 
                  className="flex-1 px-2 py-1 text-xs font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-100"
                  onClick={() => {
                    setAggregations([]);
                    setCurrentAggregation({
                      property: '',
                      aggregationType: 'avg',
                      dimension: 'day'
                    });
                    // 立即保存配置到节点
                    if (selectedCanvasEntity) {
                      const updatedNodes = nodes.map(n => {
                        if (n.id === selectedCanvasEntity) {
                          return {
                            ...n,
                            data: {
                              ...n.data,
                              config: {
                                filters: n.data.config?.filters || [],
                                aggregations: []
                              }
                            }
                          };
                        }
                        return n;
                      });
                      setNodes(updatedNodes);
                    }
                  }}
                >
                  重置
                </button>
              </div>
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
          
          {/* 聚合结果展示 */}
          {selectedCanvasEntity && (
            <div className="p-4 border-t border-gray-200">
              <h3 className="mb-3 text-sm font-medium text-gray-700">聚合结果</h3>
              <div className="space-y-2">
                {aggregationResults[selectedCanvasEntity] ? (
                  Object.entries(aggregationResults[selectedCanvasEntity]).map(([key, value]) => {
                    const [property, aggType] = key.split('_');
                    const aggTypeMap: Record<string, string> = {
                      avg: '平均值',
                      sum: '总和',
                      count: '计数',
                      min: '最小值',
                      max: '最大值'
                    };
                    return (
                      <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
                        <span className="text-xs text-gray-600">
                          {property} ({aggTypeMap[aggType]})
                        </span>
                        <span className="font-medium text-blue-600">{value}</span>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-xs text-gray-500">暂无聚合结果，请先添加聚合条件并执行查询</div>
                )}
              </div>
            </div>
          )}
          
          {/* 查询结果列表 */}
          {selectedCanvasEntity && nodeResults[selectedCanvasEntity] && (
            <div className="p-4 border-t border-gray-200">
              <h3 className="mb-3 text-sm font-medium text-gray-700">查询结果</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">总数:</span>
                  <span className="font-medium text-green-600">{nodeResults[selectedCanvasEntity].count}</span>
                </div>
                <div className="max-h-48 overflow-y-auto border border-gray-200 rounded-md">
                  {nodeResults[selectedCanvasEntity].results.slice(0, 100).map((result, index) => (
                    <div 
                      key={index}
                      className="px-2 py-1 text-xs border-b border-gray-100 last:border-b-0 hover:bg-gray-50"
                    >
                      {result}
                    </div>
                  ))}
                </div>
                {nodeResults[selectedCanvasEntity].results.length > 100 && (
                  <div className="text-xs text-gray-400 text-center">
                    仅显示前 100 条结果
                  </div>
                )}
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default OntologyExplorer;