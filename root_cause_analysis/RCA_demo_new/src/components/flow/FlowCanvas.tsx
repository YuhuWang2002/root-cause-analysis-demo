import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { useCurrentProjectFlow, useFlowStore, type NodeType, type NodeStatus } from '@/stores/flowStore';

const typeColors: Record<NodeType, { bg: string; border: string; text: string; light: string }> = {
  source: { bg: '#8B5CF6', border: '#A78BFA', text: '#C4B5FD', light: 'rgba(139, 92, 246, 0.15)' },
  acquisition: { bg: '#3B82F6', border: '#60A5FA', text: '#93C5FD', light: 'rgba(59, 130, 246, 0.15)' },
  process: { bg: '#06B6D4', border: '#22D3EE', text: '#67E8F9', light: 'rgba(6, 182, 212, 0.15)' },
  quality: { bg: '#F59E0B', border: '#FBBF24', text: '#FCD34D', light: 'rgba(245, 158, 11, 0.15)' },
  dataset: { bg: '#10B981', border: '#34D399', text: '#6EE7B7', light: 'rgba(16, 185, 129, 0.15)' },
  ontology: { bg: '#EC4899', border: '#F472B6', text: '#F9A8D4', light: 'rgba(236, 72, 153, 0.15)' },
  analysis: { bg: '#EF4444', border: '#F87171', text: '#FCA5A5', light: 'rgba(239, 68, 68, 0.15)' },
};

const COLUMN_WIDTH = 220;
const ROW_HEIGHT = 120;
const START_Y = 60;
const COLUMN_LABELS = ['数据源', '数据获取', '数据处理', '质量约束', '数据集', '本体构建', '数据分析'];

const statusColors: Record<NodeStatus, string> = {
  pending: 'bg-gray-500',
  running: 'bg-blue-500',
  completed: 'bg-green-500',
  configured: 'bg-green-500',
  unconfigured: 'bg-yellow-500',
};

const statusLabels: Record<NodeStatus, string> = {
  pending: '等待中',
  running: '运行中',
  completed: '已完成',
  configured: '已配置',
  unconfigured: '未配置',
};

interface FlowCanvasProps {
  onAddSource: () => void;
  onAddOntology: () => void;
  onAddAnalysis: () => void;
}

export default function FlowCanvas({ onAddSource, onAddOntology, onAddAnalysis }: FlowCanvasProps) {
  const { nodes, connections } = useCurrentProjectFlow();
  const setSelectedNode = useFlowStore(state => state.setSelectedNode);

  const columns = useMemo(() => {
    return COLUMN_LABELS.map((label, colIndex) => {
      const colNodes = nodes.filter(node => {
        const nodeColIndex = Math.round((node.x - 0) / COLUMN_WIDTH);
        return nodeColIndex === colIndex;
      });
      return { label, nodes: colNodes, index: colIndex };
    });
  }, [nodes]);

  const sourceNodes = nodes.filter(n => n.type === 'source');
  const ontologyNodes = nodes.filter(n => n.type === 'ontology');
  const analysisNodes = nodes.filter(n => n.type === 'analysis');
  const buttonY = sourceNodes.length > 0 
    ? sourceNodes[sourceNodes.length - 1].y + ROW_HEIGHT * 1.5 
    : 60;
  const ontologyY = ontologyNodes.length > 0 
    ? ontologyNodes[ontologyNodes.length - 1].y + ROW_HEIGHT * 1.5 
    : START_Y;
  const analysisY = analysisNodes.length > 0 
    ? analysisNodes[analysisNodes.length - 1].y + ROW_HEIGHT * 1.5 
    : START_Y;
  const allYPositions = nodes.length > 0 ? [
    ...nodes.map(n => n.y + 80),
    buttonY + 80,
    analysisY + 80
  ] : [200];
  const maxY = Math.max(...allYPositions);
  const svgHeight = Math.max(maxY + 100, 600);

  const isEmpty = nodes.length === 0;

  if (isEmpty) {
    return (
      <div className="w-full h-full bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 relative overflow-auto">
        <div className="absolute inset-0 flex items-center justify-center z-30">
          <div className="text-center">
            <div className="w-24 h-24 mx-auto mb-6 bg-gray-800 rounded-full flex items-center justify-center">
              <svg className="w-12 h-12 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">开始您的分析</h3>
            <p className="text-gray-400 mb-6 max-w-sm">
              点击下方按钮添加数据源，开始构建您的根因分析流程
            </p>
            <button
              onClick={onAddSource}
              className="px-6 py-3 bg-primary hover:bg-primary-dark text-white rounded-lg transition-colors inline-flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              添加数据源
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 relative overflow-auto">
      <svg 
        className="absolute top-0 left-0 pointer-events-none z-10" 
        style={{ 
          width: COLUMN_WIDTH * 10, 
          height: svgHeight 
        }}
      >
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon
              points="0 0, 10 3.5, 0 7"
              fill="#60A5FA"
            />
          </marker>
        </defs>
        
        {connections.map((conn) => {
          const fromNode = nodes.find(n => n.id === conn.from);
          const toNode = nodes.find(n => n.id === conn.to);
          
          if (!fromNode || !toNode) return null;
          
          const fromColIndex = Math.round((fromNode.x - 0) / COLUMN_WIDTH);
          const toColIndex = Math.round((toNode.x - 0) / COLUMN_WIDTH);
          
          const startX = fromColIndex * COLUMN_WIDTH + 20 + 180;
          const startY = fromNode.y + 48 + 40;
          const endX = toColIndex * COLUMN_WIDTH + 20;
          const endY = toNode.y + 48 + 40;
          
          const path = `M ${startX} ${startY} L ${endX} ${endY}`;
          
          return (
            <path
              key={conn.id}
              d={path}
              fill="none"
              stroke="#60A5FA"
              strokeWidth="2"
              markerEnd="url(#arrowhead)"
            />
          );
        })}
      </svg>
      
      <div className="flex min-w-max relative" style={{ height: svgHeight }}>
        {columns.map((col, colIndex) => (
          <div
            key={colIndex}
            className="flex flex-col border-r border-gray-500"
            style={{ width: COLUMN_WIDTH }}
          >
            <div className="h-12 flex items-center justify-center border-b border-gray-500">
              <span className="text-sm font-bold text-gray-300 uppercase tracking-widest">
                {col.label}
              </span>
            </div>
            
            <div className="flex-1 relative">
              {col.nodes.map((node) => (
                <motion.div
                  key={node.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  whileHover={{ scale: 1.02 }}
                  className="absolute w-[180px] h-[80px] rounded-lg border-2 border-gray-600 transition-all duration-200 cursor-pointer z-20"
                  style={{
                    left: 20,
                    top: node.y,
                    backgroundColor: typeColors[node.type].light,
                    borderColor: typeColors[node.type].border + '60',
                  }}
                  onClick={() => setSelectedNode(node.id)}
                >
                  <div className="p-3 h-full flex flex-col justify-between">
                    <div className="flex items-start justify-between">
                      <span className="text-xs font-semibold text-gray-200 truncate flex-1">
                        {node.name}
                      </span>
                      <div className={`w-2 h-2 rounded-full ${statusColors[node.status]}`} />
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] text-gray-400 truncate flex-1">
                        {node.description || node.detail || ''}
                      </span>
                      <span className="text-[9px] text-green-400 ml-1">
                        {statusLabels[node.status]}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {colIndex === 0 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: nodes.length * 0.05 }}
                  className="absolute w-[180px] h-[80px] z-20"
                  style={{
                    left: 20,
                    top: buttonY,
                  }}
                >
                  <button
                    onClick={onAddSource}
                    className="w-full h-full rounded-lg border-2 border-dashed border-gray-600 hover:border-gray-400 transition-colors flex items-center justify-center group"
                  >
                    <div className="text-gray-500 group-hover:text-gray-300 transition-colors">
                      <svg className="w-8 h-8 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      <span className="text-xs">添加数据源</span>
                    </div>
                  </button>
                </motion.div>
              )}

              {colIndex === 5 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="absolute w-[180px] h-[80px] z-20"
                  style={{
                    left: 20,
                    top: ontologyY,
                  }}
                >
                  <button
                    onClick={onAddOntology}
                    className="w-full h-full rounded-lg border-2 border-dashed border-pink-600 hover:border-pink-400 transition-colors flex items-center justify-center group"
                  >
                    <div className="text-pink-500 group-hover:text-pink-300 transition-colors">
                      <svg className="w-8 h-8 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      <span className="text-xs">添加本体</span>
                    </div>
                  </button>
                </motion.div>
              )}

              {colIndex === 6 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="absolute w-[180px] h-[80px] z-20"
                  style={{
                    left: 20,
                    top: analysisY,
                  }}
                >
                  <button
                    onClick={onAddAnalysis}
                    className="w-full h-full rounded-lg border-2 border-dashed border-red-600 hover:border-red-400 transition-colors flex items-center justify-center group"
                  >
                    <div className="text-red-500 group-hover:text-red-300 transition-colors">
                      <svg className="w-8 h-8 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      <span className="text-xs">添加分析</span>
                    </div>
                  </button>
                </motion.div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
