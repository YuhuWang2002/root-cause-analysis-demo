const API_BASE_URL = 'http://127.0.0.1:5000/api';

export interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface CanvasData {
  project_id: string;
  nodes: any[];
  connections: any[];
}

export interface NodeConfig {
  project_id: string;
  node_id: string;
  config: Record<string, any>;
}

async function fetchAPI<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function getProjects(): Promise<Project[]> {
  return fetchAPI<Project[]>('/projects');
}

export async function createProject(data: { name: string; description: string; status?: string }): Promise<Project> {
  return fetchAPI<Project>('/projects', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getProject(id: string): Promise<Project> {
  return fetchAPI<Project>(`/projects/${id}`);
}

export async function updateProject(id: string, data: Partial<Project>): Promise<Project> {
  return fetchAPI<Project>(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteProject(id: string): Promise<{ message: string }> {
  return fetchAPI<{ message: string }>(`/projects/${id}`, {
    method: 'DELETE',
  });
}

export async function getCanvas(projectId: string): Promise<CanvasData> {
  return fetchAPI<CanvasData>(`/projects/${projectId}/canvas`);
}

export async function saveCanvas(projectId: string, data: { nodes: any[]; connections: any[] }): Promise<CanvasData> {
  return fetchAPI<CanvasData>(`/projects/${projectId}/canvas`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function getNodeConfig(projectId: string, nodeId: string): Promise<NodeConfig> {
  return fetchAPI<NodeConfig>(`/projects/${projectId}/nodes/${nodeId}/config`);
}

export async function saveNodeConfig(projectId: string, nodeId: string, config: Record<string, any>): Promise<NodeConfig> {
  return fetchAPI<NodeConfig>(`/projects/${projectId}/nodes/${nodeId}/config`, {
    method: 'PUT',
    body: JSON.stringify({ config }),
  });
}

export async function getAllNodeConfigs(projectId: string): Promise<NodeConfig[]> {
  return fetchAPI<NodeConfig[]>(`/projects/${projectId}/nodes/configs`);
}

export async function saveAllNodeConfigs(projectId: string, configs: { node_id: string; config: Record<string, any> }[]): Promise<{ message: string }> {
  return fetchAPI<{ message: string }>(`/projects/${projectId}/nodes/configs`, {
    method: 'PUT',
    body: JSON.stringify({ configs }),
  });
}

export interface OntologyClass {
  id: number;
  ontology_id: number;
  name: string;
  description: string;
  properties: Array<{
    id: number;
    name: string;
    type: string;
    description: string;
  }>;
}

export interface OntologyRelation {
  id: number;
  ontology_id: number;
  source_class_id: number;
  target_class_id: number;
  relation_type: string;
  description: string;
  source_class_name?: string;
  target_class_name?: string;
}

export interface Ontology {
  id: number;
  project_id: string;
  name: string;
  description: string;
  canvas_data: any[];
  classes: OntologyClass[];
  relations: OntologyRelation[];
}

export async function getOntologies(projectId: string): Promise<Ontology[]> {
  return fetchAPI<Ontology[]>(`/projects/${projectId}/ontologies`);
}

export async function getOntology(projectId: string, ontologyId: number): Promise<Ontology> {
  return fetchAPI<Ontology>(`/projects/${projectId}/ontologies/${ontologyId}`);
}

export async function createOntology(projectId: string, data: { name: string; description: string }): Promise<Ontology> {
  return fetchAPI<Ontology>(`/projects/${projectId}/ontologies`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateOntology(projectId: string, ontologyId: number, data: Partial<Ontology>): Promise<Ontology> {
  return fetchAPI<Ontology>(`/projects/${projectId}/ontologies/${ontologyId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteOntology(projectId: string, ontologyId: number): Promise<{ message: string }> {
  return fetchAPI<{ message: string }>(`/projects/${projectId}/ontologies/${ontologyId}`, {
    method: 'DELETE',
  });
}

export async function saveOntologyCanvas(projectId: string, ontologyId: number, canvasData: any[]): Promise<Ontology> {
  return fetchAPI<Ontology>(`/projects/${projectId}/ontologies/${ontologyId}/canvas`, {
    method: 'PUT',
    body: JSON.stringify({ canvas_data: canvasData }),
  });
}

export async function getOntologyClasses(projectId: string, ontologyId: number): Promise<OntologyClass[]> {
  return fetchAPI<OntologyClass[]>(`/projects/${projectId}/ontologies/${ontologyId}/classes`);
}

export async function createOntologyClass(projectId: string, ontologyId: number, data: { name: string; description: string }): Promise<OntologyClass> {
  return fetchAPI<OntologyClass>(`/projects/${projectId}/ontologies/${ontologyId}/classes`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateOntologyClass(projectId: string, ontologyId: number, classId: number, data: Partial<OntologyClass>): Promise<OntologyClass> {
  return fetchAPI<OntologyClass>(`/projects/${projectId}/ontologies/${ontologyId}/classes/${classId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteOntologyClass(projectId: string, ontologyId: number, classId: number): Promise<{ message: string }> {
  return fetchAPI<{ message: string }>(`/projects/${projectId}/ontologies/${ontologyId}/classes/${classId}`, {
    method: 'DELETE',
  });
}

export async function addClassProperty(projectId: string, ontologyId: number, classId: number, data: { name: string; type: string; description: string }): Promise<any[]> {
  return fetchAPI<any[]>(`/projects/${projectId}/ontologies/${ontologyId}/classes/${classId}/properties`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateClassProperty(projectId: string, ontologyId: number, classId: number, propId: number, data: { name?: string; type?: string; description?: string }): Promise<any[]> {
  return fetchAPI<any[]>(`/projects/${projectId}/ontologies/${ontologyId}/classes/${classId}/properties/${propId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteClassProperty(projectId: string, ontologyId: number, classId: number, propId: number): Promise<any[]> {
  return fetchAPI<any[]>(`/projects/${projectId}/ontologies/${ontologyId}/classes/${classId}/properties/${propId}`, {
    method: 'DELETE',
  });
}

export async function getOntologyRelations(projectId: string, ontologyId: number): Promise<OntologyRelation[]> {
  return fetchAPI<OntologyRelation[]>(`/projects/${projectId}/ontologies/${ontologyId}/relations`);
}

export async function createOntologyRelation(projectId: string, ontologyId: number, data: { source_class_id: number; target_class_id: number; relation_type: string; description?: string }): Promise<OntologyRelation> {
  return fetchAPI<OntologyRelation>(`/projects/${projectId}/ontologies/${ontologyId}/relations`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteOntologyRelation(projectId: string, ontologyId: number, relationId: number): Promise<{ message: string }> {
  return fetchAPI<{ message: string }>(`/projects/${projectId}/ontologies/${ontologyId}/relations/${relationId}`, {
    method: 'DELETE',
  });
}
