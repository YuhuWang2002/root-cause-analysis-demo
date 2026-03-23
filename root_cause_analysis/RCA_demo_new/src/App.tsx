import { Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from '@/components/layout/Navbar';
import ProjectList from './pages/ProjectList';
import CreateProject from './pages/CreateProject';
import AnalysisFlow from './pages/AnalysisFlow';
import OntologyEditor from './pages/OntologyEditor';
import OntologyObjectEditor from './pages/OntologyObjectEditor';
import OntologyLinkEditor from './pages/OntologyLinkEditor';
import OntologyActionEditor from './pages/OntologyActionEditor';
import OntologyExplorer from './pages/OntologyExplorer';
import DataAnalysisDashboard from './pages/DataAnalysisDashboard';
import RootCauseAnalysis from './pages/RootCauseAnalysis';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="pt-16">
        <Routes>
          <Route path="/" element={<ProjectList />} />
          <Route path="/create" element={<CreateProject />} />
          <Route path="/flow/:id" element={<AnalysisFlow />} />
          <Route path="/ontology/:projectId/:ontologyId?" element={<OntologyEditor />} />
          <Route path="/ontology/:projectId/:ontologyId/object/:objectId" element={<OntologyObjectEditor />} />
          <Route path="/ontology/:projectId/:ontologyId/link/:linkId" element={<OntologyLinkEditor />} />
          <Route path="/ontology/:projectId/:ontologyId/action/:actionId" element={<OntologyActionEditor />} />
          <Route path="/ontology/:projectId/:ontologyId/explorer" element={<OntologyExplorer />} />
          <Route path="/dashboard/:projectId" element={<DataAnalysisDashboard />} />
          <Route path="/dashboard/:projectId/:dashboardId" element={<DataAnalysisDashboard />} />
          <Route path="/root-cause/:projectId" element={<RootCauseAnalysis />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
