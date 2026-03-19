import { Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from '@/components/layout/Navbar';
import { ProjectList } from '@/pages/ProjectList';
import { CreateProject } from '@/pages/CreateProject';
import { AnalysisFlow } from '@/pages/AnalysisFlow';
import OntologyEditor from './pages/OntologyEditor';

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
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
