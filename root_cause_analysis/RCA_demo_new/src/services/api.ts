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

export interface OntologyAction {
  id: number;
  ontology_id: number;
  name: string;
  api_name: string;
  description: string;
  event_type: string;
  source_object: string;
  trigger_condition: string;
  logic_type: string;
  target_system: string;
  parameter_mappings: Array<{ sourceField: string; targetField: string }>;
  variables: Array<{ name: string; type: string; defaultValue: string }>;
}

export interface Ontology {
  id: number;
  project_id: string;
  name: string;
  description: string;
  canvas_data: any[];
  classes: OntologyClass[];
  relations: OntologyRelation[];
  actions: OntologyAction[];
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

export async function saveOntologyCanvas(projectId: string, ontologyId: number, canvasData: any): Promise<Ontology> {
  return fetchAPI<Ontology>(`/projects/${projectId}/ontologies/${ontologyId}/canvas`, {
    method: 'PUT',
    body: JSON.stringify({ canvas_data: [canvasData] }),
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

export async function getOntologyActions(projectId: string, ontologyId: number): Promise<OntologyAction[]> {
  return fetchAPI<OntologyAction[]>(`/projects/${projectId}/ontologies/${ontologyId}/actions`);
}

export async function createOntologyAction(projectId: string, ontologyId: number, data: Partial<OntologyAction>): Promise<OntologyAction> {
  return fetchAPI<OntologyAction>(`/projects/${projectId}/ontologies/${ontologyId}/actions`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getOntologyAction(projectId: string, ontologyId: number, actionId: number): Promise<OntologyAction> {
  return fetchAPI<OntologyAction>(`/projects/${projectId}/ontologies/${ontologyId}/actions/${actionId}`);
}

export async function updateOntologyAction(projectId: string, ontologyId: number, actionId: number, data: Partial<OntologyAction>): Promise<OntologyAction> {
  return fetchAPI<OntologyAction>(`/projects/${projectId}/ontologies/${ontologyId}/actions/${actionId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteOntologyAction(projectId: string, ontologyId: number, actionId: number): Promise<{ message: string }> {
  return fetchAPI<{ message: string }>(`/projects/${projectId}/ontologies/${ontologyId}/actions/${actionId}`, {
    method: 'DELETE',
  });
}

// ============ Data Analysis Dashboard APIs ============

export interface CSVAnalysisResult {
  file_path: string;
  total_rows: number;
  fields: Array<{ name: string; type: string; sample: any; null_count: number }>;
}

export interface DataQuery {
  fields?: string[];
  filters?: Array<{ field: string; operator: string; value: any }>;
  groupBy?: { field: string; granularity: string };
  aggregations?: Array<{ field: string; function: string; alias: string }>;
}

export interface DataSource {
  type: string;
  file_path: string;
}

export interface DataQueryResult {
  fields: Array<{ name: string; type: string }>;
  data: any[];
}

export interface Dashboard {
  id: number;
  project_id: string;
  name: string;
  description: string;
  layout: any;
  components: any[];
  created_at: string;
  updated_at: string;
}

export async function analyzeCSV(filePath: string): Promise<CSVAnalysisResult> {
  return fetchAPI<CSVAnalysisResult>('/data/csv/analyze', {
    method: 'POST',
    body: JSON.stringify({ file_path: filePath }),
  });
}

export async function queryData(dataSource: DataSource, query: DataQuery): Promise<DataQueryResult> {
  return fetchAPI<DataQueryResult>('/data/query', {
    method: 'POST',
    body: JSON.stringify({ dataSource, query }),
  });
}

export async function getDashboards(projectId: string): Promise<Dashboard[]> {
  return fetchAPI<Dashboard[]>(`/projects/${projectId}/dashboards`);
}

export async function getDashboard(projectId: string, dashboardId: number): Promise<Dashboard> {
  return fetchAPI<Dashboard>(`/projects/${projectId}/dashboards/${dashboardId}`);
}

export async function createDashboard(projectId: string, data: { name: string; description?: string; layout?: any; components?: any[] }): Promise<Dashboard> {
  return fetchAPI<Dashboard>(`/projects/${projectId}/dashboards`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateDashboard(projectId: string, dashboardId: number, data: Partial<{ name: string; description: string; layout: any; components: any[] }>): Promise<Dashboard> {
  return fetchAPI<Dashboard>(`/projects/${projectId}/dashboards/${dashboardId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteDashboard(projectId: string, dashboardId: number): Promise<{ message: string }> {
  return fetchAPI<{ message: string }>(`/projects/${projectId}/dashboards/${dashboardId}`, {
    method: 'DELETE',
  });
}

export interface RootCauseResults {
  counterfactual_analysis: {
    inventory_reduction: number;
    reduction_percentage: number;
    actual_inventory_mean: number;
    counterfactual_inventory_mean: number;
    decline_period_actual_inventory: number;
    decline_period_counterfactual_inventory: number;
    decline_period_reduction: number;
  } | null;
  causal_graph?: string;
  message?: string;
}

export async function getCausalGraph(projectId: string, nodeId: string): Promise<{ causal_graph: string }> {
  return fetchAPI<{ causal_graph: string }>(`/root-cause/${projectId}/causal_graph/${nodeId}`);
}

export async function saveCausalGraph(projectId: string, nodeId: string, causalGraph: string): Promise<{ causal_graph: string }> {
  return fetchAPI<{ causal_graph: string }>(`/root-cause/${projectId}/causal_graph/${nodeId}`, {
    method: 'PUT',
    body: JSON.stringify({ causal_graph: causalGraph }),
  });
}

export async function runRootCauseAnalysis(projectId: string, causalGraph: string, fastMode: boolean = true): Promise<RootCauseResults> {
  return fetchAPI<RootCauseResults>(`/root-cause/${projectId}/analysis`, {
    method: 'POST',
    body: JSON.stringify({ causal_graph: causalGraph, fast_mode: fastMode }),
  });
}

export async function getRootCauseResults(projectId: string): Promise<RootCauseResults> {
  return fetchAPI<RootCauseResults>(`/root-cause/${projectId}/results`);
}

export async function buildCausalGraph(dataSummary: string): Promise<{ causal_graph: string }> {
  return fetchAPI<{ causal_graph: string }>('/root-cause/build-graph', {
    method: 'POST',
    body: JSON.stringify({ data_summary: dataSummary }),
  });
}

export interface LLMConfig {
  api_key: string;
  model?: string;
  base_url?: string;
}

export interface LLMTestResult {
  success: boolean;
  message: string;
}

export interface LLMExplanationResult {
  explanation: string;
  message: string;
}

export interface LLMSolutionResult {
  solution: string;
  message: string;
}

export async function configureLLM(config: LLMConfig): Promise<{ message: string; model: string; base_url: string }> {
  return fetchAPI<{ message: string; model: string; base_url: string }>('/root-cause/llm/config', {
    method: 'POST',
    body: JSON.stringify(config),
  });
}

export async function testLLMConnection(config: LLMConfig): Promise<LLMTestResult> {
  return fetchAPI<LLMTestResult>('/root-cause/llm/test', {
    method: 'POST',
    body: JSON.stringify(config),
  });
}

export async function generateRootCauseExplanation(
  projectId: string,
  analysisResults: any,
  causalGraph?: string
): Promise<LLMExplanationResult> {
  return fetchAPI<LLMExplanationResult>(`/root-cause/${projectId}/explain`, {
    method: 'POST',
    body: JSON.stringify({ analysis_results: analysisResults, causal_graph: causalGraph }),
  });
}

export async function generateSolution(
  projectId: string,
  analysisResults: any,
  causalGraph?: string,
  rootCauseText?: string,
  knowledgeBase?: string
): Promise<LLMSolutionResult> {
  return fetchAPI<LLMSolutionResult>(`/root-cause/${projectId}/solution`, {
    method: 'POST',
    body: JSON.stringify({
      analysis_results: analysisResults,
      causal_graph: causalGraph,
      root_cause_text: rootCauseText,
      knowledge_base: knowledgeBase,
    }),
  });
}
