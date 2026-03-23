import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import GridLayout, { Layout } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import * as api from '@/services/api';
import { useProjectStore } from '@/stores/projectStore';
import { useWizardStore } from '@/stores/wizardStore';

interface FieldInfo {
  name: string;
  type: string;
  sample: any;
  null_count: number;
}

interface Filter {
  field: string;
  operator: string;
  value: string;
}

interface Aggregation {
  field: string;
  function: string;
  alias: string;
}

interface GroupBy {
  field: string;
  granularity: string;
}

interface ComponentConfig {
  dataSource: { type: string; file_path: string };
  fields: string[];
  filters: Filter[];
  aggregations: Aggregation[];
  groupBy: GroupBy | null;
  chartType?: 'line' | 'bar' | 'pie';
}

interface DashboardComponent {
  id: string;
  type: string;
  title: string;
  w: number;
  h: number;
  config: ComponentConfig;
}

const DEFAULT_CSV_PATH = '/Users/yuhuwang/Documents/trae_projects/root_cause_analysis/product_inventory_data.csv';
const CHART_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

export default function DataAnalysisDashboard() {
  const { projectId, dashboardId } = useParams<{ projectId: string; dashboardId?: string }>();
  const navigate = useNavigate();

  const { dataSources } = useWizardStore();
  const { projectsData } = useProjectStore();
  
  const [csvPath, setCsvPath] = useState(DEFAULT_CSV_PATH);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<api.CSVAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [dashboards, setDashboards] = useState<api.Dashboard[]>([]);
  const [currentDashboard, setCurrentDashboard] = useState<api.Dashboard | null>(null);
  const [dashboardName, setDashboardName] = useState('未命名看板');
  const [isSaving, setIsSaving] = useState(false);

  const [components, setComponents] = useState<DashboardComponent[]>([]);
  const [selectedComponentId, setSelectedComponentId] = useState<string | null>(null);
  const [showComponentConfig, setShowComponentConfig] = useState(false);

  const [showAddComponentModal, setShowAddComponentModal] = useState(false);
  const [componentData, setComponentData] = useState<Record<string, any[]>>({});
  
  // 数据集选项
  const [datasets, setDatasets] = useState<{ value: string; label: string }[]>([]);
  const [selectedDataset, setSelectedDataset] = useState('');
  
  // 加载数据集
  useEffect(() => {
    // 从项目数据或数据源中获取数据集
    const project = projectsData[projectId];
    if (project) {
      // 这里可以根据实际情况从项目数据中提取数据集
      // 暂时使用数据源作为数据集
      const projectDatasets = dataSources.map(source => ({
        value: source.host, // 假设 host 是文件路径
        label: source.name
      }));
      setDatasets(projectDatasets);
      
      // 如果有数据集，默认选择第一个
      if (projectDatasets.length > 0) {
        setSelectedDataset(projectDatasets[0].value);
        setCsvPath(projectDatasets[0].value);
      }
    }
  }, [projectId, projectsData, dataSources]);

  useEffect(() => {
    if (projectId) {
      loadDashboards();
    }
  }, [projectId]);

  useEffect(() => {
    if (!dashboardId) return;
    
    if (dashboards.length > 0) {
      const db = dashboards.find(d => d.id === Number(dashboardId));
      if (db) {
        setCurrentDashboard(db);
        setDashboardName(db.name);
        setComponents(db.components || []);
        
        if (db.components && db.components.length > 0) {
          const csvPath = db.components[0]?.config?.dataSource?.file_path;
          if (csvPath) {
            setCsvPath(csvPath);
            handleAnalyzeWithPath(csvPath);
          }
        }
      }
    }
  }, [dashboards, dashboardId]);

  const handleAnalyzeWithPath = async (filePath: string) => {
    try {
      const result = await api.analyzeCSV(filePath);
      setAnalysisResult(result);
    } catch (err) {
      console.error('Failed to analyze CSV:', err);
    }
  };

  useEffect(() => {
    if (components.length === 0 || !analysisResult) return;
    
    components.forEach(comp => {
      if (comp.config.dataSource.file_path && (comp.config.fields.length > 0 || comp.config.aggregations.length > 0)) {
        loadComponentData(comp);
      }
    });
  }, [components, analysisResult]);

  const getLayouts = (): Layout[] => {
    return components.map((comp, index) => ({
      i: comp.id,
      x: (index % 3) * 4,
      y: Math.floor(index / 3) * 2,
      w: comp.w,
      h: comp.h,
      minW: 2,
      minH: 1,
    }));
  };

  const onLayoutChange = (newLayout: Layout[]) => {
    setComponents(prevComponents => {
      return prevComponents.map(comp => {
        const layout = newLayout.find(l => l.i === comp.id);
        if (layout) {
          return { ...comp, w: layout.w, h: layout.h };
        }
        return comp;
      });
    });
  };

  const handleComponentClick = (e: React.MouseEvent, componentId: string) => {
    e.preventDefault();
    e.stopPropagation();
    setSelectedComponentId(componentId);
    setShowComponentConfig(true);
  };

  const loadDashboards = async () => {
    if (!projectId) return;
    try {
      const data = await api.getDashboards(projectId);
      setDashboards(data);
    } catch (err) {
      console.error('Failed to load dashboards:', err);
    }
  };

  const loadComponentData = async (component: DashboardComponent) => {
    try {
      const result = await api.queryData(component.config.dataSource, {
        fields: component.config.fields,
        filters: component.config.filters,
        aggregations: component.config.aggregations,
        groupBy: component.config.groupBy || undefined,
      });
      setComponentData(prev => ({ ...prev, [component.id]: result.data }));
    } catch (err) {
      console.error('Failed to load component data:', err);
    }
  };

  const handleAnalyze = async () => {
    if (!csvPath.trim()) {
      setError('请输入 CSV 文件路径');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await api.analyzeCSV(csvPath.trim());
      setAnalysisResult(result);
    } catch (err) {
      console.error('Failed to analyze CSV:', err);
      setError('分析 CSV 文件失败: ' + (err as Error).message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSaveDashboard = async () => {
    if (!projectId) return;

    setIsSaving(true);
    try {
      const dashboardData = {
        name: dashboardName,
        layout: { type: 'grid', cols: 12 },
        components: components,
      };

      if (currentDashboard) {
        await api.updateDashboard(projectId, currentDashboard.id, dashboardData);
      } else {
        const newDashboard = await api.createDashboard(projectId, dashboardData);
        setCurrentDashboard(newDashboard);
        navigate(`/dashboard/${projectId}/${newDashboard.id}`, { replace: true });
      }
      await loadDashboards();
    } catch (err) {
      console.error('Failed to save dashboard:', err);
      setError('保存看板失败: ' + (err as Error).message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddComponent = (type: string) => {
    const newComponent: DashboardComponent = {
      id: `component-${Date.now()}`,
      type,
      title: type === 'table' ? '数据表格' : type === 'chart' ? '图表' : '指标卡',
      w: type === 'metric' ? 4 : 12,
      h: type === 'metric' ? 2 : 5,
      config: {
        dataSource: { type: 'csv', file_path: csvPath },
        fields: [],
        filters: [],
        aggregations: [],
        groupBy: null,
        chartType: 'line',
      },
    };
    setComponents([...components, newComponent]);
    setShowAddComponentModal(false);
  };

  const handleDeleteComponent = (componentId: string) => {
    setComponents(components.filter(c => c.id !== componentId));
    if (selectedComponentId === componentId) {
      setSelectedComponentId(null);
      setShowComponentConfig(false);
    }
  };

  const updateComponentConfig = (componentId: string, updates: Partial<ComponentConfig>) => {
    setComponents(components.map(c => c.id === componentId ? { ...c, config: { ...c.config, ...updates } } : c));
  };

  const selectedComponent = components.find(c => c.id === selectedComponentId);

  const renderMetricCard = (component: DashboardComponent) => {
    const data = componentData[component.id] || [];
    const agg = component.config.aggregations[0];
    const value = data.length > 0 && agg ? data[0][agg.alias] : null;

    return (
      <div className="h-full flex flex-col items-center justify-center p-4">
        <div className="text-3xl font-bold text-gray-900">
          {value !== null && value !== undefined ? (typeof value === 'number' ? value.toLocaleString() : value) : '-'}
        </div>
        <div className="text-sm text-gray-500 mt-1">{agg ? `${agg.function.toUpperCase()}(${agg.field})` : '未配置'}</div>
      </div>
    );
  };

  const renderChart = (component: DashboardComponent) => {
    const data = componentData[component.id] || [];
    if (data.length === 0) return <div className="h-full flex items-center justify-center text-gray-400">暂无数据</div>;

    const groupField = component.config.groupBy?.field;
    const aggAlias = component.config.aggregations[0]?.alias;

    if (component.config.chartType === 'pie') {
      const pieData = data.map((item, idx) => ({
        name: groupField ? item[groupField] : `Item ${idx}`,
        value: aggAlias ? item[aggAlias] : 0,
      }));
      return (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius="80%" label>
              {pieData.map((_, idx) => <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />)}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      );
    }

    const ChartComponent = component.config.chartType === 'bar' ? BarChart : LineChart;
    return (
      <ResponsiveContainer width="100%" height="100%">
        <ChartComponent data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={groupField} fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip />
          {component.config.aggregations.map((agg, idx) => (
            component.config.chartType === 'bar' ? (
              <Bar key={idx} dataKey={agg.alias} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
            ) : (
              <Line key={idx} type="monotone" dataKey={agg.alias} stroke={CHART_COLORS[idx % CHART_COLORS.length]} />
            )
          ))}
        </ChartComponent>
      </ResponsiveContainer>
    );
  };

  const renderTable = (component: DashboardComponent) => {
    const data = componentData[component.id] || [];
    if (data.length === 0) return <div className="h-full flex items-center justify-center text-gray-400">暂无数据</div>;

    const columns = component.config.fields.length > 0 ? component.config.fields : 
      (component.config.groupBy ? [component.config.groupBy.field, ...component.config.aggregations.map(a => a.alias)] : Object.keys(data[0] || {}));

    return (
      <div className="h-full overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-gray-50">
            <tr>
              {columns.map(col => <th key={col} className="px-3 py-2 text-left font-medium text-gray-600 border-b">{col}</th>)}
            </tr>
          </thead>
          <tbody>
            {data.slice(0, 100).map((row, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                {columns.map(col => <td key={col} className="px-3 py-2 border-b text-gray-900">{String(row[col] ?? '-')}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
        {data.length > 100 && <div className="text-center py-2 text-gray-500 text-xs">显示前100条，共{data.length}条</div>}
      </div>
    );
  };

  const renderComponentContent = (component: DashboardComponent) => {
    switch (component.type) {
      case 'metric': return renderMetricCard(component);
      case 'chart': return renderChart(component);
      case 'table': return renderTable(component);
      default: return null;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <div className="h-14 bg-white border-b flex items-center px-6 justify-between shrink-0">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(`/flow/${projectId}`)} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            返回项目
          </button>
          <div className="h-6 w-px bg-gray-200" />
          <h1 className="text-lg font-semibold text-gray-900">数据分析看板</h1>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={currentDashboard?.id || ''}
            onChange={(e) => {
              const selectedId = parseInt(e.target.value);
              if (selectedId) navigate(`/dashboard/${projectId}/${selectedId}`);
            }}
            className="px-4 py-2 border rounded-lg bg-white"
          >
            <option value="">选择看板</option>
            {dashboards.map(db => <option key={db.id} value={db.id}>{db.name}</option>)}
          </select>
          <button onClick={handleSaveDashboard} disabled={isSaving} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            {isSaving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="w-80 bg-white border-r flex flex-col shrink-0">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900 mb-4">数据源配置</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-400 mb-2">选择项目的数据集</label>
                <select
                  value={selectedDataset}
                  onChange={(e) => {
                    setSelectedDataset(e.target.value);
                    setCsvPath(e.target.value);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="">请选择数据集</option>
                  {datasets.map((dataset) => (
                    <option key={dataset.value} value={dataset.value}>{dataset.label}</option>
                  ))}
                </select>
              </div>
              <button onClick={handleAnalyze} disabled={isAnalyzing} className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">
                {isAnalyzing ? '分析中...' : '分析'}
              </button>
            </div>
            {error && <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">{error}</div>}
          </div>

          {analysisResult && (
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="p-4 border-b">
                <h2 className="font-semibold text-gray-900">字段信息</h2>
                <p className="text-xs text-gray-500 mt-1">共 {analysisResult.total_rows} 行, {analysisResult.fields.length} 个字段</p>
              </div>
              <div className="flex-1 overflow-auto p-3 space-y-2">
                {analysisResult.fields.map((field: FieldInfo) => (
                  <div key={field.name} className="p-3 rounded-lg border border-gray-200 bg-gray-50">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900 text-sm">{field.name}</span>
                      <span className="text-xs px-2 py-0.5 bg-gray-200 text-gray-600 rounded">{field.type}</span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">空值: {field.null_count} | 示例: {String(field.sample).substring(0, 20)}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="p-4 border-t">
            <label className="block text-sm font-medium text-gray-700 mb-1">看板名称</label>
            <input type="text" value={dashboardName} onChange={(e) => setDashboardName(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
          </div>
        </div>

        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="h-12 bg-white border-b flex items-center px-4 gap-3 shrink-0">
            <button onClick={() => setShowAddComponentModal(true)} className="px-4 py-1.5 bg-blue-600 text-white rounded-lg text-sm">+ 添加组件</button>
            <div className="text-sm text-gray-500">共 {components.length} 个组件</div>
          </div>

          <div className="flex-1 overflow-auto p-6 bg-gray-100">
            {components.length === 0 ? (
              <div className="h-full flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <p>暂无组件</p>
                  <p className="text-sm mt-1">点击上方"添加组件"开始构建看板</p>
                </div>
              </div>
            ) : (
              <GridLayout
                className="layout"
                layout={getLayouts()}
                cols={12}
                rowHeight={100}
                width={1200}
                onLayoutChange={onLayoutChange}
                margin={[16, 16]}
                containerPadding={[0, 0]}
                isDraggable={true}
                isResizable={true}
              >
                {components.map((component) => (
                  <div
                    key={component.id}
                    className={`bg-white rounded-xl border-2 ${selectedComponentId === component.id ? 'border-blue-600 shadow-lg' : 'border-gray-200 hover:border-gray-300'}`}
                  >
                    <div className="h-full p-4 flex flex-col">
                      <div 
                        className="flex items-center justify-between mb-2 cursor-pointer"
                        onClick={(e) => handleComponentClick(e, component.id)}
                      >
                        <h3 className="font-medium text-gray-900 text-sm">{component.title}</h3>
                        <button 
                          onClick={(e) => { e.stopPropagation(); handleDeleteComponent(component.id); }} 
                          className="text-gray-400 hover:text-red-500"
                        >
                          ✕
                        </button>
                      </div>
                      <div className="flex-1 overflow-hidden">
                        {renderComponentContent(component)}
                      </div>
                    </div>
                  </div>
                ))}
              </GridLayout>
            )}
          </div>
        </div>

        {showComponentConfig && selectedComponent && analysisResult && (
          <div className="w-80 bg-white border-l flex flex-col shrink-0">
            <div className="p-4 border-b flex items-center justify-between">
              <h2 className="font-semibold text-gray-900">组件配置</h2>
              <button onClick={() => setShowComponentConfig(false)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="flex-1 overflow-auto p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">组件标题</label>
                <input
                  type="text"
                  value={selectedComponent.title}
                  onChange={(e) => setComponents(components.map(c => c.id === selectedComponent.id ? { ...c, title: e.target.value } : c))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>

              {selectedComponent.type === 'chart' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">图表类型</label>
                  <select
                    value={selectedComponent.config.chartType || 'line'}
                    onChange={(e) => updateComponentConfig(selectedComponent.id, { chartType: e.target.value as 'line' | 'bar' | 'pie' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="line">折线图</option>
                    <option value="bar">柱状图</option>
                    <option value="pie">饼图</option>
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">分组字段</label>
                <select
                  value={selectedComponent.config.groupBy?.field || ''}
                  onChange={(e) => {
                    const field = e.target.value;
                    if (!field) {
                      updateComponentConfig(selectedComponent.id, { groupBy: null });
                    } else {
                      const fieldInfo = analysisResult.fields.find(f => f.name === field);
                      updateComponentConfig(selectedComponent.id, { 
                        groupBy: { field, granularity: fieldInfo?.type === 'date' ? 'day' : 'none' } 
                      });
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="">无分组</option>
                  {analysisResult.fields.map(f => <option key={f.name} value={f.name}>{f.name} ({f.type})</option>)}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">聚合函数</label>
                <div className="space-y-2">
                  {selectedComponent.config.aggregations.map((agg, idx) => (
                    <div key={idx} className="flex gap-2">
                      <select
                        value={agg.function}
                        onChange={(e) => {
                          const newAggs = [...selectedComponent.config.aggregations];
                          newAggs[idx] = { ...agg, function: e.target.value };
                          updateComponentConfig(selectedComponent.id, { aggregations: newAggs });
                        }}
                        className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                      >
                        <option value="sum">SUM</option>
                        <option value="avg">AVG</option>
                        <option value="count">COUNT</option>
                        <option value="min">MIN</option>
                        <option value="max">MAX</option>
                      </select>
                      <select
                        value={agg.field}
                        onChange={(e) => {
                          const newAggs = [...selectedComponent.config.aggregations];
                          newAggs[idx] = { ...agg, field: e.target.value, alias: `${agg.function}_${e.target.value}` };
                          updateComponentConfig(selectedComponent.id, { aggregations: newAggs });
                        }}
                        className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                      >
                        {analysisResult.fields.filter(f => f.type === 'number').map(f => <option key={f.name} value={f.name}>{f.name}</option>)}
                      </select>
                      <button onClick={() => {
                        const newAggs = selectedComponent.config.aggregations.filter((_, i) => i !== idx);
                        updateComponentConfig(selectedComponent.id, { aggregations: newAggs });
                      }} className="text-red-500 hover:text-red-700">✕</button>
                    </div>
                  ))}
                  <button
                    onClick={() => {
                      const numberFields = analysisResult.fields.filter(f => f.type === 'number');
                      if (numberFields.length > 0) {
                        updateComponentConfig(selectedComponent.id, { 
                          aggregations: [...selectedComponent.config.aggregations, { function: 'sum', field: numberFields[0].name, alias: `sum_${numberFields[0].name}` }] 
                        });
                      }
                    }}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    + 添加聚合
                  </button>
                </div>
              </div>

              <button
                onClick={() => {
                  const comp = components.find(c => c.id === selectedComponent.id);
                  if (comp) loadComponentData(comp);
                }}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg text-sm"
              >
                刷新数据
              </button>
            </div>
          </div>
        )}
      </div>

      {showAddComponentModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowAddComponentModal(false)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">添加组件</h3>
              <button onClick={() => setShowAddComponentModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <button onClick={() => handleAddComponent('table')} className="p-4 border border-gray-200 rounded-xl hover:border-blue-600 hover:bg-blue-50 text-center">
                <div className="text-3xl mb-2">📊</div>
                <div className="text-sm font-medium text-gray-900">数据表格</div>
              </button>
              <button onClick={() => handleAddComponent('chart')} className="p-4 border border-gray-200 rounded-xl hover:border-blue-600 hover:bg-blue-50 text-center">
                <div className="text-3xl mb-2">📈</div>
                <div className="text-sm font-medium text-gray-900">图表</div>
              </button>
              <button onClick={() => handleAddComponent('metric')} className="p-4 border border-gray-200 rounded-xl hover:border-blue-600 hover:bg-blue-50 text-center">
                <div className="text-3xl mb-2">📉</div>
                <div className="text-sm font-medium text-gray-900">指标卡</div>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
