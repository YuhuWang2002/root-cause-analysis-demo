import { useFlowStore, type NodeType } from '@/stores/flowStore';

interface ToolItem {
  type: NodeType;
  label: string;
  color: string;
  allowedZones: string[];
}

const toolItems: ToolItem[] = [
  { type: 'system', label: '源系统', color: '#8B5CF6', allowedZones: ['source'] },
  { type: 'acquisition', label: '数据表', color: '#3B82F6', allowedZones: ['pipeline'] },
  { type: 'datapipeline', label: 'DataPipeline', color: '#06B6D4', allowedZones: ['pipeline'] },
  { type: 'quality', label: '质量约束', color: '#F59E0B', allowedZones: ['pipeline'] },
  { type: 'dataset', label: '数据集', color: '#10B981', allowedZones: ['dataset'] },
  { type: 'ontology', label: '本体构建', color: '#EC4899', allowedZones: ['analysis'] },
  { type: 'ontologyExplore', label: '本体探索', color: '#F472B6', allowedZones: ['analysis'] },
  { type: 'analysis', label: '数据分析', color: '#EF4444', allowedZones: ['analysis'] },
  { type: 'rootCause', label: '根因分析', color: '#7C3AED', allowedZones: ['analysis'] },
];

export default function ToolPalette() {
  const { openAddModal } = useFlowStore();

  const handleDragStart = (e: React.DragEvent, type: NodeType) => {
    e.dataTransfer.setData('application/reactflow', type);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', type);
  };

  const handleClick = (type: NodeType) => {
    if (type === 'system') {
      openAddModal('system');
    } else if (type === 'dataset') {
      openAddModal('dataset');
    } else if (type === 'ontology') {
      openAddModal('ontology');
    } else if (type === 'ontologyExplore') {
      openAddModal('ontology');
    } else if (type === 'analysis') {
      openAddModal('analysis');
    }
  };

  return (
    <div className="w-20 bg-white border-r border-gray-200 flex flex-col items-center py-4 z-30 overflow-y-auto">
      <h3 className="text-xs font-medium text-gray-500 mb-4 uppercase tracking-wider flex-shrink-0">工具</h3>
      
      <div className="space-y-3 w-full px-2 flex flex-col items-center">
        {toolItems.map((item) => (
          <div
            key={item.type}
            draggable
            onDragStart={(e) => handleDragStart(e, item.type)}
            onClick={() => handleClick(item.type)}
            className="group flex flex-col items-center cursor-grab active:cursor-grabbing p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center mb-1 shadow-lg"
              style={{ backgroundColor: item.color }}
            >
              {item.type === 'system' && (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              )}
              {item.type === 'acquisition' && (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              )}
              {item.type === 'datapipeline' && (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              )}
              {item.type === 'quality' && (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
              {item.type === 'rootCause' && (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              )}
              {item.type === 'dataset' && (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                </svg>
              )}
              {item.type === 'ontology' && (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
              )}
              {item.type === 'ontologyExplore' && (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              )}
              {item.type === 'analysis' && (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              )}
            </div>
            <span className="text-[10px] text-gray-500 group-hover:text-gray-700 text-center">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
