import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useFlowStore } from '@/stores/flowStore';
import { Button } from '@/components/common/Button';

export default function AddNodeModal() {
  const { isAddModalOpen, addModalType, closeAddModal, addDataSource, addOntology, addAnalysis, currentProjectId, projectsData } = useFlowStore();
  const [formData, setFormData] = useState({ name: '', description: '', connection: '', analysisType: 'ontology_explore', ontologyId: '' });

  if (!isAddModalOpen) return null;

  const handleSubmit = () => {
    if (addModalType === 'source') {
      if (formData.name && formData.connection) {
        addDataSource(formData.name, formData.description, formData.connection);
        setFormData({ name: '', description: '', connection: '', analysisType: 'ontology_explore', ontologyId: '' });
        closeAddModal();
      }
    } else if (addModalType === 'ontology') {
      addOntology(formData.name || '本体库');
      setFormData({ name: '', description: '', connection: '', analysisType: 'ontology_explore', ontologyId: '' });
      closeAddModal();
    } else if (addModalType === 'analysis') {
      addAnalysis(formData.name || getAnalysisLabel(formData.analysisType), formData.analysisType, formData.ontologyId || undefined);
      setFormData({ name: '', description: '', connection: '', analysisType: 'ontology_explore', ontologyId: '' });
      closeAddModal();
    }
  };

  const isOntology = addModalType === 'ontology';
  const isAnalysis = addModalType === 'analysis';

  const projectData = currentProjectId ? projectsData[currentProjectId] : null;
  const ontologyNodes = projectData?.nodes.filter(n => n.type === 'ontology') || [];

  const analysisTypes = [
    { value: 'ontology_explore', label: '本体探索' },
    { value: 'data_analysis', label: '数据分析' },
    { value: 'root_cause', label: '根因分析' },
  ];

  const getAnalysisLabel = (type: string) => {
    return analysisTypes.find(t => t.value === type)?.label || '分析';
  };

  return (
    <AnimatePresence>
      {isAddModalOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={closeAddModal}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            className="bg-gray-800 rounded-xl p-6 w-96 border border-gray-700"
            onClick={e => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold text-white mb-4">
              {isAnalysis ? '添加分析' : isOntology ? '添加本体' : '添加数据源'}
            </h3>
            
            <div className="space-y-4">
              {isAnalysis && (
                <div>
                  <label className="block text-sm text-gray-400 mb-1">分析类型</label>
                  <select
                    value={formData.analysisType}
                    onChange={(e) => setFormData({ ...formData, analysisType: e.target.value, name: '' })}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary"
                  >
                    {analysisTypes.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
              )}

              {isAnalysis && ontologyNodes.length > 0 && (
                <div>
                  <label className="block text-sm text-gray-400 mb-1">关联本体库</label>
                  <select
                    value={formData.ontologyId}
                    onChange={(e) => setFormData({ ...formData, ontologyId: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary"
                  >
                    <option value="">自动选择第一个本体</option>
                    {ontologyNodes.map(n => (
                      <option key={n.id} value={n.id}>{n.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm text-gray-400 mb-1">名称</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  placeholder={isAnalysis ? `如：${getAnalysisLabel(formData.analysisType)}` : isOntology ? '如：系统异常本体' : '如：采购系统'}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
                />
              </div>
              
              {!isOntology && !isAnalysis && (
                <>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">描述</label>
                    <input
                      type="text"
                      value={formData.description}
                      onChange={e => setFormData({ ...formData, description: e.target.value })}
                      placeholder="如：企业采购管理数据库"
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">连接信息</label>
                    <input
                      type="text"
                      value={formData.connection}
                      onChange={e => setFormData({ ...formData, connection: e.target.value })}
                      placeholder="如：MySQL | 192.168.1.10:3306"
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
                    />
                  </div>
                </>
              )}
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="ghost" onClick={closeAddModal}>取消</Button>
              <Button 
                onClick={handleSubmit} 
                disabled={!isOntology && !isAnalysis && (!formData.name || !formData.connection)}
              >
                添加
              </Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
