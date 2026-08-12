import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const ProcessingPage = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [message, setMessage] = useState('Verifying payment and starting generation...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const startProcessing = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/jobs/${jobId}/process`, {
          method: 'POST',
        });

        if (response.status === 402) {
          const payload = await response.json();
          if (payload.detail?.message) {
            setError(payload.detail.message);
            setMessage('Payment still required.');
            return;
          }
        }

        if (!response.ok) {
          const payload = await response.json();
          throw new Error(payload.detail || 'Processing failed.');
        }

        const data = await response.json();
        if (data.processing_status === 'completed') {
          navigate('/result');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Processing failed.');
      }
    };

    startProcessing();
  }, [jobId, navigate]);

  return (
    <div className="space-y-8 py-10">
      <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8 shadow-xl shadow-slate-900/20">
        <h2 className="text-3xl font-semibold">Processing</h2>
        <p className="mt-2 text-slate-400">Your job is being validated and queued for slide generation.</p>

        <div className="mt-8 rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
          <p className="text-sm text-slate-400">Status</p>
          <p className="mt-2 text-lg font-semibold text-white">{message}</p>
          {error && <p className="mt-4 text-sm text-rose-300">{error}</p>}
        </div>
      </div>
    </div>
  );
};

export default ProcessingPage;
