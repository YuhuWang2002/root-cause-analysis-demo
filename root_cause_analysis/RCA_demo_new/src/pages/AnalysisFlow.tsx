import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ReactFlowProvider } from '@xyflow/react';
import FlowCanvas from '@/components/flow/FlowCanvas';
import ConfigPanel from '@/components/flow/ConfigPanel';
import { OntologyPanel } from '@/components/flow/OntologyPanel';
import AddNodeModal from '@/components/flow/AddNodeModal';
import AutomationModal from '@/components/flow/AutomationModal';
import PermissionsModal from '@/components/flow/PermissionsModal';
import ToolPalette from '@/components/flow/ToolPalette';
import { useFlowStore, useCurrentProjectFlow } from '@/stores/flowStore';
import { useProjectStore } from '@/stores/projectStore';
import { Button } from '@/components/common/Button';
import * as api from '@/services/api';

export default function AnalysisFlow() {
  const navigate = useNavigate();
  const { id: projectId } = useParams<{ id: string }>();
  const { loadProject, isConfigPanelOpen, isPlaying, togglePlay, openAddModal } = useFlowStore();
  const { nodes, connections } = useCurrentProjectFlow();
  const { projects } = useProjectStore();
  const [showConfirm, setShowConfirm] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');
  const [showAutomation, setShowAutomation] = useState(false);
  const [showPermissions, setShowPermissions] = useState(false);
  
  const currentProject = projects.find(p => p.id === projectId);
  
  useEffect(() => {
    if (projectId) {
      console.log('===== AnalysisFlow useEffect triggered =====');
      console.log('projectId:', projectId);
      console.log('currentProject:', currentProject);
      const scenario = currentProject?.scenario;
      console.log('scenario:', scenario);
      loadProject(projectId, scenario);
    }
  }, [projectId, currentProject, loadProject]);

  useEffect(() => {
    console.log('===== AnalysisFlow nodes/connections changed =====');
    console.log('nodes:', nodes);
    console.log('connections:', connections);
    console.log('nodes.length:', nodes.length);
  }, [nodes, connections]);
  
  const hasChanges = nodes.length > 0;
  
  const handleSave = async () => {
    if (!projectId) return;
    setSaveStatus('saving');
    try {
      await api.saveCanvas(projectId, { nodes, connections });
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 1500);
    } catch (error) {
      console.error('保存失败:', error);
      setSaveStatus('idle');
    }
  };
  
  const handleGoBack = () => {
    if (hasChanges) {
      setShowConfirm(true);
    } else {
      navigate('/');
    }
  };
  
  const handleSaveAndLeave = () => {
    handleSave();
    setTimeout(() => navigate('/'), 600);
  };
  
  const totalNodes = nodes.length;
  const configuredNodes = nodes.filter(n => n.status === 'configured' || n.status === 'completed').length;
  const progress = totalNodes > 0 ? Math.round((configuredNodes / totalNodes) * 100) : 0;

  return (
    <div className="h-screen bg-gray-100 flex flex-col overflow-hidden">
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between flex-shrink-0 min-h-[72px] z-10 relative">
        <div className="flex items-center space-x-4">
          <button
            onClick={handleGoBack}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">{currentProject?.name || '根因分析流程'}</h1>
            <p className="text-sm text-gray-500">{currentProject?.description || '自定义分析'}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
            <button className="p-2 hover:bg-gray-200 rounded-md transition-colors">
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button 
              onClick={togglePlay}
              className={`p-2 rounded-md transition-colors ${isPlaying ? 'bg-primary text-white' : 'hover:bg-gray-200 text-gray-500'}`}
            >
              {isPlaying ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </button>
            <button className="p-2 hover:bg-gray-200 rounded-md transition-colors">
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
          
          <div className="text-sm text-gray-600">
            {configuredNodes} / {totalNodes} 节点
          </div>
          
          <div className="w-40">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-primary rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1 text-right">{progress}%</p>
          </div>
          
          <Button variant="secondary" onClick={handleSave}>
            {saveStatus === 'idle' ? '保存' : saveStatus === 'saving' ? '保存中...' : '已保存'}
          </Button>
          
          <Button variant="secondary" onClick={() => setShowAutomation(true)}>
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            自动化
          </Button>
          
          <Button variant="secondary" onClick={() => setShowPermissions(true)}>
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            权限
          </Button>
        </div>
      </header>
      
      <div className="flex-1 relative overflow-hidden flex">
        <ToolPalette />
        <div className="flex-1 relative">
          <ReactFlowProvider>
            <FlowCanvas 
              onAddSource={() => openAddModal('system')} 
              onAddOntology={() => openAddModal('ontology')} 
              onAddAnalysis={() => openAddModal('analysis')} 
            />
          </ReactFlowProvider>
        </div>
        <ConfigPanel />
        <OntologyPanel />
        <AddNodeModal />
        <AutomationModal isOpen={showAutomation} onClose={() => setShowAutomation(false)} />
        <PermissionsModal isOpen={showPermissions} onClose={() => setShowPermissions(false)} />
        
        {showConfirm && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
            <div className="bg-white rounded-xl p-6 max-w-sm w-full mx-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">保存更改？</h3>
              <p className="text-gray-600 mb-6">您有未保存的更改，请选择操作</p>
              <div className="flex justify-end space-x-3">
                <Button variant="ghost" onClick={() => setShowConfirm(false)}>
                  取消
                </Button>
                <Button variant="secondary" onClick={() => navigate('/')}>
                  不保存离开
                </Button>
                <Button onClick={handleSaveAndLeave}>
                  保存并离开
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
