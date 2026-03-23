import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { StepIndicator } from '@/components/common/StepIndicator';
import { Button } from '@/components/common/Button';
import { Input, Select, Textarea } from '@/components/common/Input';
import { Card } from '@/components/common/Card';
import { useWizardStore } from '@/stores/wizardStore';
import { useProjectStore } from '@/stores/projectStore';
import type { DataSource, QualityConstraint } from '@/types';

const steps = [
  { title: '基本信息' },
  { title: '数据源配置' },
  { title: '数据权限' },
  { title: '数据转换' },
  { title: '质量约束' },
  { title: '本体构建' },
  { title: '分析配置' },
];

const dataSourceTypes = [
  { value: 'mysql', label: 'MySQL' },
  { value: 'postgresql', label: 'PostgreSQL' },
  { value: 'mongodb', label: 'MongoDB' },
  { value: 'api', label: 'API 接口' },
  { value: 'csv', label: 'CSV 文件' },
];

const scenarioOptions = [
  { value: 'system_anomaly', label: '系统异常分析' },
  { value: 'performance', label: '性能问题分析' },
  { value: 'quality', label: '质量问题分析' },
  { value: 'custom', label: '自定义场景' },
];

function StepBasicInfo() {
  const { projectName, projectDescription, scenario, setProjectName, setProjectDescription, setScenario } = useWizardStore();
  
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">基本信息</h2>
        <p className="text-gray-500 text-sm">定义分析项目的基本信息</p>
      </div>
      
      <Input
        label="项目名称"
        placeholder="请输入项目名称"
        value={projectName}
        onChange={(e) => setProjectName(e.target.value)}
        maxLength={50}
      />
      
      <Textarea
        label="项目描述"
        placeholder="请描述项目的分析目标和背景..."
        value={projectDescription}
        onChange={(e) => setProjectDescription(e.target.value)}
        maxLength={500}
      />
      
      <Select
        label="分析场景"
        value={scenario}
        onChange={(e) => setScenario(e.target.value)}
        options={scenarioOptions}
      />
    </motion.div>
  );
}

function StepDataSource() {
  const { dataSources, addDataSource, removeDataSource } = useWizardStore();
  const [newSource, setNewSource] = useState<{ type: DataSource['type']; name: string; host: string; port: number; database: string; username: string; password: string }>({ type: 'mysql', name: '', host: '', port: 3306, database: '', username: '', password: '' });
  
  const handleAdd = () => {
    if (newSource.name && newSource.host) {
      addDataSource({ ...newSource, id: Date.now().toString() } as DataSource);
      setNewSource({ type: 'mysql', name: '', host: '', port: 3306, database: '', username: '', password: '' });
    }
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">数据源配置</h2>
        <p className="text-gray-500 text-sm">配置要分析的数据来源</p>
      </div>
      
      <Card className="p-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="数据源名称"
            placeholder="命名此数据源"
            value={newSource.name}
            onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
          />
          <Select
            label="数据类型"
            value={newSource.type}
            onChange={(e) => setNewSource({ ...newSource, type: e.target.value as any })}
            options={dataSourceTypes}
          />
          <Input
            label="主机地址"
            placeholder="localhost"
            value={newSource.host}
            onChange={(e) => setNewSource({ ...newSource, host: e.target.value })}
          />
          <Input
            label="端口"
            type="number"
            value={newSource.port}
            onChange={(e) => setNewSource({ ...newSource, port: parseInt(e.target.value) })}
          />
          <Input
            label="数据库名"
            placeholder="database"
            value={newSource.database}
            onChange={(e) => setNewSource({ ...newSource, database: e.target.value })}
          />
          <Input
            label="用户名"
            placeholder="root"
            value={newSource.username}
            onChange={(e) => setNewSource({ ...newSource, username: e.target.value })}
          />
          <div className="col-span-2">
            <Input
              label="密码"
              type="password"
              placeholder="请输入密码"
              value={newSource.password}
              onChange={(e) => setNewSource({ ...newSource, password: e.target.value })}
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <Button onClick={handleAdd} disabled={!newSource.name || !newSource.host}>
            添加数据源
          </Button>
        </div>
      </Card>
      
      {dataSources.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-700">已添加的数据源</h3>
          {dataSources.map((source) => (
            <Card key={source.id} className="p-3 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{source.name}</p>
                  <p className="text-xs text-gray-500">{source.type} • {source.host}</p>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={() => removeDataSource(source.id)}>
                删除
              </Button>
            </Card>
          ))}
        </div>
      )}
    </motion.div>
  );
}

function StepDataPermission() {
  const sampleTables = [
    { name: 'users', fields: ['id', 'name', 'email', 'created_at'] },
    { name: 'orders', fields: ['id', 'user_id', 'amount', 'status', 'created_at'] },
    { name: 'logs', fields: ['id', 'user_id', 'action', 'timestamp'] },
  ];
  const [selectedTables, setSelectedTables] = useState<string[]>([]);
  
  const toggleTable = (tableName: string) => {
    setSelectedTables(prev => 
      prev.includes(tableName) 
        ? prev.filter(t => t !== tableName)
        : [...prev, tableName]
    );
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">数据权限配置</h2>
        <p className="text-gray-500 text-sm">选择需要读取的表和字段</p>
      </div>
      
      <div className="space-y-4">
        {sampleTables.map((table) => (
          <Card key={table.name} className="p-4">
            <div className="flex items-center justify-between mb-3">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedTables.includes(table.name)}
                  onChange={() => toggleTable(table.name)}
                  className="w-4 h-4 text-primary rounded border-gray-300 focus:ring-primary"
                />
                <span className="font-medium text-gray-900">{table.name}</span>
              </label>
            </div>
            <div className="flex flex-wrap gap-2">
              {table.fields.map((field) => (
                <span
                  key={field}
                  className={`px-2 py-1 text-xs rounded ${
                    selectedTables.includes(table.name)
                      ? 'bg-primary/10 text-primary'
                      : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {field}
                </span>
              ))}
            </div>
          </Card>
        ))}
      </div>
      
      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600">
          已选择 <span className="font-medium text-primary">{selectedTables.length}</span> 个表
        </p>
      </div>
    </motion.div>
  );
}

function StepDataTransform() {
  const { dataTransform, setDataTransform } = useWizardStore();
  
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">数据转换配置</h2>
        <p className="text-gray-500 text-sm">配置数据转换和存储方式</p>
      </div>
      
      <Select
        label="输出格式"
        value={dataTransform.outputFormat}
        onChange={(e) => setDataTransform({ ...dataTransform, outputFormat: e.target.value as any })}
        options={[
          { value: 'json', label: 'JSON' },
          { value: 'parquet', label: 'Parquet' },
          { value: 'delta', label: 'Delta Lake' },
        ]}
      />
      
      <Input
        label="存储位置"
        placeholder="s3://bucket/path 或本地路径"
        value={dataTransform.storageLocation}
        onChange={(e) => setDataTransform({ ...dataTransform, storageLocation: e.target.value })}
      />
      
      <Select
        label="调度方式"
        value={dataTransform.schedule}
        onChange={(e) => setDataTransform({ ...dataTransform, schedule: e.target.value as any })}
        options={[
          { value: 'immediate', label: '立即执行' },
          { value: 'scheduled', label: '定时执行' },
          { value: 'manual', label: '手动触发' },
        ]}
      />
    </motion.div>
  );
}

function StepQualityConstraint() {
  const { qualityConstraints, addQualityConstraint, removeQualityConstraint } = useWizardStore();
  const [newConstraint, setNewConstraint] = useState<{ type: QualityConstraint['type']; table: string; field: string; alertLevel: QualityConstraint['alertLevel'] }>({ type: 'not_null', table: 'users', field: 'id', alertLevel: 'warning' });
  
  const handleAdd = () => {
    addQualityConstraint({ ...newConstraint, id: Date.now().toString(), condition: '', enabled: true } as QualityConstraint);
  };
  
  const constraintTypes = [
    { value: 'not_null', label: '非空检查' },
    { value: 'unique', label: '唯一性检查' },
    { value: 'range', label: '范围检查' },
    { value: 'format', label: '格式检查' },
  ];
  
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">数据质量约束</h2>
        <p className="text-gray-500 text-sm">配置数据质量检查规则</p>
      </div>
      
      <Card className="p-4">
        <div className="grid grid-cols-3 gap-4">
          <Select
            label="约束类型"
            value={newConstraint.type}
            onChange={(e) => setNewConstraint({ ...newConstraint, type: e.target.value as any })}
            options={constraintTypes}
          />
          <Select
            label="数据表"
            value={newConstraint.table}
            onChange={(e) => setNewConstraint({ ...newConstraint, table: e.target.value })}
            options={[
              { value: 'users', label: 'users' },
              { value: 'orders', label: 'orders' },
              { value: 'logs', label: 'logs' },
            ]}
          />
          <Select
            label="告警级别"
            value={newConstraint.alertLevel}
            onChange={(e) => setNewConstraint({ ...newConstraint, alertLevel: e.target.value as any })}
            options={[
              { value: 'info', label: '信息' },
              { value: 'warning', label: '警告' },
              { value: 'error', label: '错误' },
            ]}
          />
        </div>
        <div className="mt-4 flex justify-end">
          <Button onClick={handleAdd}>添加约束</Button>
        </div>
      </Card>
      
      {qualityConstraints.length > 0 && (
        <div className="space-y-2">
          {qualityConstraints.map((c) => (
            <Card key={c.id} className="p-3 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className={`px-2 py-0.5 text-xs rounded ${
                  c.alertLevel === 'error' ? 'bg-red-100 text-red-700' :
                  c.alertLevel === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-blue-100 text-blue-700'
                }`}>
                  {c.alertLevel}
                </span>
                <span className="text-sm">{c.type} - {c.table}.{c.field}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={() => removeQualityConstraint(c.id)}>删除</Button>
            </Card>
          ))}
        </div>
      )}
    </motion.div>
  );
}

function StepOntology() {
  const { ontology, setOntology } = useWizardStore();
  
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">本体构建</h2>
        <p className="text-gray-500 text-sm">构建分析所需的本体模型</p>
      </div>
      
      <Select
        label="本体类型"
        value={ontology.type}
        onChange={(e) => setOntology({ ...ontology, type: e.target.value as any })}
        options={[
          { value: 'event', label: '事件本体' },
          { value: 'causal', label: '因果本体' },
          { value: 'hierarchy', label: '层次本体' },
        ]}
      />
      
      <div className="p-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center min-h-[200px]">
        <div className="text-center">
          <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
          <p className="text-sm text-gray-500">本体可视化预览区域</p>
          <p className="text-xs text-gray-400 mt-1">将在构建后显示</p>
        </div>
      </div>
    </motion.div>
  );
}

function StepAnalysis() {
  const { analysisConfig, setAnalysisConfig } = useWizardStore();
  
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">分析配置</h2>
        <p className="text-gray-500 text-sm">配置分析方法和算法参数</p>
      </div>
      
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700">分析方法</label>
        <div className="flex flex-wrap gap-3">
          {[
            { value: 'causal_analysis', label: '因果分析' },
            { value: 'root_cause', label: '根因识别' },
            { value: 'correlation', label: '关联分析' },
          ].map((method) => (
            <label key={method.value} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={analysisConfig.methods.includes(method.value as any)}
                onChange={(e) => {
                  const methods = e.target.checked
                    ? [...analysisConfig.methods, method.value as any]
                    : analysisConfig.methods.filter(m => m !== method.value);
                  setAnalysisConfig({ ...analysisConfig, methods });
                }}
                className="w-4 h-4 text-primary rounded border-gray-300 focus:ring-primary"
              />
              <span className="text-sm text-gray-700">{method.label}</span>
            </label>
          ))}
        </div>
      </div>
      
      <Select
        label="算法选择"
        value={analysisConfig.algorithm}
        onChange={(e) => setAnalysisConfig({ ...analysisConfig, algorithm: e.target.value as any })}
        options={[
          { value: 'pc', label: 'PC 算法' },
          { value: 'fci', label: 'FCI 算法' },
          { value: 'grasp', label: 'GRaSP 算法' },
        ]}
      />
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium text-gray-700 mb-1.5 block">置信度阈值</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={analysisConfig.parameters.confidenceThreshold}
            onChange={(e) => setAnalysisConfig({
              ...analysisConfig,
              parameters: { ...analysisConfig.parameters, confidenceThreshold: parseFloat(e.target.value) }
            })}
            className="w-full"
          />
          <p className="text-xs text-gray-500 mt-1">{analysisConfig.parameters.confidenceThreshold}</p>
        </div>
        <div>
          <label className="text-sm font-medium text-gray-700 mb-1.5 block">最大因果路径长度</label>
          <input
            type="number"
            min="1"
            max="10"
            value={analysisConfig.parameters.maxPathLength}
            onChange={(e) => setAnalysisConfig({
              ...analysisConfig,
              parameters: { ...analysisConfig.parameters, maxPathLength: parseInt(e.target.value) }
            })}
            className="w-full px-4 py-2 border border-gray-300 rounded-md"
          />
        </div>
      </div>
      
      <Select
        label="输出格式"
        value={analysisConfig.outputFormat}
        onChange={(e) => setAnalysisConfig({ ...analysisConfig, outputFormat: e.target.value as any })}
        options={[
          { value: 'json', label: 'JSON' },
          { value: 'csv', label: 'CSV' },
          { value: 'report', label: '分析报告' },
        ]}
      />
    </motion.div>
  );
}

const stepComponents = [StepBasicInfo, StepDataSource, StepDataPermission, StepDataTransform, StepQualityConstraint, StepOntology, StepAnalysis];

export default function CreateProject() {
  const navigate = useNavigate();
  const { currentStep, totalSteps, nextStep, prevStep, setStep, projectName, scenario, reset } = useWizardStore();
  const { addProject } = useProjectStore();
  
  const StepComponent = stepComponents[currentStep];
  
  const handleCreate = () => {
    addProject({
      name: projectName || '新项目',
      description: useWizardStore.getState().projectDescription,
      scenario: scenario || 'custom',
      status: 'draft',
      progress: 0,
    });
    reset();
    navigate('/');
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="mb-8">
          <StepIndicator steps={steps} currentStep={currentStep} onStepClick={setStep} />
        </div>
        
        <Card className="p-8">
          <AnimatePresence mode="wait">
            <StepComponent key={currentStep} />
          </AnimatePresence>
          
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
            <Button
              variant="ghost"
              onClick={prevStep}
              disabled={currentStep === 0}
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              上一步
            </Button>
            
            <div className="flex space-x-3">
              <Button variant="secondary" onClick={() => navigate('/')}>
                取消
              </Button>
              {currentStep === totalSteps - 1 ? (
                <Button onClick={handleCreate}>
                  创建项目
                  <svg className="w-5 h-5 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </Button>
              ) : (
                <Button onClick={nextStep}>
                  下一步
                  <svg className="w-5 h-5 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Button>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
