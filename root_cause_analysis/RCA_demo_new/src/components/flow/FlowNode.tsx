import { Handle, Position, type NodeProps } from '@xyflow/react';
import { motion } from 'framer-motion';
import { type NodeStatus } from '@/stores/flowStore';

interface FlowNodeData {
  label: string;
  description?: string;
  status: NodeStatus;
  detail?: string;
  nodeType: string;
  colors: {
    bg: string;
    border: string;
    text: string;
    light: string;
  };
  onClick?: () => void;
}

export default function FlowNode({ id, data, selected }: NodeProps<FlowNodeData>) {
  const { label, description, status, detail, colors, onClick } = data;

  const statusColors = {
    pending: 'bg-gray-500',
    running: 'bg-blue-500',
    completed: 'bg-green-500',
    configured: 'bg-green-500',
    unconfigured: 'bg-yellow-500',
  };

  const statusLabels = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    configured: '已配置',
    unconfigured: '未配置',
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className={`
        relative w-[180px] h-[80px] rounded-lg border-2 
        ${selected ? 'border-white shadow-lg shadow-white/20' : 'border-gray-600'}
        transition-all duration-200 cursor-pointer
      `}
      style={{
        backgroundColor: colors.light,
        borderColor: selected ? colors.border : colors.border + '60',
      }}
      onClick={onClick}
    >
      {/* 左侧连接点 */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-gray-400 !border-2 !border-gray-600"
      />

      {/* 右侧连接点 */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-gray-400 !border-2 !border-gray-600"
      />

      {/* 内容 */}
      <div className="p-3 h-full flex flex-col justify-between">
        <div className="flex items-start justify-between">
          <span className="text-xs font-semibold text-gray-200 truncate flex-1">
            {label}
          </span>
          <div className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-gray-400 truncate flex-1">
            {description || detail || ''}
          </span>
          <span className="text-[9px] text-green-400 ml-1">
            {statusLabels[status]}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
