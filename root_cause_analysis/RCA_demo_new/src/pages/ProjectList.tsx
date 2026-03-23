import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input, Select } from '@/components/common/Input';
import { CreateProjectModal } from '@/components/common/CreateProjectModal';
import { useProjectStore } from '@/stores/projectStore';
import type { Project } from '@/types';

const scenarioLabels: Record<string, string> = {
  system_anomaly: '系统异常分析',
  performance: '性能问题分析',
  quality: '质量问题分析',
  custom: '自定义场景',
};

const statusLabels: Record<string, { text: string; color: string }> = {
  draft: { text: '草稿', color: 'bg-gray-100 text-gray-700' },
  running: { text: '进行中', color: 'bg-blue-100 text-blue-700' },
  completed: { text: '已完成', color: 'bg-green-100 text-green-700' },
  failed: { text: '失败', color: 'bg-red-100 text-red-700' },
};

function ProjectCard({ project, onClick, onDelete }: { project: Project; onClick: () => void; onDelete: (id: string) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
    >
      <Card hover onClick={onClick}>
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">{project.name}</h3>
            <p className="text-sm text-gray-500">{scenarioLabels[project.scenario] || project.scenario}</p>
          </div>
          <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusLabels[project.status].color}`}>
            {statusLabels[project.status].text}
          </span>
        </div>

        <p className="text-sm text-gray-600 mb-4 line-clamp-2">{project.description}</p>

        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1.5">
            <span>进度</span>
            <span>{project.progress}%</span>
          </div>
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${project.progress}%` }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="h-full bg-primary rounded-full"
            />
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>创建于 {new Date(project.createdAt).toLocaleDateString('zh-CN')}</span>
          <div className="flex space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
              }}
              className="p-1.5 hover:bg-gray-100 rounded transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(project.id);
              }}
              className="p-1.5 hover:bg-gray-100 rounded transition-colors text-gray-400 hover:text-error"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}

function EmptyState({ onCreateClick }: { onCreateClick: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col items-center justify-center py-20"
    >
      <div className="w-32 h-32 mb-6 bg-gray-100 rounded-full flex items-center justify-center">
        <svg className="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">暂无项目</h3>
      <p className="text-gray-500 mb-6 text-center max-w-sm">
        创建您的第一个根因分析项目，开始探索数据中的隐藏规律
      </p>
      <Button onClick={onCreateClick}>
        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        创建项目
      </Button>
    </motion.div>
  );
}

export default function ProjectList() {
  const navigate = useNavigate();
  const { searchQuery, statusFilter, sortBy, setSearchQuery, setStatusFilter, setSortBy, getFilteredProjects, projects, addProject, deleteProject, fetchProjects } = useProjectStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deleteProjectId, setDeleteProjectId] = useState<string | null>(null);
  
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);
  
  const filteredProjects = getFilteredProjects();

  const handleCreateProject = async (name: string, description: string, scenario: string) => {
    const newProjectId = await addProject({
      name,
      description,
      scenario,
      status: 'draft',
      progress: 0,
    });
    setIsModalOpen(false);
    navigate(`/flow/${newProjectId}`);
  };

  const handleDeleteProject = (id: string) => {
    deleteProject(id);
    setDeleteProjectId(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-display font-semibold text-gray-900 mb-1">我的项目</h1>
            <p className="text-gray-500">共 {projects.length} 个分析项目</p>
          </div>
          <Button onClick={() => setIsModalOpen(true)}>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            新建项目
          </Button>
        </div>

        <div className="flex flex-wrap gap-4 mb-6 p-4 bg-white rounded-lg shadow-sm">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="搜索项目名称..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="w-40">
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              options={[
                { value: 'all', label: '全部状态' },
                { value: 'draft', label: '草稿' },
                { value: 'running', label: '进行中' },
                { value: 'completed', label: '已完成' },
                { value: 'failed', label: '失败' },
              ]}
            />
          </div>
          <div className="w-40">
            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              options={[
                { value: 'newest', label: '最新创建' },
                { value: 'oldest', label: '最早创建' },
              ]}
            />
          </div>
        </div>

        {filteredProjects.length === 0 ? (
          <EmptyState onCreateClick={() => setIsModalOpen(true)} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onClick={() => navigate(`/flow/${project.id}`)}
                onDelete={setDeleteProjectId}
              />
            ))}
          </div>
        )}
      </div>
      <CreateProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={handleCreateProject}
      />
      
      {deleteProjectId && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">确认删除？</h3>
            <p className="text-gray-600 mb-6">确定要删除此项目吗？此操作不可恢复。</p>
            <div className="flex justify-end space-x-3">
              <Button variant="ghost" onClick={() => setDeleteProjectId(null)}>
                取消
              </Button>
              <Button onClick={() => handleDeleteProject(deleteProjectId)}>
                删除
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
