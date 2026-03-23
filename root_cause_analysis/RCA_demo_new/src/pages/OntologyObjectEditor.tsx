import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/common/Button';
import { Input, Textarea, Select } from '@/components/common/Input';
import * as api from '@/services/api';

interface Property {
  fieldName: string;
  displayName: string;
  dataType: 'String' | 'Timestamp' | 'Integer' | 'Double';
  isPrimaryKey: boolean;
  indexType: '唯一索引' | '常规索引' | '-';
  isEditable: boolean;
}

interface ChangeHistory {
  action: string;
  user: string;
  time: string;
}

const OntologyObjectEditor = () => {
  const { projectId, ontologyId, objectId } = useParams<{ projectId: string; ontologyId: string; objectId: string }>();
  const navigate = useNavigate();
  
  // 基本信息状态
  const [displayName, setDisplayName] = useState('');
  const [apiName, setApiName] = useState('');
  const [description, setDescription] = useState('');
  
  // 属性列表状态
  const [properties, setProperties] = useState<Property[]>([]);
  
  // 更改历史状态
  const [changeHistory, setChangeHistory] = useState<ChangeHistory[]>([]);
  
  // 加载状态
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  // 数据预览
  const [mockData, setMockData] = useState<any>({});
  
  // 加载对象类型数据
  useEffect(() => {
    const loadObjectType = async () => {
      if (!projectId || !ontologyId || !objectId) return;
      
      setIsLoading(true);
      try {
        // 获取本体数据
        const ontology = await api.getOntology(projectId, parseInt(ontologyId));
        // 找到对应的对象类型
        const objectType = ontology.classes.find(cls => cls.id === parseInt(objectId));
        
        if (objectType) {
          // 设置基本信息
          setDisplayName(objectType.name);
          setApiName(objectType.name.toLowerCase().replace(/\s+/g, '_'));
          setDescription(objectType.description || '');
          
          // 设置属性列表
          const loadedProperties: Property[] = objectType.properties.map(prop => ({
            fieldName: prop.name,
            displayName: prop.name,
            dataType: prop.type as 'String' | 'Timestamp' | 'Integer' | 'Double',
            isPrimaryKey: false, // 默认不是主键
            indexType: '-', // 默认无索引
            isEditable: true
          }));
          setProperties(loadedProperties);
          
          // 生成模拟数据
          const generatedMockData: any = {};
          loadedProperties.forEach(prop => {
            switch (prop.dataType) {
              case 'String':
                generatedMockData[prop.fieldName] = 'Sample value';
                break;
              case 'Timestamp':
                generatedMockData[prop.fieldName] = new Date().toISOString();
                break;
              case 'Integer':
                generatedMockData[prop.fieldName] = Math.floor(Math.random() * 100);
                break;
              case 'Double':
                generatedMockData[prop.fieldName] = Math.random() * 100;
                break;
            }
          });
          setMockData(generatedMockData);
        }
      } catch (error) {
        console.error('Failed to load object type:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadObjectType();
  }, [projectId, ontologyId, objectId]);
  
  const handleAddProperty = () => {
    const newProperty: Property = {
      fieldName: '',
      displayName: '',
      dataType: 'String',
      isPrimaryKey: false,
      indexType: '-',
      isEditable: true
    };
    setProperties([...properties, newProperty]);
  };
  
  const handleSaveAndPublish = async () => {
    if (!projectId || !ontologyId || !objectId) return;
    
    setIsSaving(true);
    try {
      // 更新对象类型基本信息
      await api.updateOntologyClass(
        projectId,
        parseInt(ontologyId),
        parseInt(objectId),
        {
          name: displayName,
          description: description
        }
      );
      
      // 处理属性更新
      for (const property of properties) {
        // 这里需要根据实际情况调用相应的 API
        // 例如，如果是新属性，调用 addClassProperty
        // 如果是现有属性，调用 updateClassProperty
      }
      
      // 添加到更改历史
      const newHistory: ChangeHistory = {
        action: `更新对象类型 ${displayName}`,
        user: '当前用户',
        time: '刚刚'
      };
      setChangeHistory([newHistory, ...changeHistory]);
      
      alert('保存并发布成功');
    } catch (error) {
      console.error('Failed to save object type:', error);
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
              className="flex items-center space-x-3 p-3 rounded-lg bg-blue-50 border-r-2 border-blue-500 transition-colors"
            >
              <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <span className="text-sm font-medium text-blue-700">对象类型</span>
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
            <span className="text-gray-500">本体</span>
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-gray-500">对象类型</span>
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="font-medium text-gray-900">航班记录 (Flight Record)</span>
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
              {/* 基本信息 */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
                <div className="px-6 py-4 border-b border-gray-200 flex items-center space-x-2">
                  <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h3 className="font-medium text-gray-900">基本信息</h3>
                </div>
                <div className="p-6 space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">显示名称</label>
                      <Input
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">唯一标识符 (API Name)</label>
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
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
                      <Input
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        className="w-full"
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              {/* 属性列表 */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    <h3 className="font-medium text-gray-900">属性列表</h3>
                  </div>
                  <Button onClick={handleAddProperty} variant="primary" size="sm">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    添加新属性
                  </Button>
                </div>
                
                {/* 属性表格 */}
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">字段名</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">显示名</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数据类型</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">主键</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">索引</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {properties.map((property, index) => (
                        <tr key={index} className={!property.isEditable ? 'opacity-50' : ''}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {property.fieldName}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {property.displayName}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              property.dataType === 'String' ? 'bg-blue-100 text-blue-800' :
                              property.dataType === 'Timestamp' ? 'bg-purple-100 text-purple-800' :
                              property.dataType === 'Integer' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {property.dataType}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {property.isPrimaryKey ? (
                              <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            ) : (
                              <svg className="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {property.indexType}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {property.isEditable ? (
                              <svg className="w-4 h-4 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                              </svg>
                            ) : (
                              <svg className="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                              </svg>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
      
      {/* 右侧预览和操作 */}
      <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
        {/* 数据预览 */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-900">数据预览 (Mock)</h3>
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <div className="bg-gray-900 rounded-lg p-4 text-gray-300 font-mono text-sm">
            <pre>
{
  JSON.stringify(mockData, null, 2)
}
            </pre>
          </div>
        </div>
        
        {/* 更改历史 */}
        <div className="flex-1 p-4 border-b border-gray-200 overflow-y-auto">
          <h3 className="font-medium text-gray-900 mb-3">更改历史</h3>
          <div className="space-y-4">
            {changeHistory.map((history, index) => (
              <div key={index} className="relative pl-6">
                <div className="absolute left-0 top-1.5 w-2 h-2 rounded-full bg-blue-500"></div>
                <div className="border-l-2 border-blue-200 pl-4 py-1">
                  <p className="text-sm font-medium text-gray-900">{history.action}</p>
                  <p className="text-xs text-gray-500 mt-1">{history.user} · {history.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* 发布控制 */}
        <div className="p-4 space-y-2">
          <Button 
            onClick={handleSaveAndPublish} 
            variant="primary" 
            className="w-full"
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
          <Button 
            onClick={handleDiscardDraft} 
            variant="secondary" 
            className="w-full"
            disabled={isSaving}
          >
            放弃草稿
          </Button>
        </div>
      </div>
    </div>
  );
};

export default OntologyObjectEditor;