import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useFlowStore } from '@/stores/flowStore';
import { Button } from '@/components/common/Button';

interface AutomationConfig {
  enabled: boolean;
  frequency: 'manual' | 'hourly' | 'daily' | 'weekly' | 'event';
  time?: string;
  eventTrigger?: string;
  notifyOnComplete: boolean;
  notifyEmail?: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function AutomationModal({ isOpen, onClose }: Props) {
  const { currentProjectId, projectsData, updateProjectAutomation } = useFlowStore();
  const [config, setConfig] = useState<AutomationConfig>({
    enabled: false,
    frequency: 'daily',
    notifyOnComplete: false,
    eventTrigger: 'data_updated',
  });

  const projectData = currentProjectId ? projectsData[currentProjectId] : null;
  const existingConfig = projectData?.automation;

  const handleSave = () => {
    if (currentProjectId) {
      updateProjectAutomation(currentProjectId, config);
    }
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            className="bg-gray-800 rounded-xl p-6 w-[480px] border border-gray-700 max-h-[80vh] overflow-y-auto"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-white">自动化配置</h3>
              <button
                onClick={onClose}
                className="p-1 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-white font-medium">自动执行</h4>
                  <p className="text-sm text-gray-400">启用后系统将自动执行分析</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.enabled}
                    onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">执行频率</label>
                <select
                  value={config.frequency}
                  onChange={(e) => setConfig({ ...config, frequency: e.target.value as any })}
                  disabled={!config.enabled}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary disabled:opacity-50"
                >
                  <option value="manual">手动执行</option>
                  <option value="hourly">每小时</option>
                  <option value="daily">每天</option>
                  <option value="weekly">每周</option>
                  <option value="event">事件触发</option>
                </select>
              </div>

              {config.frequency === 'event' && (
                <div>
                  <label className="block text-sm text-gray-400 mb-2">触发事件</label>
                  <select
                    value={config.eventTrigger}
                    onChange={(e) => setConfig({ ...config, eventTrigger: e.target.value })}
                    disabled={!config.enabled}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary disabled:opacity-50"
                  >
                    <option value="data_updated">数据更新</option>
                    <option value="data_added">新增数据</option>
                    <option value="quality_failed">质量检查失败</option>
                    <option value="scheduled">定时任务完成</option>
                  </select>
                </div>
              )}

              {config.frequency !== 'manual' && config.frequency !== 'hourly' && (
                <div>
                  <label className="block text-sm text-gray-400 mb-2">执行时间</label>
                  <input
                    type="time"
                    value={config.time || '00:00'}
                    onChange={(e) => setConfig({ ...config, time: e.target.value })}
                    disabled={!config.enabled}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-primary disabled:opacity-50"
                  />
                </div>
              )}

              <div className="border-t border-gray-700 pt-4">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="text-white font-medium">通知设置</h4>
                    <p className="text-sm text-gray-400">执行完成后发送通知</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.notifyOnComplete}
                      onChange={(e) => setConfig({ ...config, notifyOnComplete: e.target.checked })}
                      disabled={!config.enabled}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary disabled:opacity-50"></div>
                  </label>
                </div>

                {config.notifyOnComplete && (
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">通知邮箱</label>
                    <input
                      type="email"
                      value={config.notifyEmail || ''}
                      onChange={(e) => setConfig({ ...config, notifyEmail: e.target.value })}
                      placeholder="example@company.com"
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
                    />
                  </div>
                )}
              </div>

              <div className="border-t border-gray-700 pt-4">
                <h4 className="text-white font-medium mb-3">执行范围</h4>
                <div className="space-y-2">
                  <label className="flex items-center space-x-2">
                    <input type="checkbox" defaultChecked className="rounded bg-gray-700 border-gray-600" />
                    <span className="text-sm text-gray-300">数据获取</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input type="checkbox" defaultChecked className="rounded bg-gray-700 border-gray-600" />
                    <span className="text-sm text-gray-300">数据处理</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input type="checkbox" defaultChecked className="rounded bg-gray-700 border-gray-600" />
                    <span className="text-sm text-gray-300">质量约束检查</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input type="checkbox" defaultChecked className="rounded bg-gray-700 border-gray-600" />
                    <span className="text-sm text-gray-300">本体构建</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input type="checkbox" className="rounded bg-gray-700 border-gray-600" />
                    <span className="text-sm text-gray-300">数据分析</span>
                  </label>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="ghost" onClick={onClose}>取消</Button>
              <Button onClick={handleSave}>保存配置</Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
