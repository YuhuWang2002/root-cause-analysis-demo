import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Project } from '@/types';
import * as api from '@/services/api';

interface ProjectState {
  projects: Project[];
  searchQuery: string;
  statusFilter: 'all' | 'draft' | 'running' | 'completed' | 'failed';
  sortBy: 'newest' | 'oldest';
  isLoading: boolean;
  addProject: (project: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>) => Promise<string>;
  createEmptyProject: () => Promise<string>;
  updateProject: (id: string, updates: Partial<Project>) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  setSearchQuery: (query: string) => void;
  setStatusFilter: (status: ProjectState['statusFilter']) => void;
  setSortBy: (sort: ProjectState['sortBy']) => void;
  getFilteredProjects: () => Project[];
  fetchProjects: () => Promise<void>;
}

const mapApiProjectToProject = (apiProject: api.Project): Project => ({
  id: apiProject.id,
  name: apiProject.name,
  description: apiProject.description,
  scenario: 'custom',
  status: apiProject.status as Project['status'],
  progress: apiProject.progress,
  createdAt: apiProject.created_at,
  updatedAt: apiProject.updated_at,
});

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      projects: [],
      searchQuery: '',
      statusFilter: 'all',
      sortBy: 'newest',
      isLoading: false,

      fetchProjects: async () => {
        set({ isLoading: true });
        try {
          const apiProjects = await api.getProjects();
          const projects = apiProjects.map(mapApiProjectToProject);
          set({ projects, isLoading: false });
        } catch (error) {
          console.error('Failed to fetch projects:', error);
          set({ isLoading: false });
        }
      },

      addProject: async (project) => {
        try {
          const apiProject = await api.createProject({
            name: project.name,
            description: project.description,
            status: project.status || 'draft',
          });
          const newProject = mapApiProjectToProject(apiProject);
          set((state) => ({ projects: [...state.projects, newProject] }));
          return newProject.id;
        } catch (error) {
          console.error('Failed to create project:', error);
          const newId = `local-${Date.now()}`;
          const newProject: Project = {
            ...project,
            id: newId,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };
          set((state) => ({ projects: [...state.projects, newProject] }));
          return newId;
        }
      },

      createEmptyProject: async () => {
        try {
          const apiProject = await api.createProject({
            name: '新分析项目',
            description: '',
            status: 'draft',
          });
          const newProject = mapApiProjectToProject(apiProject);
          set((state) => ({ projects: [...state.projects, newProject] }));
          return newProject.id;
        } catch (error) {
          console.error('Failed to create project:', error);
          const newId = `local-${Date.now()}`;
          const newProject: Project = {
            name: '新分析项目',
            description: '',
            scenario: 'custom',
            status: 'draft',
            progress: 0,
            id: newId,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };
          set((state) => ({ projects: [...state.projects, newProject] }));
          return newId;
        }
      },

      updateProject: async (id, updates) => {
        try {
          await api.updateProject(id, {
            name: updates.name,
            description: updates.description,
            status: updates.status,
            progress: updates.progress,
          });
        } catch (error) {
          console.error('Failed to update project:', error);
        }
        set((state) => ({
          projects: state.projects.map((p) =>
            p.id === id ? { ...p, ...updates, updatedAt: new Date().toISOString() } : p
          ),
        }));
      },

      deleteProject: async (id) => {
        try {
          await api.deleteProject(id);
        } catch (error) {
          console.error('Failed to delete project:', error);
        }
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
      name: 'project-storage',
      partialize: (state) => ({ projects: state.projects }),
    }
  )
);
