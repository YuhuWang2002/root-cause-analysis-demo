import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useFlowStore, type NodeStatus, type NodeType } from '@/stores/flowStore';
import { useProjectStore } from '@/stores/projectStore';
import { useOntologyStore } from '@/stores/ontologyStore';
import { Button } from '@/components/common/Button';
import { Input, Select, Textarea } from '@/components/common/Input';
import * as api from '@/services/api';

const typeColors: Record<string, { bg: string; light: string; label: string }> = {
  system: { bg: '#8B5CF6', light: 'rgba(139, 92, 246, 0.15)', label: '源系统' },
  acquisition: { bg: '#3B82F6', light: 'rgba(59, 130, 246, 0.15)', label: '数据获取' },
  datapipeline: { bg: '#06B6D4', light: 'rgba(6, 182, 212, 0.15)', label: 'DataPipeline' },
  quality: { bg: '#F59E0B', light: 'rgba(245, 158, 11, 0.15)', label: '质量约束' },
  dataset: { bg: '#10B981', light: 'rgba(16, 185, 129, 0.15)', label: '数据集' },
  ontology: { bg: '#EC4899', light: 'rgba(236, 72, 153, 0.15)', label: '本体构建' },
  ontologyExplore: { bg: '#F472B6', light: 'rgba(244, 114, 182, 0.15)', label: '本体探索' },
  analysis: { bg: '#EF4444', light: 'rgba(239, 68, 68, 0.15)', label: '数据分析' },
  rootCause: { bg: '#7C3AED', light: 'rgba(124, 58, 237, 0.15)', label: '根因分析' },
};

const statusLabels: Record<NodeStatus, string> = {
  pending: '等待中',
  running: '运行中',
  completed: '已完成',
  configured: '已配置',
  unconfigured: '未配置',
};

const systemTypeOptions = [
  { value: 'SAP', label: 'SAP ERP' },
  { value: 'Oracle', label: 'Oracle EBS' },
  { value: 'Salesforce', label: 'Salesforce' },
  { value: 'MES', label: 'MES 制造执行系统' },
  { value: 'WMS', label: 'WMS 仓储管理系统' },
  { value: 'CRM', label: 'CRM 客户关系管理' },
  { value: 'HRM', label: 'HRM 人力资源管理' },
  { value: 'OA', label: 'OA 办公自动化' },
  { value: 'API', label: 'API 接口' },
];

function SystemConfig({ node, onSave }: { node: any; onSave: (config: Record<string, unknown>) => void }) {
  const [config, setConfig] = useState({
    systemType: node.config?.systemType || 'SAP',
    address: node.config?.address || '',
    description: node.config?.description || '',
  });

  const handleSystemTypeChange = (value: string) => {
    const systemLabel = systemTypeOptions.find(o => o.value === value)?.label || value;
    setConfig({ ...config, systemType: value });
    onSave({
      ...config,
      systemType: value,
      _displayName: systemLabel,
    });
  };

  const handleSubmit = () => {
    const systemLabel = systemTypeOptions.find(o => o.value === config.systemType)?.label || config.systemType;
    onSave({
      ...config,
      _displayName: systemLabel,
    });
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm text-gray-400 mb-2">选择企业系统</label>
        <Select
          value={config.systemType}
          onChange={(e) => handleSystemTypeChange(e.target.value)}
          options={systemTypeOptions}
        />
      </div>

      <Input
        label="系统地址"
        value={config.address}
        onChange={(e) => setConfig({ ...config, address: e.target.value })}
        placeholder="https://system.company.com"
      />

      <Input
        label="系统描述"
        value={config.description}
        onChange={(e) => setConfig({ ...config, description: e.target.value })}
        placeholder="简要描述该系统"
      />

      <Button onClick={handleSubmit} className="w-full">保存配置</Button>
    </div>
  );
}

function AcquisitionConfig({ node, onSave }: { node: any; onSave: (config: Record<string, unknown>) => void }) {
  const [tables, setTables] = useState<string[]>(node.config?.tables || []);
  const [newTable, setNewTable] = useState('');

  const handleAddTable = () => {
    if (newTable && !tables.includes(newTable)) {
      setTables([...tables, newTable]);
      setNewTable('');
    }
  };

  const handleSave = () => {
    onSave({ tables });
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm text-gray-400 mb-2">选择数据表</label>
        <div className="flex gap-2">
          <Input
            value={newTable}
            onChange={(e) => setNewTable(e.target.value)}
            placeholder="输入表名"
          />
          <Button size="sm" onClick={handleAddTable}>添加</Button>
        </div>
      </div>

      {tables.length > 0 && (
        <div className="space-y-2">
          <label className="text-xs text-gray-500 uppercase tracking-wider">已选表 ({tables.length})</label>
          <div className="flex flex-wrap gap-2">
            {tables.map((table) => (
              <span
                key={table}
                className="inline-flex items-center px-2.5 py-1 rounded-full text-xs bg-blue-900/50 text-blue-300"
              >
                {table}
                <button
                  onClick={() => setTables(tables.filter(t => t !== table))}
                  className="ml-1.5 text-blue-400 hover:text-blue-200"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      <Button onClick={handleSave} className="w-full">
        保存配置
      </Button>
    </div>
  );
}

function ProcessConfig({ node, onSave }: { node: any; onSave: (config: Record<string, unknown>) => void }) {
  const [transforms, setTransforms] = useState<{ from: string; to: string; type: string }[]>(
    node.config?.transforms || []
  );
  const [filters, setFilters] = useState<string[]>(node.config?.filters || []);

  const handleAddTransform = () => {
    setTransforms([...transforms, { from: '', to: '', type: 'rename' }]);
  };

  const handleSave = () => {
    onSave({ transforms, filters });
  };

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm text-gray-400">字段转换规则</label>
          <Button size="sm" variant="ghost" onClick={handleAddTransform}>+ 添加</Button>
        </div>
        {transforms.map((t, i) => (
          <div key={i} className="flex gap-2 mb-2">
            <Input
              value={t.from}
              onChange={(e) => {
                const newT = [...transforms];
                newT[i].from = e.target.value;
                setTransforms(newT);
              }}
              placeholder="原字段"
            />
            <Input
              value={t.to}
              onChange={(e) => {
                const newT = [...transforms];
                newT[i].to = e.target.value;
                setTransforms(newT);
              }}
              placeholder="新字段"
            />
          </div>
        ))}
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-2">过滤条件</label>
        <Textarea
          value={filters.join('\n')}
          onChange={(e) => setFilters(e.target.value.split('\n').filter(f => f))}
          placeholder="每行一个条件，如: status = 'active'"
          rows={4}
        />
      </div>

      <Button onClick={handleSave} className="w-full">
        保存配置
      </Button>
    </div>
  );
}

function QualityConfig({ node, onSave }: { node: any; onSave: (config: Record<string, unknown>) => void }) {
  const [rules, setRules] = useState<{ field: string; type: string; value: string }[]>(
    node.config?.rules || []
  );

  const ruleTypes = [
    { value: 'not_null', label: '非空检查' },
    { value: 'unique', label: '唯一性检查' },
    { value: 'range', label: '范围检查' },
    { value: 'regex', label: '正则匹配' },
  ];

  const handleAddRule = () => {
    setRules([...rules, { field: '', type: 'not_null', value: '' }]);
  };

  const handleSave = () => {
    onSave({ rules });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm text-gray-400">质量规则</label>
        <Button size="sm" variant="ghost" onClick={handleAddRule}>+ 添加规则</Button>
      </div>

      {rules.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-4">暂无质量规则</p>
      ) : (
        rules.map((rule, i) => (
          <div key={i} className="bg-gray-800 rounded-lg p-3 space-y-2">
            <Input
              value={rule.field}
              onChange={(e) => {
                const newR = [...rules];
                newR[i].field = e.target.value;
                setRules(newR);
              }}
              placeholder="字段名"
            />
            <Select
              value={rule.type}
              onChange={(e) => {
                const newR = [...rules];
                newR[i].type = e.target.value;
                setRules(newR);
              }}
              options={ruleTypes}
            />
            <Input
              value={rule.value}
              onChange={(e) => {
                const newR = [...rules];
                newR[i].value = e.target.value;
                setRules(newR);
              }}
              placeholder="阈值/正则表达式"
            />
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setRules(rules.filter((_, idx) => idx !== i))}
              className="text-red-400"
            >
              删除
            </Button>
          </div>
        ))
      )}

      <Button onClick={handleSave} className="w-full">
        保存配置
      </Button>
    </div>
  );
}

function DatasetConfig({ node, nodes, onSave }: { node: any; nodes: any[]; onSave: (config: Record<string, unknown>) => void }) {
  const [sourceIds, setSourceIds] = useState<string[]>(node.config?.sourceIds || []);
  const [joinType, setJoinType] = useState(node.config?.joinType || 'union');

  const sourceNodes = nodes.filter(n => n.type === 'system');

  const handleToggleSource = (id: string) => {
    if (sourceIds.includes(id)) {
      setSourceIds(sourceIds.filter(s => s !== id));
    } else {
      setSourceIds([...sourceIds, id]);
    }
  };

  const handleSave = () => {
    onSave({ sourceIds, joinType });
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm text-gray-400 mb-2">选择数据源</label>
        {sourceNodes.length === 0 ? (
          <p className="text-sm text-gray-500">暂无数据源</p>
        ) : (
          <div className="space-y-2">
            {sourceNodes.map((source) => (
              <label
                key={source.id}
                className={`flex items-center p-3 rounded-lg cursor-pointer transition-colors ${
                  sourceIds.includes(source.id)
                    ? 'bg-green-900/50 border border-green-700'
                    : 'bg-gray-800 border border-gray-700 hover:border-gray-600'
                }`}
              >
                <input
                  type="checkbox"
                  checked={sourceIds.includes(source.id)}
                  onChange={() => handleToggleSource(source.id)}
                  className="sr-only"
                />
                <span className="text-sm text-gray-300">{source.name}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-2">合并方式</label>
        <Select
          value={joinType}
          onChange={(e) => setJoinType(e.target.value)}
          options={[
            { value: 'union', label: '合并 (UNION)' },
            { value: 'join', label: '关联 (JOIN)' },
          ]}
        />
      </div>

      <Button onClick={handleSave} className="w-full" disabled={sourceIds.length === 0}>
        保存配置
      </Button>
    </div>
  );
}

function OntologyConfig({ node, nodes, onSave }: { node: any; nodes: any[]; onSave: (config: Record<string, unknown>) => void }) {
  const [template, setTemplate] = useState(node.config?.template || 'custom');
  const [entities, setEntities] = useState<{ name: string; sourceTable: string; sourceField: string; description: string }[]>(
    node.config?.entities || []
  );
  const [relationships, setRelationships] = useState<{ from: string; to: string; type: string; description: string }[]>(
    node.config?.relationships || []
  );
  
  const { currentProjectId } = useFlowStore();
  const { projects } = useProjectStore();
  const { ontologies, fetchOntologies, selectOntology } = useOntologyStore();
  const projectId = currentProjectId || projects[0]?.id;
  const navigate = useNavigate();
  
  useEffect(() => {
    if (projectId) {
      fetchOntologies(projectId);
    }
  }, [projectId, fetchOntologies]);

  const selectedOntologyId = node.config?.ontologyId;
  const selectedOntology = ontologies.find(o => o.id === selectedOntologyId);

  const sourceNodes = nodes.filter(n => n.type === 'source');
  const acquisitionNodes = nodes.filter(n => n.type === 'acquisition');

  const templates = [
    { value: 'system_anomaly', label: '系统异常分析' },
    { value: 'quality_issue', label: '质量问题分析' },
    { value: 'performance', label: '性能问题分析' },
    { value: 'custom', label: '自定义本体' },
  ];

  const relationTypes = [
    { value: 'causes', label: '因果关系' },
    { value: 'depends_on', label: '依赖关系' },
    { value: 'contains', label: '组成关系' },
    { value: 'similar_to', label: '相似关系' },
  ];

  const handleSelectOntology = (ontologyId: number) => {
    onSave({ ...node.config, ontologyId });
  };

  const handleOpenOntologyPage = () => {
    if (projectId) {
      navigate(`/ontology/${projectId}`);
    }
  };

  const handleAddEntity = () => {
    setEntities([...entities, { name: '', sourceTable: '', sourceField: '', description: '' }]);
  };

  const handleAddRelationship = () => {
    setRelationships([...relationships, { from: '', to: '', type: 'causes', description: '' }]);
  };

  const handleSave = () => {
    onSave({ template, entities, relationships, ontologyId: selectedOntologyId });
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm text-gray-400 mb-2">选择本体库</label>
        <Select
          value={selectedOntologyId || ''}
          onChange={(e) => handleSelectOntology(parseInt(e.target.value))}
          options={[
            { value: '', label: '-- 请选择本体库 --' },
            ...ontologies.map(o => ({ value: String(o.id), label: o.name }))
          ]}
        />
        {selectedOntologyId && (
          <button
            onClick={handleOpenOntologyPage}
            className="mt-2 w-full py-2 bg-primary text-white rounded-lg hover:bg-primary-dark"
          >
            配置本体库
          </button>
        )}
      </div>
      
      {ontologies.length === 0 && (
        <div className="space-y-2">
          <p className="text-sm text-gray-500">暂无本体库，请在页面中创建</p>
          <button
            onClick={handleOpenOntologyPage}
            className="w-full py-2 bg-primary text-white rounded-lg hover:bg-primary-dark"
          >
            前往本体库配置页面
          </button>
        </div>
      )}

      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm text-gray-400">实体映射</label>
          <Button size="sm" variant="ghost" onClick={handleAddEntity}>+ 添加实体</Button>
        </div>
        
        {entities.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-2">暂无实体映射</p>
        ) : (
          <div className="space-y-3">
            {entities.map((entity, i) => (
              <div key={i} className="bg-gray-800 rounded-lg p-3 space-y-2">
                <Input
                  value={entity.name}
                  onChange={(e) => {
                    const newE = [...entities];
                    newE[i].name = e.target.value;
                    setEntities(newE);
                  }}
                  placeholder="实体名称"
                />
                <div className="flex gap-2">
                  <select
                    value={entity.sourceTable}
                    onChange={(e) => {
                      const newE = [...entities];
                      newE[i].sourceTable = e.target.value;
                      setEntities(newE);
                    }}
                    className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-300"
                  >
                    <option value="">选择数据表</option>
                    {acquisitionNodes.map(n => (
                      <option key={n.id} value={n.name}>{n.name}</option>
                    ))}
                  </select>
                  <Input
                    value={entity.sourceField}
                    onChange={(e) => {
                      const newE = [...entities];
                      newE[i].sourceField = e.target.value;
                      setEntities(newE);
                    }}
                    placeholder="字段名"
                    className="flex-1"
                  />
                </div>
                <Input
                  value={entity.description}
                  onChange={(e) => {
                    const newE = [...entities];
                    newE[i].description = e.target.value;
                    setEntities(newE);
                  }}
                  placeholder="实体描述"
                />
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setEntities(entities.filter((_, idx) => idx !== i))}
                  className="text-red-400"
                >
                  删除
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm text-gray-400">关系定义</label>
          <Button size="sm" variant="ghost" onClick={handleAddRelationship}>+ 添加关系</Button>
        </div>
        
        {relationships.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-2">暂无关系定义</p>
        ) : (
          <div className="space-y-3">
            {relationships.map((rel, i) => (
              <div key={i} className="bg-gray-800 rounded-lg p-3 space-y-2">
                <div className="flex gap-2">
                  <select
                    value={rel.from}
                    onChange={(e) => {
                      const newR = [...relationships];
                      newR[i].from = e.target.value;
                      setRelationships(newR);
                    }}
                    className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-300"
                  >
                    <option value="">源实体</option>
                    {entities.map(e => (
                      <option key={e.name} value={e.name}>{e.name}</option>
                    ))}
                  </select>
                  <select
                    value={rel.type}
                    onChange={(e) => {
                      const newR = [...relationships];
                      newR[i].type = e.target.value;
                      setRelationships(newR);
                    }}
                    className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-300"
                  >
                    {relationTypes.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                  <select
                    value={rel.to}
                    onChange={(e) => {
                      const newR = [...relationships];
                      newR[i].to = e.target.value;
                      setRelationships(newR);
                    }}
                    className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-300"
                  >
                    <option value="">目标实体</option>
                    {entities.map(e => (
                      <option key={e.name} value={e.name}>{e.name}</option>
                    ))}
                  </select>
                </div>
                <Input
                  value={rel.description}
                  onChange={(e) => {
                    const newR = [...relationships];
                    newR[i].description = e.target.value;
                    setRelationships(newR);
                  }}
                  placeholder="关系描述"
                />
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setRelationships(relationships.filter((_, idx) => idx !== i))}
                  className="text-red-400"
                >
                  删除
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      <Button onClick={handleSave} className="w-full">
        保存配置
      </Button>
    </div>
  );
}

function AnalysisConfig({ node, nodes, onSave }: { node: any; nodes: any[]; onSave: (config: Record<string, unknown>) => void }) {
  const analysisType = node.detail || 'ontology_explore';
  const { currentProjectId } = useFlowStore();
  const navigate = useNavigate();
  
  const [selectedEntities, setSelectedEntities] = useState<string[]>(node.config?.selectedEntities || []);
  const [analysisParams, setAnalysisParams] = useState(node.config?.params || {});
  const [dashboards, setDashboards] = useState<api.Dashboard[]>([]);
  const [isNavigating, setIsNavigating] = useState(false);
  
  const savedDashboardId = node.config?.dashboardId;
  
  useEffect(() => {
    if (currentProjectId) {
      api.getDashboards(currentProjectId).then(data => {
        setDashboards(data);
      }).catch(err => console.error('Failed to load dashboards:', err));
    }
  }, [currentProjectId]);
  
  const handleOpenDashboard = async () => {
    if (!currentProjectId || isNavigating) return;
    setIsNavigating(true);
    
    try {
      let targetDashboardId = savedDashboardId;
      
      if (!targetDashboardId) {
        const newDashboard = await api.createDashboard(currentProjectId, {
          name: `${node.name || '数据分析'}看板`,
          layout: { type: 'grid', cols: 12 },
          components: [],
        });
        targetDashboardId = newDashboard.id;
      }
      
      // 更新节点配置
      const newConfig = { ...node.config, dashboardId: targetDashboardId };
      
      // 先更新onSave
      onSave(newConfig);
      
      // 获取当前canvas数据，更新节点配置后保存
      const canvasData = await api.getCanvas(currentProjectId);
      const updatedNodes = canvasData.nodes.map((n: any) => 
        n.id === node.id ? { ...n, config: newConfig } : n
      );
      await api.saveCanvas(currentProjectId, {
        nodes: updatedNodes,
        connections: canvasData.connections
      });
      
      navigate(`/dashboard/${currentProjectId}/${targetDashboardId}`);
    } catch (err) {
      console.error('Failed to open dashboard:', err);
    } finally {
      setIsNavigating(false);
    }
  };
  
  const ontologyNodes = nodes.filter(n => n.type === 'ontology');
  
  let ontologyConfig: any = null;
  for (const n of nodes) {
    if (n.type === 'ontology') {
      ontologyConfig = n.config;
      break;
    }
  }
  
  const entities = ontologyConfig?.entities || [];
  const relationships = ontologyConfig?.relationships || [];
  
  const handleToggleEntity = (entityName: string) => {
    if (selectedEntities.includes(entityName)) {
      setSelectedEntities(selectedEntities.filter(e => e !== entityName));
    } else {
      setSelectedEntities([...selectedEntities, entityName]);
    }
  };
  
  const handleSave = () => {
    onSave({ selectedEntities, params: analysisParams, dashboardId: node.config?.dashboardId });
  };

  // 所有 analysis 节点都显示跳转按钮
  return (
    <div className="space-y-4">
      <div>
        <button
          onClick={handleOpenDashboard}
          disabled={isNavigating}
          className="w-full py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium disabled:opacity-50"
        >
          {isNavigating ? '打开中...' : '打开数据分析看板'}
        </button>
      </div>
      
      {analysisType === 'data_analysis' && (
        <>
          <div>
            <label className="block text-sm text-gray-400 mb-2">分析类型</label>
            <select
              value={analysisParams.type || 'statistics'}
              onChange={(e) => setAnalysisParams({ ...analysisParams, type: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-300"
            >
              <option value="statistics">统计分析</option>
              <option value="trend">趋势分析</option>
              <option value="correlation">相关性分析</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-2">输出格式</label>
            <select
              value={analysisParams.format || 'chart'}
              onChange={(e) => setAnalysisParams({ ...analysisParams, format: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-300"
            >
              <option value="chart">图表</option>
              <option value="table">表格</option>
              <option value="report">报告</option>
            </select>
          </div>
        </>
      )}
      
      {analysisType === 'root_cause' && (
        <>
          <div>
            <label className="block text-sm text-gray-400 mb-2">分析深度</label>
            <select
              value={analysisParams.depth || '2'}
              onChange={(e) => setAnalysisParams({ ...analysisParams, depth: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-300"
            >
              <option value="1">1 层</option>
              <option value="2">2 层</option>
              <option value="3">3 层</option>
              <option value="5">5 层</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-2">根因阈值</label>
            <input
              type="number"
              value={analysisParams.threshold || '0.5'}
              onChange={(e) => setAnalysisParams({ ...analysisParams, threshold: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-gray-300"
              step="0.1"
              min="0"
              max="1"
            />
          </div>
          
          <div>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={analysisParams.autoDetect || false}
                onChange={(e) => setAnalysisParams({ ...analysisParams, autoDetect: e.target.checked })}
                className="rounded bg-gray-700 border-gray-600"
              />
              <span className="text-sm text-gray-300">自动根因检测</span>
            </label>
          </div>
        </>
      )}
      
      {analysisType === 'ontology_explore' && (
        <>
          <div>
            <label className="block text-sm text-gray-400 mb-2">选择展示的实体</label>
            {entities.length === 0 ? (
              <p className="text-sm text-gray-500">请先在本体库中配置实体</p>
            ) : (
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {entities.map((entity: any) => (
                  <label
                    key={entity.name}
                    className={`flex items-center p-2 rounded cursor-pointer transition-colors ${
                      selectedEntities.includes(entity.name)
                        ? 'bg-pink-900/50 border border-pink-700'
                        : 'bg-gray-800 border border-gray-700 hover:border-gray-600'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedEntities.includes(entity.name)}
                      onChange={() => handleToggleEntity(entity.name)}
                      className="sr-only"
                    />
                    <span className="text-sm text-gray-300">{entity.name}</span>
                    {entity.description && (
                      <span className="text-xs text-gray-500 ml-2 truncate">{entity.description}</span>
                    )}
                  </label>
                ))}
              </div>
            )}
          </div>
          
          {selectedEntities.length > 0 && relationships.length > 0 && (
            <div>
              <label className="block text-sm text-gray-400 mb-2">实体关系图预览</label>
              <div className="bg-gray-800 rounded-lg p-3 text-xs text-gray-500">
                <p>已选择 {selectedEntities.length} 个实体</p>
                <p>可用关系: {relationships.length} 条</p>
                <div className="mt-2 space-y-1">
                  {relationships.slice(0, 5).map((rel: any, i: number) => (
                    <p key={i}>{rel.from} → {rel.to} ({rel.type})</p>
                  ))}
                  {relationships.length > 5 && <p>...等 {relationships.length} 条关系</p>}
                </div>
              </div>
            </div>
          )}
        </>
      )}
      
      <Button onClick={handleSave} className="w-full">
        保存配置
      </Button>
    </div>
  );
}

function DefaultConfig() {
  return (
    <div className="text-center py-8">
      <p className="text-gray-500">该节点类型暂不支持配置</p>
    </div>
  );
}

export default function ConfigPanel() {
  const { selectedNodeId, currentProjectId, projectsData, updateNodeStatus, updateNodeConfig, updateNodeName, removeDataSource, removeNode, toggleConfigPanel } = useFlowStore();
  
  const currentProject = currentProjectId ? projectsData[currentProjectId] : null;
  const nodes = currentProject?.nodes || [];
  const node = nodes.find(n => n.id === selectedNodeId);

  if (!node) return null;

  const colors = typeColors[node.type] || typeColors.system;

  const handleSaveConfig = (config: Record<string, unknown>) => {
    updateNodeConfig(node.id, config);
  };

  const handleDelete = () => {
    if (window.confirm('确定要删除此节点吗？')) {
      removeNode(node.id);
    }
  };

  const showDelete = ['system', 'acquisition', 'datapipeline', 'quality', 'dataset', 'ontology', 'analysis', 'rootCause'].includes(node.type);

  const renderConfigContent = () => {
    switch (node.type) {
      case 'system':
        return <SystemConfig node={node} onSave={handleSaveConfig} />;
      case 'acquisition':
        return <AcquisitionConfig node={node} onSave={handleSaveConfig} />;
      case 'datapipeline':
        return <ProcessConfig node={node} onSave={handleSaveConfig} />;
      case 'quality':
        return <QualityConfig node={node} onSave={handleSaveConfig} />;
      case 'dataset':
        return <DatasetConfig node={node} nodes={nodes} onSave={handleSaveConfig} />;
      case 'ontology':
        return <OntologyConfig node={node} nodes={nodes} onSave={handleSaveConfig} />;
      case 'analysis':
        return <AnalysisConfig node={node} nodes={nodes} onSave={handleSaveConfig} />;
      default:
        return <DefaultConfig />;
    }
  };

  return (
    <AnimatePresence>
      {node && (
        <motion.div
          initial={{ x: 320, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 320, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed right-0 top-16 bottom-0 w-80 bg-gray-900 border-l border-gray-800 z-40 overflow-y-auto"
        >
          <div className="p-4">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-white">节点配置</h3>
              <button
                onClick={() => toggleConfigPanel(false)}
                className="p-1 hover:bg-gray-800 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <div 
                    className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: colors.light }}
                  >
                    <span className="text-lg font-bold" style={{ color: colors.bg }}>
                      {node.name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h4 className="text-white font-medium">{node.name}</h4>
                    <p className="text-xs text-gray-400">{colors.label}</p>
                  </div>
                </div>
                
                <div className="mt-3">
                  <label className="block text-xs text-gray-500 mb-1">节点名称</label>
                  <Input
                    value={node.name}
                    onChange={(e) => updateNodeName(node.id, e.target.value)}
                    placeholder="输入节点名称"
                  />
                </div>
                
                {node.detail && (
                  <p className="text-xs text-gray-500 font-mono mt-2">{node.detail}</p>
                )}
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500 uppercase tracking-wider">状态</span>
                <span 
                  className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium"
                  style={{ 
                    backgroundColor: colors.light,
                    color: colors.bg,
                  }}
                >
                  {statusLabels[node.status]}
                </span>
              </div>

              <hr className="border-gray-800" />

              {renderConfigContent()}

              {showDelete && (
                <div className="pt-4 border-t border-gray-800">
                  <Button variant="danger" size="sm" onClick={handleDelete}>
                    删除节点
                  </Button>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
