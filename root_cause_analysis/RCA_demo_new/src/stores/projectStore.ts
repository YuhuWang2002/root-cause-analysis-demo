import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Project } from '@/types';

interface ProjectState {
  projects: Project[];
  searchQuery: string;
  statusFilter: 'all' | 'draft' | 'running' | 'completed' | 'failed';
  sortBy: 'newest' | 'oldest';
  addProject: (project: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>) => string;
  createEmptyProject: () => string;
  updateProject: (id: string, updates: Partial<Project>) => void;
  deleteProject: (id: string) => void;
  setSearchQuery: (query: string) => void;
  setStatusFilter: (status: ProjectState['statusFilter']) => void;
  setSortBy: (sort: ProjectState['sortBy']) => void;
  getFilteredProjects: () => Project[];
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      projects: [
        {
          id: '1',
          name: '系统异常根因分析',
          description: '分析线上系统频繁异常的根因，识别关键故障因素',
          scenario: 'system_anomaly',
          status: 'running',
          progress: 65,
          createdAt: '2024-01-15T10:00:00Z',
          updatedAt: '2024-01-16T14:30:00Z',
        },
        {
          id: '2',
          name: '性能瓶颈分析',
          description: '识别数据库查询性能瓶颈，优化系统响应时间',
          scenario: 'performance',
          status: 'completed',
          progress: 100,
          createdAt: '2024-01-10T09:00:00Z',
          updatedAt: '2024-01-12T16:00:00Z',
        },
        {
          id: '3',
          name: '用户流失原因分析',
          description: '分析用户流失的关键因素，制定留存策略',
          scenario: 'quality',
          status: 'draft',
          progress: 0,
          createdAt: '2024-01-18T11:00:00Z',
          updatedAt: '2024-01-18T11:00:00Z',
        },
      ],
      searchQuery: '',
      statusFilter: 'all',
      sortBy: 'newest',

      addProject: (project) => {
        const newProject: Project = {
          ...project,
          id: Date.now().toString(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        set((state) => ({ projects: [...state.projects, newProject] }));
        return newProject.id;
      },

      createEmptyProject: () => {
        const newProject: Project = {
          id: `proj-${Date.now()}`,
          name: '新分析项目',
          description: '',
          scenario: 'custom',
          status: 'draft',
          progress: 0,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        set((state) => ({ projects: [...state.projects, newProject] }));
        return newProject.id;
      },

      updateProject: (id, updates) => {
        set((state) => ({
          projects: state.projects.map((p) =>
            p.id === id ? { ...p, ...updates, updatedAt: new Date().toISOString() } : p
          ),
        }));
      },

      deleteProject: (id) => {
        set((state) => ({
          projects: state.projects.filter((p) => p.id !== id),
        }));
      },

      setSearchQuery: (query) => set({ searchQuery: query }),
      setStatusFilter: (status) => set({ statusFilter: status }),
      setSortBy: (sort) => set({ sortBy: sort }),

      getFilteredProjects: () => {
        const { projects, searchQuery, statusFilter, sortBy } = get();
        let filtered = [...projects];

        if (searchQuery) {
          filtered = filtered.filter(
            (p) =>
              p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
              p.description.toLowerCase().includes(searchQuery.toLowerCase())
          );
        }

        if (statusFilter !== 'all') {
          filtered = filtered.filter((p) => p.status === statusFilter);
        }

        filtered.sort((a, b) => {
          const dateA = new Date(a.createdAt).getTime();
          const dateB = new Date(b.createdAt).getTime();
          return sortBy === 'newest' ? dateB - dateA : dateA - dateB;
        });

        return filtered;
      },
    }),
    {
      name: 'rca-projects',
    }
  )
);
