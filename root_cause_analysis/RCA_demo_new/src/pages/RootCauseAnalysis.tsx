import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactFlow, { 
  Node, 
  Edge, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
} from 'reactflow';
import ReactMarkdown from 'react-markdown';
import 'reactflow/dist/style.css';
import * as api from '@/services/api';

const DEFAULT_CAUSAL_GRAPH = `digraph {
    kunlun_2280_sales -> pac900s12_b2_1_consumption;
    server_2288hv7_sales -> pac900s12_b2_1_consumption;
    server_2288hv7_uses_pac900s12_b2_1 -> pac900s12_b2_1_consumption;
    pac900s12_b2_1_consumption -> pac900s12_b2_1_inventory;
    pac900s12_b2_1_procurement -> pac900s12_b2_1_inventory;
    kunlun_2280_sales -> pac900s12_b2_1_procurement;
}`;

interface CausalNode {
  id: string;
  label: string;
  x?: number;
  y?: number;
}

interface CausalEdge {
  from: string;
  to: string;
}

function parseDotGraph(dot: string): { nodes: CausalNode[]; edges: CausalEdge[] } {
  const nodes: CausalNode[] = [];
  const edges: CausalEdge[] = [];
  const nodeSet = new Set<string>();
  
  const lines = dot.split('\n');
  for (const line of lines) {
    const edgeMatch = line.match(/(\w+)\s*->\s*(\w+)/);
    if (edgeMatch) {
      const from = edgeMatch[1].trim();
      const to = edgeMatch[2].trim();
      if (!nodeSet.has(from)) {
        nodeSet.add(from);
        nodes.push({ id: from, label: from });
      }
      if (!nodeSet.has(to)) {
        nodeSet.add(to);
        nodes.push({ id: to, label: to });
      }
      edges.push({ from, to });
    }
  }
  
  const nodeCount = nodes.length;
  nodes.forEach((node, idx) => {
    const col = idx % 4;
    const row = Math.floor(idx / 4);
    node.x = col * 200 + 100;
    node.y = row * 150 + 100;
  });
  
  return { nodes, edges };
}

export default function RootCauseAnalysis() {
  const { projectId, nodeId } = useParams<{ projectId: string; nodeId: string }>();
  const navigate = useNavigate();

  const [causalGraph, setCausalGraph] = useState(DEFAULT_CAUSAL_GRAPH);
  const [analysisResults, setAnalysisResults] = useState<api.RootCauseResults | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [fastMode, setFastMode] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const [llmConfig, setLlmConfig] = useState({
    api_key: '',
    model: 'Qwen/Qwen2.5-7B-Instruct',
    base_url: 'https://api.siliconflow.cn/v1',
  });
  const [llmConfigured, setLlmConfigured] = useState(false);
  const [isTestingLlm, setIsTestingLlm] = useState(false);
  const [llmTestResult, setLlmTestResult] = useState<string | null>(null);
  const [isGeneratingExplanation, setIsGeneratingExplanation] = useState(false);
  const [isGeneratingSolution, setIsGeneratingSolution] = useState(false);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [solution, setSolution] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) {
      loadData();
    }
  }, [projectId]);

  useEffect(() => {
    const { nodes: causalNodes, edges: causalEdges } = parseDotGraph(causalGraph);
    
    const flowNodes: Node[] = causalNodes.map((n) => ({
      id: n.id,
      data: { label: n.label },
      position: { x: n.x || 0, y: n.y || 0 },
      style: {
        background: '#fff',
        border: '2px solid #6366f1',
        borderRadius: '8px',
        padding: '12px',
        fontSize: '13px',
        boxShadow: '0 2px 8px rgba(99, 102, 241, 0.15)',
      },
    }));

    const flowEdges: Edge[] = causalEdges.map((e, idx) => ({
      id: `e${idx}`,
      source: e.from,
      target: e.to,
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#6366f1',
      },
      style: { 
        stroke: '#6366f1',
        strokeWidth: 2,
      },
    }));

    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [causalGraph, setNodes, setEdges]);

  const loadData = async () => {
    if (!projectId || !nodeId) return;
    setIsLoading(true);
    try {
      const graphData = await api.getCausalGraph(projectId, nodeId);
      setCausalGraph(graphData.causal_graph || DEFAULT_CAUSAL_GRAPH);
      
      try {
        const results = await api.getRootCauseResults(projectId);
        setAnalysisResults(results);
      } catch (e) {
        console.log('No analysis results yet');
      }
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveGraph = async () => {
    if (!projectId || !nodeId) return;
    try {
      await api.saveCausalGraph(projectId, nodeId, causalGraph);
    } catch (err) {
      console.error('Failed to save graph:', err);
    }
  };

  const handleBuildGraph = async () => {
    try {
      const result = await api.buildCausalGraph('Inventory data analysis');
      setCausalGraph(result.causal_graph);
    } catch (err) {
      console.error('Failed to build graph:', err);
    }
  };

  const handleRunAnalysis = async () => {
    if (!projectId) return;
    setIsAnalyzing(true);
    setError(null);
    setExplanation(null);
    setSolution(null);
    try {
      await handleSaveGraph();
      const results = await api.runRootCauseAnalysis(projectId, causalGraph, fastMode);
      setAnalysisResults(results);
    } catch (err) {
      setError('运行分析失败: ' + (err as Error).message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleTestLlm = async () => {
    if (!llmConfig.api_key) {
      setLlmTestResult('请输入API密钥');
      return;
    }
    setIsTestingLlm(true);
    setLlmTestResult(null);
    try {
      const result = await api.testLLMConnection(llmConfig);
      if (result.success) {
        setLlmTestResult('连接成功！');
        setLlmConfigured(true);
        await api.configureLLM(llmConfig);
      } else {
        setLlmTestResult('连接失败: ' + result.message);
        setLlmConfigured(false);
      }
    } catch (err) {
      setLlmTestResult('测试失败: ' + (err as Error).message);
    } finally {
      setIsTestingLlm(false);
    }
  };

  const handleGenerateExplanation = async () => {
    if (!projectId || !analysisResults) return;
    setIsGeneratingExplanation(true);
    setExplanation(null);
    try {
      const result = await api.generateRootCauseExplanation(projectId, analysisResults, causalGraph);
      setExplanation(result.explanation);
    } catch (err) {
      setExplanation('生成解释失败: ' + (err as Error).message);
    } finally {
      setIsGeneratingExplanation(false);
    }
  };

  const handleGenerateSolution = async () => {
    if (!projectId || !analysisResults) return;
    setIsGeneratingSolution(true);
    setSolution(null);
    try {
      const result = await api.generateSolution(projectId, analysisResults, causalGraph, explanation || undefined);
      setSolution(result.solution);
    } catch (err) {
      setSolution('生成解决方案失败: ' + (err as Error).message);
    } finally {
      setIsGeneratingSolution(false);
    }
  };

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({ 
      ...params, 
      animated: true,
      markerEnd: { type: MarkerType.ArrowClosed, color: '#6366f1' },
      style: { stroke: '#6366f1', strokeWidth: 2 },
    }, eds)),
    [setEdges]
  );

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50">
        <div className="text-indigo-600 flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
          <div>加载中...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50">
      {/* 顶部导航栏 */}
      <div className="bg-white shadow-lg border-b border-indigo-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => navigate(`/flow/${projectId}`)} 
                className="flex items-center gap-2 text-gray-600 hover:text-indigo-600 transition-colors duration-200"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span className="font-medium">返回项目</span>
              </button>
              <div className="h-6 w-px bg-gray-200" />
              <h1 className="text-xl font-bold text-gray-900">根因分析</h1>
            </div>
            <div className="flex items-center gap-3">
              {analysisResults?.counterfactual_analysis && (
                <>
                  <button
                    onClick={handleGenerateExplanation}
                    disabled={!llmConfigured || isGeneratingExplanation}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm hover:shadow-md"
                  >
                    {isGeneratingExplanation ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        生成中...
                      </>
                    ) : (
                      <>
                        <span>🔍</span>
                        根因解释
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleGenerateSolution}
                    disabled={!llmConfigured || isGeneratingSolution}
                    className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm hover:shadow-md"
                  >
                    {isGeneratingSolution ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        生成中...
                      </>
                    ) : (
                      <>
                        <span>💡</span>
                        解决方案
                      </>
                    )}
                  </button>
                </>
              )}
              <button
                onClick={handleRunAnalysis}
                disabled={isAnalyzing}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm hover:shadow-md"
              >
                {isAnalyzing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    分析中...
                  </>
                ) : (
                  <>
                    <span>⚡</span>
                    运行因果分析
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm shadow-sm">
            {error}
          </div>
        )}

        {/* 主要内容网格 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧边栏 */}
          <div className="lg:col-span-1 space-y-4">
            {/* 因果图编辑 */}
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-shadow duration-300">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-indigo-600">📊</span>
                因果图编辑
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">DOT格式</label>
                  <textarea
                    value={causalGraph}
                    onChange={(e) => setCausalGraph(e.target.value)}
                    className="w-full h-48 px-4 py-3 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200 resize-y"
                    placeholder="输入DOT格式的因果图..."
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={handleBuildGraph}
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors duration-200 flex items-center gap-1 shadow-sm"
                  >
                    <span>🤖</span>
                    AI构建
                  </button>
                  <button
                    onClick={handleSaveGraph}
                    className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg text-sm transition-colors duration-200 flex items-center gap-1 border border-gray-200"
                  >
                    <span>💾</span>
                    保存
                  </button>
                  <button
                    onClick={() => setCausalGraph(DEFAULT_CAUSAL_GRAPH)}
                    className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg text-sm transition-colors duration-200 flex items-center gap-1 border border-gray-200"
                  >
                    <span>🔄</span>
                    重置
                  </button>
                </div>
              </div>
            </div>

            {/* 分析设置 */}
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-shadow duration-300">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-indigo-600">⚙️</span>
                分析设置
              </h2>
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={fastMode}
                    onChange={(e) => setFastMode(e.target.checked)}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <label className="text-sm text-gray-700">快速模式 (跳过驳斥检验)</label>
                </div>
              </div>
            </div>

            {/* 大模型配置 */}
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-shadow duration-300">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-indigo-600">🧠</span>
                大模型配置
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">API密钥</label>
                  <input
                    type="password"
                    value={llmConfig.api_key}
                    onChange={(e) => setLlmConfig({ ...llmConfig, api_key: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200"
                    placeholder="输入SiliconFlow API密钥"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">模型</label>
                  <select
                    value={llmConfig.model}
                    onChange={(e) => setLlmConfig({ ...llmConfig, model: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200"
                  >
                    <option value="Qwen/Qwen2.5-7B-Instruct">Qwen2.5-7B-Instruct</option>
                    <option value="Qwen/Qwen2.5-14B-Instruct">Qwen2.5-14B-Instruct</option>
                    <option value="deepseek-ai/DeepSeek-V2-Chat">DeepSeek-V2-Chat</option>
                    <option value="THUDM/glm-4-9b-chat">GLM-4-9B-Chat</option>
                  </select>
                </div>
                <button
                  onClick={handleTestLlm}
                  disabled={isTestingLlm}
                  className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-sm"
                >
                  {isTestingLlm ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      测试中...
                    </>
                  ) : (
                    <>
                      <span>🔌</span>
                      测试连接
                    </>
                  )}
                </button>
                {llmTestResult && (
                  <div className={`text-sm ${llmConfigured ? 'text-green-600' : 'text-red-600'} mt-2 font-medium`}>
                    {llmTestResult}
                  </div>
                )}
              </div>
            </div>

            {/* 节点列表 */}
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-shadow duration-300">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-indigo-600">📋</span>
                节点列表
              </h2>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                {nodes.map((node) => (
                  <div 
                    key={node.id} 
                    className="px-4 py-3 bg-indigo-50 rounded-lg text-sm text-indigo-800 hover:bg-indigo-100 transition-colors duration-200 border border-indigo-100"
                  >
                    {node.data.label}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 右侧内容区 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 因果图画布 */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-indigo-50 to-purple-50">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <span className="text-indigo-600">🖼️</span>
                  因果图可视化
                </h2>
              </div>
              <div className="h-[400px]">
                <ReactFlow
                  nodes={nodes}
                  edges={edges}
                  onNodesChange={onNodesChange}
                  onEdgesChange={onEdgesChange}
                  onConnect={onConnect}
                  fitView
                >
                  <Controls />
                  <Background color="#f8fafc" gap={16} />
                </ReactFlow>
              </div>
            </div>

            {/* 分析结果 */}
            {analysisResults?.counterfactual_analysis && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <span className="text-indigo-600">📈</span>
                  分析结果
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-purple-50 p-4 rounded-lg border border-purple-100 shadow-sm hover:shadow-md transition-shadow duration-200">
                    <div className="text-sm text-purple-600 mb-1 font-medium">库存降低量</div>
                    <div className="text-2xl font-bold text-purple-900">
                      {analysisResults.counterfactual_analysis.inventory_reduction} 单位
                    </div>
                    <div className="text-sm text-purple-600 font-medium">
                      {analysisResults.counterfactual_analysis.reduction_percentage}%
                    </div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 shadow-sm hover:shadow-md transition-shadow duration-200">
                    <div className="text-sm text-blue-600 mb-1 font-medium">实际库存均值</div>
                    <div className="text-2xl font-bold text-blue-900">
                      {analysisResults.counterfactual_analysis.actual_inventory_mean}
                    </div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg border border-green-100 shadow-sm hover:shadow-md transition-shadow duration-200">
                    <div className="text-sm text-green-600 mb-1 font-medium">反事实库存均值</div>
                    <div className="text-2xl font-bold text-green-900">
                      {analysisResults.counterfactual_analysis.counterfactual_inventory_mean}
                    </div>
                    <div className="text-sm text-green-600 font-medium">如果改变原因</div>
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-3 rounded-lg border border-gray-100 shadow-sm">
                    <div className="text-sm text-gray-600 font-medium">下降期实际库存</div>
                    <div className="font-semibold text-gray-900">{analysisResults.counterfactual_analysis.decline_period_actual_inventory}</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg border border-gray-100 shadow-sm">
                    <div className="text-sm text-gray-600 font-medium">下降期反事实库存</div>
                    <div className="font-semibold text-gray-900">{analysisResults.counterfactual_analysis.decline_period_counterfactual_inventory}</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg border border-gray-100 shadow-sm">
                    <div className="text-sm text-gray-600 font-medium">下降期库存降低</div>
                    <div className="font-semibold text-gray-900">{analysisResults.counterfactual_analysis.decline_period_reduction}</div>
                  </div>
                </div>
              </div>
            )}

            {/* 根因解释 */}
            {explanation && (
              <div className="bg-gradient-to-r from-indigo-50 to-indigo-100 rounded-xl shadow-lg p-6 border border-indigo-200">
                <h2 className="text-lg font-semibold text-indigo-900 mb-4 flex items-center gap-2">
                  <span>🔍</span>
                  根因解释
                </h2>
                <div className="prose prose-indigo max-w-none">
                  <ReactMarkdown>{explanation}</ReactMarkdown>
                </div>
              </div>
            )}

            {/* 解决方案 */}
            {solution && (
              <div className="bg-gradient-to-r from-teal-50 to-teal-100 rounded-xl shadow-lg p-6 border border-teal-200">
                <h2 className="text-lg font-semibold text-teal-900 mb-4 flex items-center gap-2">
                  <span>💡</span>
                  解决方案
                </h2>
                <div className="prose prose-teal max-w-none">
                  <ReactMarkdown>{solution}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 页脚 */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            根因分析系统 © 2026 | 基于 DoWhy 和大模型智能分析
          </div>
        </div>
      </footer>
    </div>
  );
}
