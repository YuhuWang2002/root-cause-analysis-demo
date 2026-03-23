import { useParams, useNavigate } from 'react-router-dom';
import React, { useState, useCallback } from 'react';
import ReactFlow, { addEdge, Background, Controls, useNodesState, useEdgesState, Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';

const DataPipelineBuilder = () => {
  const { projectId, pipelineId } = useParams<{ projectId: string; pipelineId: string }>();
  const navigate = useNavigate();

  // 定义节点类型
  const nodeTypes = {
    source: {
      // 源节点组件
    },
    processing: {
      // 处理节点组件
    },
    aggregate: {
      // 聚合节点组件
    },
    terminal: {
      // 终端节点组件
    },
  };

  // 初始节点
  const initialNodes: Node[] = [
    {
      id: 'procurement',
      type: 'source',
      data: { label: '采购 (Procurement)' },
      position: { x: 100, y: 50 },
      style: {
        background: '#f8f9fa',
        border: '1px solid #dee2e6',
        borderRadius: '8px',
        padding: '10px',
      },
    },
    {
      id: 'warehouse',
      type: 'source',
      data: { label: '仓库 (Warehouse)' },
      position: { x: 100, y: 150 },
      style: {
        background: '#f8f9fa',
        border: '1px solid #dee2e6',
        borderRadius: '8px',
        padding: '10px',
      },
    },
    {
      id: 'production',
      type: 'source',
      data: { label: '生产 (Production)' },
      position: { x: 100, y: 250 },
      style: {
        background: '#f8f9fa',
        border: '1px solid #dee2e6',
        borderRadius: '8px',
        padding: '10px',
      },
    },
    {
      id: 'sales',
      type: 'source',
      data: { label: '销售 (Sales)' },
      position: { x: 100, y: 350 },
      style: {
        background: '#f8f9fa',
        border: '1px solid #dee2e6',
        borderRadius: '8px',
        padding: '10px',
      },
    },
    {
      id: 'join',
      type: 'processing',
      data: { label: '关联 (JOIN)' },
      position: { x: 400, y: 100 },
      style: {
        background: '#e3f2fd',
        border: '1px solid #90caf9',
        borderRadius: '8px',
        padding: '10px',
      },
    },
    {
      id: 'clean',
      type: 'processing',
      data: { label: '数据清洗 (CLEAN)' },
      position: { x: 400, y: 250 },
      style: {
        background: '#e8f5e8',
        border: '1px solid #a5d6a7',
        borderRadius: '8px',
        padding: '10px',
      },
    },
    {
      id: 'aggregate',
      type: 'aggregate',
      data: { label: '聚合 (AGGREGATE)' },
      position: { x: 700, y: 175 },
      style: {
        background: '#fff3e0',
        border: '1px solid #ffcc80',
        borderRadius: '8px',
        padding: '10px',
      },
    },
    {
      id: 'terminal',
      type: 'terminal',
      data: { label: '企业主数据集 (Enterprise Master Dataset)' },
      position: { x: 950, y: 175 },
      style: {
        background: '#e1bee7',
        border: '1px solid #ce93d8',
        borderRadius: '8px',
        padding: '10px',
      },
    },
  ];

  // 初始边
  const initialEdges: Edge[] = [
    { id: 'e1', source: 'procurement', target: 'join' },
    { id: 'e2', source: 'warehouse', target: 'join' },
    { id: 'e3', source: 'production', target: 'clean' },
    { id: 'e4', source: 'sales', target: 'clean' },
    { id: 'e5', source: 'join', target: 'aggregate' },
    { id: 'e6', source: 'clean', target: 'aggregate' },
    { id: 'e7', source: 'aggregate', target: 'terminal' },
  ];

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback((params) => {
    setEdges((eds) => addEdge(params, eds));
  }, [setEdges]);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* 顶部导航栏 */}
      <div className="h-16 bg-white border-b flex items-center px-6 justify-between shrink-0">
        <div className="flex items-center gap-8">
          <h1 className="text-xl font-semibold text-gray-900">数据管道建模器</h1>
          <div className="flex items-center gap-6">
            <a href="#" className="text-blue-600 font-medium">项目预览</a>
            <a href="#" className="text-gray-600 hover:text-gray-900">资源管理</a>
            <a href="#" className="text-gray-600 hover:text-gray-900">节点库</a>
            <a href="#" className="text-gray-600 hover:text-gray-900">历史版本</a>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button className="text-gray-600 hover:text-gray-900">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </button>
          <button className="text-gray-600 hover:text-gray-900">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </button>
          <button className="text-gray-600 hover:text-gray-900">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
            <span className="text-gray-700 font-medium">U</span>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* 左侧边栏 */}
        <div className="w-64 bg-white border-r flex flex-col shrink-0">
          <div className="p-4 border-b">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-gray-900">节点资源</h3>
                <p className="text-xs text-gray-500">工业级组件库</p>
              </div>
            </div>
            <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
              新建节点
            </button>
          </div>
          <div className="flex-1 overflow-auto p-4">
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
                <span className="text-sm font-medium text-gray-700">源数据集</span>
              </div>
              <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <span className="text-sm font-medium text-gray-700">转换操作</span>
              </div>
              <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm font-medium text-gray-700">输出结果</span>
              </div>
              <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
                <span className="text-sm font-medium text-gray-700">连接</span>
              </div>
              <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                <span className="text-sm font-medium text-gray-700">过滤</span>
              </div>
              <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span className="text-sm font-medium text-gray-700">聚合</span>
              </div>
            </div>
          </div>
        </div>

        {/* 主画布区域 */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 relative">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              nodeTypes={nodeTypes}
              fitView
            >
              <Background variant="dots" gap={16} size={1} />
              <Controls />
            </ReactFlow>
          </div>

          {/* 数据预览区域 */}
          <div className="h-64 bg-white border-t">
            <div className="p-4 flex items-center justify-between border-b">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="font-medium text-gray-900">数据预览 (实时抽取)</h3>
              </div>
              <div className="flex items-center gap-2">
                <button className="p-2 rounded-lg hover:bg-gray-100">
                  <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
                <button className="p-2 rounded-lg hover:bg-gray-100">
                  <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="overflow-auto h-48">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium text-gray-600 border-b">TRANS_ID</th>
                    <th className="px-4 py-2 text-left font-medium text-gray-600 border-b">ENTITY_SOURCE</th>
                    <th className="px-4 py-2 text-left font-medium text-gray-600 border-b">PRODUCT_GROUP</th>
                    <th className="px-4 py-2 text-left font-medium text-gray-600 border-b">QUANTITY</th>
                    <th className="px-4 py-2 text-left font-medium text-gray-600 border-b">VALUE_USD</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-2 border-b text-gray-900">TXN-001293</td>
                    <td className="px-4 py-2 border-b text-gray-900">PROCUREMENT</td>
                    <td className="px-4 py-2 border-b text-gray-900">RAW_METAL</td>
                    <td className="px-4 py-2 border-b text-gray-900">1,240.00</td>
                    <td className="px-4 py-2 border-b text-gray-900">$14,500.00</td>
                  </tr>
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-2 border-b text-gray-900">TXN-001294</td>
                    <td className="px-4 py-2 border-b text-gray-900">SALES</td>
                    <td className="px-4 py-2 border-b text-gray-900">FINISHED_ENG</td>
                    <td className="px-4 py-2 border-b text-gray-900">42.00</td>
                    <td className="px-4 py-2 border-b text-gray-900">$89,200.00</td>
                  </tr>
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-2 border-b text-gray-900">TXN-001295</td>
                    <td className="px-4 py-2 border-b text-gray-900">WAREHOUSE</td>
                    <td className="px-4 py-2 border-b text-gray-900">SEMICON</td>
                    <td className="px-4 py-2 border-b text-gray-900">8,000.00</td>
                    <td className="px-4 py-2 border-b text-gray-900">$2,400.00</td>
                  </tr>
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-2 border-b text-gray-900">TXN-001296</td>
                    <td className="px-4 py-2 border-b text-gray-900">PRODUCTION</td>
                    <td className="px-4 py-2 border-b text-gray-900">GEAR_BOX</td>
                    <td className="px-4 py-2 border-b text-gray-900">120.00</td>
                    <td className="px-4 py-2 border-b text-gray-900">$15,800.00</td>
                  </tr>
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-2 border-b text-gray-900">TXN-001297</td>
                    <td className="px-4 py-2 border-b text-gray-900">SALES</td>
                    <td className="px-4 py-2 border-b text-gray-900">TURBINE_S1</td>
                    <td className="px-4 py-2 border-b text-gray-900">4.00</td>
                    <td className="px-4 py-2 border-b text-gray-900">$340,000.00</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataPipelineBuilder;