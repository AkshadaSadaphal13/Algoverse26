import { Routes, Route, Navigate } from 'react-router-dom';
import GeneratePage from './pages/GeneratePage';
import PaymentPage from './pages/PaymentPage';
import ProcessingPage from './pages/ProcessingPage';
import ResultPage from './pages/ResultPage';

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-6xl px-4 py-10">
        <header className="mb-10">
          <h1 className="text-4xl font-semibold">CodeVerse</h1>
          <p className="mt-2 max-w-2xl text-slate-400">
            Voice to Slide Deck Node — AI-powered pay-per-use presentation generator.
          </p>
        </header>

        <main>
          <Routes>
            <Route path="/" element={<div>Landing page placeholder</div>} />
            <Route path="/generate" element={<GeneratePage />} />
            <Route path="/payment/:jobId" element={<PaymentPage />} />
            <Route path="/processing/:jobId" element={<ProcessingPage />} />
            <Route path="/result" element={<ResultPage />} />
            <Route path="/history" element={<div>History page placeholder</div>} />
            <Route path="/dashboard" element={<div>Dashboard page placeholder</div>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
