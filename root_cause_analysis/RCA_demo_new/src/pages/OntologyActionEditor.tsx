import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/common/Button';
import { Input, Select, Textarea } from '@/components/common/Input';
import * as api from '@/services/api';

interface ParameterMapping {
  sourceField: string;
  targetField: string;
}

interface Variable {
  name: string;
  type: string;
  defaultValue: string;
}

interface RecentExecution {
  orderId: string;
  time: string;
  status: 'success' | 'failed';
}

const OntologyActionEditor = () => {
  const { projectId, ontologyId, actionId } = useParams<{ projectId: string; ontologyId: string; actionId: string }>();
  const navigate = useNavigate();
  
  // 基本信息状态
  const [actionName, setActionName] = useState('');
  const [apiName, setApiName] = useState('');
  const [description, setDescription] = useState('');
  
  // 触发器设置状态
  const [eventType, setEventType] = useState('Object Updated');
  const [sourceObject, setSourceObject] = useState('Order');
  const [triggerCondition, setTriggerCondition] = useState('Status == \'Completed\'');
  
  // 执行逻辑状态
  const [logicType, setLogicType] = useState('API 调用'); // API 调用 或 脚本执行
  const [targetSystem, setTargetSystem] = useState('企业资源计划 (ERP)');
  
  // 参数映射状态
  const [parameterMappings, setParameterMappings] = useState<ParameterMapping[]>([]);
  
  // 输入/输出状态
  const [variables, setVariables] = useState<Variable[]>([]);
  
  // 最近执行状态
  const [recentExecutions, setRecentExecutions] = useState<RecentExecution[]>([]);
  
  // 执行成功率
  const [successRate, setSuccessRate] = useState('98.4%');
  
  // 加载状态
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  // 加载操作数据
  useEffect(() => {
    const loadAction = async () => {
      if (!projectId || !ontologyId || !actionId) return;
      
      setIsLoading(true);
      try {
        // 获取本体数据
        const ontology = await api.getOntology(projectId, parseInt(ontologyId));
        // 找到对应的操作
        const action = ontology.actions.find(a => a.id === parseInt(actionId));
        
        if (action) {
          // 设置基本信息
          setActionName(action.name);
          setApiName(action.api_name);
          setDescription(action.description || '');
          
          // 设置触发器
          setEventType(action.event_type);
          setSourceObject(action.source_object);
          setTriggerCondition(action.trigger_condition || '');
          
          // 设置执行逻辑
          setLogicType(action.logic_type);
          setTargetSystem(action.target_system || '');
          
          // 设置参数映射
          const loadedMappings: ParameterMapping[] = action.parameter_mappings.map((mapping: any) => ({
            sourceField: mapping.sourceField || mapping.source_field || '',
            targetField: mapping.targetField || mapping.target_field || ''
          }));
          setParameterMappings(loadedMappings);
          
          // 设置变量
          const loadedVariables: Variable[] = action.variables.map((variable: any) => ({
            name: variable.name,
            type: variable.type,
            defaultValue: variable.defaultValue || variable.default_value || ''
          }));
          setVariables(loadedVariables);
          
          // 设置最近执行（模拟数据）
          const mockExecutions: RecentExecution[] = [
            {
              orderId: '#ORD-9021',
              time: '2 分钟前',
              status: 'success'
            },
            {
              orderId: '#ORD-8944',
              time: '14 分钟前',
              status: 'success'
            },
            {
              orderId: '#ORD-8812',
              time: '1 小时前',
              status: 'failed'
            }
          ];
          setRecentExecutions(mockExecutions);
          
          setSuccessRate('98.4%');
        }
      } catch (error) {
        console.error('Failed to load action:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadAction();
  }, [projectId, ontologyId, actionId]);
  
  const handleAddMapping = () => {
    const newMapping: ParameterMapping = {
      sourceField: '',
      targetField: ''
    };
    setParameterMappings([...parameterMappings, newMapping]);
  };
  
  const handleRemoveMapping = (index: number) => {
    setParameterMappings(parameterMappings.filter((_, idx) => idx !== index));
  };
  
  const handleAddVariable = () => {
    const newVariable: Variable = {
      name: '',
      type: 'String',
      defaultValue: 'None'
    };
    setVariables([...variables, newVariable]);
  };
  
  const handleRemoveVariable = (index: number) => {
    setVariables(variables.filter((_, idx) => idx !== index));
  };
  
  const handleSaveAndPublish = async () => {
    if (!projectId || !ontologyId || !actionId) return;
    
    setIsSaving(true);
    try {
      // 调用后台 API 保存操作更改
      await api.updateOntologyAction(
        projectId,
        parseInt(ontologyId),
        parseInt(actionId),
        {
          name: actionName,
          api_name: apiName,
          description: description,
          event_type: eventType,
          source_object: sourceObject,
          trigger_condition: triggerCondition,
          logic_type: logicType,
          target_system: targetSystem,
          parameter_mappings: parameterMappings,
          variables: variables
        }
      );
      
      alert('保存并发布成功');
    } catch (error) {
      console.error('Failed to save action:', error);
      alert('保存失败: ' + (error as Error).message);
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleDiscardDraft = () => {
    // 放弃草稿的逻辑
    if (confirm('确定要放弃草稿吗？未保存的更改将会丢失。')) {
      // 重新加载数据
      window.location.reload();
    }
  };
  
  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧导航栏 */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* 头部 */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-500 rounded flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <h2 className="font-medium text-gray-900">配置菜单</h2>
              <p className="text-xs text-gray-500">工业级架构</p>
            </div>
          </div>
        </div>
        
        {/* 导航菜单 */}
        <div className="flex-1 p-4">
          <nav className="space-y-1">
            <Link
              to={`/ontology/${projectId}/${ontologyId}/object/1`}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <span className="text-sm font-medium text-gray-700">对象类型</span>
            </Link>
            
            <Link
              to={`/ontology/${projectId}/${ontologyId}/link/1`}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span className="text-sm font-medium text-gray-700">链接类型</span>
            </Link>
            
            <Link
              to={`/ontology/${projectId}/${ontologyId}/action/1`}
              className="flex items-center space-x-3 p-3 rounded-lg bg-blue-50 border-r-2 border-blue-500 transition-colors"
            >
              <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span className="text-sm font-medium text-blue-700">操作</span>
            </Link>
            
            <Link
              to={`/ontology/${projectId}/${ontologyId}/share`}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
              <span className="text-sm font-medium text-gray-700">共享</span>
            </Link>
          </nav>
        </div>
      </div>
      
      {/* 主工作区 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* 面包屑导航 */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <span className="text-gray-500">本体列表</span>
            <span className="text-gray-500">/</span>
            <span className="text-gray-500">订单管理</span>
            <span className="text-gray-500">/</span>
            <span className="font-medium text-gray-900">动作配置</span>
          </div>
        </div>
        
        {/* 内容区域 */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">动作配置 : 订单自动同步</h1>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 左侧内容 */}
            <div className="lg:col-span-2 space-y-6">
              {/* 基本信息 */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="font-medium text-gray-900 mb-4">基本信息</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">动作名称</label>
                    <Input
                      value={actionName}
                      onChange={(e) => setActionName(e.target.value)}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">API 名称</label>
                    <Input
                      value={apiName}
                      onChange={(e) => setApiName(e.target.value)}
                      className="w-full"
                    />
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
                  <Textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full"
                    rows={3}
                  />
                </div>
              </div>
              
              {/* 触发器设置 */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="font-medium text-gray-900 mb-4">触发器设置</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">事件类型</label>
                    <div className="flex items-center space-x-2 p-3 border border-gray-200 rounded-lg">
                      <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-sm text-gray-700">对象已更新 (Object Updated)</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">源对象</label>
                    <div className="flex items-center space-x-2 p-3 border border-gray-200 rounded-lg">
                      <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      <span className="text-sm text-gray-700">订单 (Order)</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">触发条件</label>
                    <div className="p-3 border border-gray-200 rounded-lg bg-gray-50">
                      <span className="text-sm font-mono text-gray-700">Status == 'Completed'</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* 执行逻辑 */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="font-medium text-gray-900 mb-4">执行逻辑</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">逻辑类型</label>
                    <div className="flex space-x-3">
                      <button
                        onClick={() => setLogicType('API 调用')}
                        className={`flex items-center space-x-2 px-4 py-2 border rounded-lg transition-colors ${logicType === 'API 调用' ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-200 hover:border-gray-300 text-gray-700'}`}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                        </svg>
                        <span>API 调用</span>
                      </button>
                      <button
                        onClick={() => setLogicType('脚本执行')}
                        className={`flex items-center space-x-2 px-4 py-2 border rounded-lg transition-colors ${logicType === '脚本执行' ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-200 hover:border-gray-300 text-gray-700'}`}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span>脚本执行</span>
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">目标系统</label>
                    <div className="flex items-center space-x-2 p-3 border border-gray-200 rounded-lg">
                      <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                      </svg>
                      <span className="text-sm text-gray-700">企业资源计划 (ERP)</span>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">参数映射 (Parameter Mapping)</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">源字段 (Source)</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">映射</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">目标字段 (Target)</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {parameterMappings.map((mapping, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {mapping.sourceField}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                              </svg>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {mapping.targetField}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              
              {/* 输入/输出 */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-medium text-gray-900">输入/输出</h3>
                  <Button onClick={handleAddVariable} variant="secondary" size="sm">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    添加变量
                  </Button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">变量名称</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数据类型</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">默认值</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {variables.map((variable, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {variable.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              variable.type === 'String' ? 'bg-blue-100 text-blue-800' :
                              variable.type === 'Number' ? 'bg-green-100 text-green-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {variable.type}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {variable.defaultValue}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <button
                              onClick={() => handleRemoveVariable(index)}
                              className="text-red-500 hover:text-red-700"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            
            {/* 右侧边栏 */}
            <div className="space-y-6">
              {/* 动作摘要 */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-medium text-gray-900">动作摘要</h3>
                  <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    已激活
                  </span>
                </div>
                
                {/* 视觉流程图 */}
                <div className="mb-6">
                  <div className="flex flex-col items-center space-y-4">
                    {/* 触发源 */}
                    <div className="flex flex-col items-center">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                      <p className="text-sm font-medium text-gray-900">触发源</p>
                      <p className="text-xs text-gray-600 text-center">订单更新事件</p>
                    </div>
                    
                    {/* 箭头 */}
                    <div className="w-0.5 h-8 bg-gray-300"></div>
                    
                    {/* 执行逻辑 */}
                    <div className="flex flex-col items-center">
                      <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-2">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                        </svg>
                      </div>
                      <p className="text-sm font-medium text-gray-900">执行逻辑</p>
                      <p className="text-xs text-gray-600 text-center">API: POST /sync/erp</p>
                    </div>
                    
                    {/* 箭头 */}
                    <div className="w-0.5 h-8 bg-gray-300"></div>
                    
                    {/* 输出结果 */}
                    <div className="flex flex-col items-center">
                      <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-2">
                        <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <p className="text-sm font-medium text-gray-900">输出结果</p>
                      <p className="text-xs text-gray-600 text-center">ERP 响应回执</p>
                    </div>
                  </div>
                </div>
                
                {/* 最近执行 */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-medium text-gray-700">最近执行</h4>
                    <a href="#" className="text-sm text-blue-600 hover:text-blue-800">查看全部</a>
                  </div>
                  <div className="space-y-3">
                    {recentExecutions.map((execution, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-2">
                          <div className={`w-3 h-3 rounded-full ${execution.status === 'success' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                          <span className="text-sm font-medium text-gray-900">{execution.orderId}</span>
                        </div>
                        <span className="text-xs text-gray-500">{execution.time}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* 执行成功率 */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3">执行成功率</h4>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-end justify-between mb-2">
                      <p className="text-sm text-gray-600">执行成功率</p>
                      <p className="text-2xl font-semibold text-gray-900">{successRate}</p>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-600 rounded-full" style={{ width: successRate }}></div>
                    </div>
                    <div className="mt-2 flex justify-between text-xs text-gray-500">
                      <span>过去 7 天</span>
                      <span>98.4%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* 底部操作栏 */}
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-end space-x-3">
            <Button onClick={handleDiscardDraft} variant="secondary">
              放弃草稿
            </Button>
            <Button onClick={handleSaveAndPublish} variant="primary">
              保存并发布更改
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OntologyActionEditor;