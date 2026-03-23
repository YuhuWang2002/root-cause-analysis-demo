import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/common/Button';
import { Input, Select, Textarea } from '@/components/common/Input';
import * as api from '@/services/api';

interface FieldMapping {
  sourceField: string;
  sourceType: string;
  targetField: string;
  targetType: string;
  transformType: string;
}

interface ChangeHistory {
  action: string;
  time: string;
  user: string;
  details?: string;
}

const OntologyLinkEditor = () => {
  const { projectId, ontologyId, linkId } = useParams<{ projectId: string; ontologyId: string; linkId: string }>();
  const navigate = useNavigate();
  
  // 基本信息状态
  const [displayName, setDisplayName] = useState('');
  const [apiName, setApiName] = useState('');
  const [isActive, setIsActive] = useState(true);
  
  // 关系配置状态
  const [cardinality, setCardinality] = useState('1:N'); // 1:N 或 N:N
  
  // 字段映射状态
  const [fieldMappings, setFieldMappings] = useState<FieldMapping[]>([]);
  
  // 更改历史状态
  const [changeHistory, setChangeHistory] = useState<ChangeHistory[]>([]);
  
  // 加载状态
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  // 未保存的更改计数
  const [unsavedChanges, setUnsavedChanges] = useState(0);
  
  // 加载链接类型数据
  useEffect(() => {
    const loadLinkType = async () => {
      if (!projectId || !ontologyId || !linkId) return;
      
      setIsLoading(true);
      try {
        // 获取本体数据
        const ontology = await api.getOntology(projectId, parseInt(ontologyId));
        // 找到对应的链接类型
        const linkType = ontology.relations.find(rel => rel.id === parseInt(linkId));
        
        if (linkType) {
          // 设置基本信息
          setDisplayName(linkType.relation_type);
          setApiName(linkType.relation_type.toLowerCase().replace(/\s+/g, '_'));
          setIsActive(true);
          
          // 设置关系配置
          setCardinality('1:N'); // 默认一对多关系
          
          // 设置字段映射（模拟数据）
          const mockMappings: FieldMapping[] = [
            {
              sourceField: 'id',
              sourceType: 'Integer',
              targetField: 'source_id',
              targetType: 'Integer',
              transformType: 'Exact Match'
            },
            {
              sourceField: 'name',
              sourceType: 'String',
              targetField: 'source_name',
              targetType: 'String',
              transformType: 'Exact Match'
            }
          ];
          setFieldMappings(mockMappings);
          
          // 设置更改历史
          const mockHistory: ChangeHistory[] = [
            {
              action: '创建了链接类型',
              time: new Date().toLocaleString(),
              user: '当前用户'
            }
          ];
          setChangeHistory(mockHistory);
        }
      } catch (error) {
        console.error('Failed to load link type:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadLinkType();
  }, [projectId, ontologyId, linkId]);
  
  const handleAddMapping = () => {
    const newMapping: FieldMapping = {
      sourceField: '',
      sourceType: 'String',
      targetField: '',
      targetType: 'String',
      transformType: 'Exact Match'
    };
    setFieldMappings([...fieldMappings, newMapping]);
    setUnsavedChanges(prev => prev + 1);
  };
  
  const handleRemoveMapping = (index: number) => {
    setFieldMappings(fieldMappings.filter((_, idx) => idx !== index));
    setUnsavedChanges(prev => prev + 1);
  };
  
  const handleSaveAndPublish = async () => {
    if (!projectId || !ontologyId || !linkId) return;
    
    setIsSaving(true);
    try {
      // 这里需要调用后台 API 保存链接类型更改
      // 由于 API 尚未实现，我们先模拟保存
      console.log('保存链接类型更改:', {
        displayName,
        apiName,
        isActive,
        cardinality,
        fieldMappings
      });
      
      // 添加到更改历史
      const newHistory: ChangeHistory = {
        action: `更新链接类型 ${displayName}`,
        time: new Date().toLocaleString(),
        user: '当前用户'
      };
      setChangeHistory([newHistory, ...changeHistory]);
      
      setUnsavedChanges(0);
      alert('保存并发布成功');
    } catch (error) {
      console.error('Failed to save link type:', error);
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
  
  const handleOpenGraphEditor = () => {
    // 进入图形编辑器的逻辑
    console.log('进入图形编辑器');
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
              className="flex items-center space-x-3 p-3 rounded-lg bg-blue-50 border-r-2 border-blue-500 transition-colors"
            >
              <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span className="text-sm font-medium text-blue-700">链接类型</span>
            </Link>
            
            <Link
              to={`/ontology/${projectId}/${ontologyId}/action/1`}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span className="text-sm font-medium text-gray-700">操作</span>
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
            <span className="text-gray-500">Definitions</span>
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-gray-500">Link Types</span>
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="font-medium text-gray-900">Flight-Airport</span>
          </div>
        </div>
        
        {/* 内容区域 */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <>
              <div className="mb-6">
                <h1 className="text-2xl font-semibold text-gray-900 mb-2">链接配置：{displayName}</h1>
                <p className="text-gray-600">配置链接类型的语义链接和字段映射。</p>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* 左侧和中间内容 */}
                <div className="lg:col-span-2 space-y-6">
                  {/* 基本信息和关系配置 */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* 基本信息 */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-medium text-gray-900">基本信息</h3>
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                          {isActive ? 'ACTIVE' : 'INACTIVE'}
                        </span>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">显示名称</label>
                          <Input
                            value={displayName}
                            onChange={(e) => setDisplayName(e.target.value)}
                            className="w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">API 名称</label>
                          <div className="relative">
                            <Input
                              value={apiName}
                              onChange={(e) => setApiName(e.target.value)}
                              className="w-full pr-10"
                            />
                            <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                              </svg>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* 关系配置 */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <h3 className="font-medium text-gray-900 mb-4">关系配置</h3>
                      <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">基数配置 (Cardinality)</label>
                        <div className="grid grid-cols-2 gap-4">
                          <button
                            onClick={() => setCardinality('1:N')}
                            className={`p-4 border rounded-lg text-center transition-colors ${cardinality === '1:N' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}
                          >
                            <p className="font-medium text-gray-900">1 : N</p>
                            <p className="text-sm text-gray-600">一对多</p>
                          </button>
                          <button
                            onClick={() => setCardinality('N:N')}
                            className={`p-4 border rounded-lg text-center transition-colors ${cardinality === 'N:N' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}
                          >
                            <p className="font-medium text-gray-900">N : N</p>
                            <p className="text-sm text-gray-600">多对多</p>
                          </button>
                        </div>
                      </div>
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-600">
                          {cardinality === '1:N' ? '一个源对象可关联多个目标对象，一个目标对象仅对应一个源对象。' : '一个源对象可关联多个目标对象，一个目标对象也可对应多个源对象。'}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {/* 字段映射表 */}
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium text-gray-900">字段映射表 (Field Mapping)</h3>
                      <Button onClick={handleAddMapping} variant="secondary" size="sm">
                        添加映射项
                      </Button>
                    </div>
                    
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">源对象字段</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">目标对象字段</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">转换类型</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {fieldMappings.map((mapping, index) => (
                            <tr key={index}>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div>
                                  <p className="text-sm font-medium text-gray-900">{mapping.sourceField}</p>
                                  <p className="text-xs text-gray-500">{mapping.sourceType}</p>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div>
                                  <p className="text-sm font-medium text-gray-900">{mapping.targetField}</p>
                                  <p className="text-xs text-gray-500">{mapping.targetType}</p>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                  {mapping.transformType}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <button
                                  onClick={() => handleRemoveMapping(index)}
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
                  {/* 链接预览 */}
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h3 className="font-medium text-gray-900 mb-4">链接预览 (Link Preview)</h3>
                    <div className="p-4 bg-gray-50 rounded-lg mb-4">
                      <div className="flex items-center justify-center space-x-8">
                        <div className="text-center">
                          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-2 mx-auto">
                            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                          </div>
                          <p className="font-medium text-gray-900">源对象</p>
                        </div>
                        
                        <div className="flex flex-col items-center">
                          <div className="w-16 h-1 bg-gray-300"></div>
                          <div className="px-2 py-1 bg-blue-100 rounded text-xs font-medium text-blue-800">
                            {cardinality}
                          </div>
                          <div className="w-16 h-1 bg-gray-300"></div>
                        </div>
                        
                        <div className="text-center">
                          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-2 mx-auto">
                            <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                          </div>
                          <p className="font-medium text-gray-900">目标对象</p>
                        </div>
                      </div>
                    </div>
                    <Button onClick={handleOpenGraphEditor} variant="secondary" className="w-full">
                      进入图形编辑器
                    </Button>
                  </div>
                  
                  {/* 更改记录 */}
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h3 className="font-medium text-gray-900 mb-4">更改记录 (Change History)</h3>
                    <div className="space-y-4">
                      {changeHistory.map((history, index) => (
                        <div key={index} className="relative pl-6">
                          <div className="absolute left-0 top-1.5 w-2 h-2 rounded-full bg-blue-500"></div>
                          <div className="border-l-2 border-blue-200 pl-4 py-1">
                            <p className="text-sm font-medium text-gray-900">{history.action}</p>
                            <p className="text-xs text-gray-500 mt-1">{history.time} · {history.user}</p>
                            {history.details && (
                              <p className="text-xs text-gray-600 mt-1 bg-gray-50 p-2 rounded">
                                {history.details}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
      
      {/* 底部操作栏 */}
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between">
            {unsavedChanges > 0 && (
              <div className="flex items-center space-x-2 text-amber-600">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-.77-1.964-.77-2.732 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span className="text-sm font-medium">{unsavedChanges} 个未保存的更改</span>
              </div>
            )}
            <div className="flex space-x-3">
              <Button 
                onClick={handleDiscardDraft} 
                variant="secondary"
                disabled={isSaving}
              >
                放弃草稿
              </Button>
              <Button 
                onClick={handleSaveAndPublish} 
                variant="primary"
                disabled={isSaving}
              >
                {isSaving ? (
                  <>
                    <svg className="w-4 h-4 mr-1 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    保存中...
                  </>
                ) : (
                  "保存并发布更改"
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OntologyLinkEditor;