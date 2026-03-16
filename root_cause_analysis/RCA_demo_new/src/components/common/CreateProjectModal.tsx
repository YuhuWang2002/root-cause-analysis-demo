import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/common/Button';
import { Input, Textarea, Select } from '@/components/common/Input';

const scenarioOptions = [
  { value: 'system_anomaly', label: '系统异常分析' },
  { value: 'performance', label: '性能问题分析' },
  { value: 'quality', label: '质量问题分析' },
  { value: 'custom', label: '自定义场景' },
];

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (name: string, description: string, scenario: string) => void;
}

export function CreateProjectModal({ isOpen, onClose, onConfirm }: CreateProjectModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [scenario, setScenario] = useState('custom');

  const handleConfirm = () => {
    if (name.trim()) {
      onConfirm(name.trim(), description.trim(), scenario);
      setName('');
      setDescription('');
      setScenario('custom');
    }
  };

  const handleClose = () => {
    setName('');
    setDescription('');
    setScenario('custom');
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50"
            onClick={handleClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 m-auto z-50 w-full max-w-lg h-fit p-6"
          >
            <div className="bg-white rounded-xl shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">创建新项目</h2>
                <button
                  onClick={handleClose}
                  className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                <Input
                  label="项目名称"
                  placeholder="请输入项目名称"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  maxLength={50}
                  required
                />

                <Textarea
                  label="项目描述"
                  placeholder="请描述项目的分析目标和背景..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  maxLength={500}
                />

                <Select
                  label="分析场景"
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                  options={scenarioOptions}
                />
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <Button variant="secondary" onClick={handleClose}>
                  取消
                </Button>
                <Button onClick={handleConfirm} disabled={!name.trim()}>
                  创建项目
                </Button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
