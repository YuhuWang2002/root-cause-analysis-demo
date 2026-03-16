export interface Project {
  id: string;
  name: string;
  description: string;
  scenario: string;
  status: 'draft' | 'running' | 'completed' | 'failed';
  progress: number;
  createdAt: string;
  updatedAt: string;
}

export interface DataSource {
  id: string;
  type: 'mysql' | 'postgresql' | 'mongodb' | 'api' | 'csv';
  name: string;
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  connectionString?: string;
}

export interface DataPermission {
  tables: TablePermission[];
  timeRange?: {
    start: string;
    end: string;
  };
  rowLimit?: number;
}

export interface TablePermission {
  tableName: string;
  fields: string[];
}

export interface DataTransform {
  outputFormat: 'json' | 'parquet' | 'delta';
  storageLocation: string;
  rules: TransformRule[];
  schedule: 'immediate' | 'scheduled' | 'manual';
  cronExpression?: string;
}

export interface TransformRule {
  id: string;
  type: 'mapping' | 'type_convert' | 'computed';
  sourceField: string;
  targetField: string;
  expression?: string;
}

export interface QualityConstraint {
  id: string;
  type: 'not_null' | 'unique' | 'range' | 'format' | 'custom';
  table: string;
  field: string;
  condition: string;
  alertLevel: 'info' | 'warning' | 'error';
  enabled: boolean;
}

export interface Ontology {
  id: string;
  type: 'event' | 'causal' | 'hierarchy';
  entities: OntologyEntity[];
  relations: OntologyRelation[];
}

export interface OntologyEntity {
  id: string;
  name: string;
  type: string;
  properties: Record<string, string>;
}

export interface OntologyRelation {
  id: string;
  sourceId: string;
  targetId: string;
  relationType: 'causes' | 'contains' | 'depends_on' | 'precedes';
}

export interface AnalysisConfig {
  methods: ('causal_analysis' | 'root_cause' | 'correlation')[];
  algorithm: 'pc' | 'fci' | 'grasp';
  parameters: {
    confidenceThreshold: number;
    maxPathLength: number;
  };
  outputFormat: 'json' | 'csv' | 'report';
}

export interface FlowNode {
  id: string;
  type: 'data' | 'process' | 'ontology' | 'analysis' | 'result';
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: string;
  endTime?: string;
  input?: string;
  output?: string;
  logs?: string;
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
}
