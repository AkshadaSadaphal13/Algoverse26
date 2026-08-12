import { useState, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';

interface JobCreateResponse {
  job_id: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  audio_duration_seconds: number | null;
  usage_minutes: number | null;
  price_usdc: number | null;
  payment_status: string;
  processing_status: string;
}

function formatFileSize(bytes: number) {
  if (bytes >= 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }

  if (bytes >= 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${bytes} bytes`;
}

const GeneratePage = () => {
  const navigate = useNavigate();

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [processing, setProcessing] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const handleFileChange = (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    setError(null);

    const file =
      event.target.files?.[0] || null;

    setSelectedFile(file);
  };

  const handleGenerate = async () => {
    if (!selectedFile) {
      setError(
        'Please select an audio file first.',
      );
      return;
    }

    const formData = new FormData();

    formData.append(
      'file',
      selectedFile,
    );

    setProcessing(true);
    setError(null);

    try {
      // --------------------------------------------------
      // STEP 1: CREATE JOB
      // --------------------------------------------------

      const response = await fetch(
  'http://127.0.0.1:8000/api/jobs/upload',
  {
    method: 'POST',
    body: formData,
  },
);
      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            'Unable to create job.',
        );
      }

      const job: JobCreateResponse = data;

      if (!job.job_id) {
        throw new Error(
          'Backend did not return a job ID.',
        );
      }

      console.log(
        'Job created:',
        job,
      );

      // --------------------------------------------------
      // STEP 2: GO TO PAYMENT
      // --------------------------------------------------

      navigate(
        `/payment/${job.job_id}`,
      );

    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to create job.',
      );
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-8 py-10">

      <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8 shadow-xl shadow-slate-900/20">

        <h2 className="text-3xl font-semibold text-white">
          Generate Your Slide Deck
        </h2>

        <p className="mt-2 max-w-2xl text-slate-400">
          Upload a meeting or brainstorming
          recording. CodeVerse will analyze
          your audio and generate a
          presentation-ready slide deck.
        </p>

        <div className="mt-8 space-y-4">

          {/* Upload */}
          <label className="flex cursor-pointer flex-col gap-3 rounded-3xl border border-dashed border-slate-700 bg-slate-900/80 p-8 text-center transition hover:border-sky-500">

            <span className="text-sm uppercase tracking-[0.24em] text-slate-500">
              Select audio file
            </span>

            <span className="text-lg font-medium text-slate-100">
              MP3, WAV, or M4A
            </span>

            <input
              type="file"
              accept="audio/*"
              className="hidden"
              onChange={handleFileChange}
            />

          </label>

          {/* Selected file */}
          {selectedFile && (
            <div className="rounded-3xl border border-slate-700 bg-slate-900/80 p-6">

              <p className="text-sm text-slate-400">
                Selected file
              </p>

              <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

                <p className="text-lg font-semibold text-white">
                  {selectedFile.name}
                </p>

                <p className="text-sm text-slate-400">
                  {formatFileSize(
                    selectedFile.size,
                  )}
                </p>

              </div>

            </div>
          )}

          {/* Generate */}
          <button
            type="button"
            onClick={handleGenerate}
            disabled={
              processing ||
              !selectedFile
            }
            className="inline-flex w-full items-center justify-center rounded-3xl bg-sky-500 px-6 py-4 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {processing
              ? 'Preparing your payment...'
              : 'Continue to Payment'}
          </button>

          {/* Processing */}
          {processing && (
            <div className="rounded-2xl border border-slate-700 bg-slate-900/80 p-5 text-center">

              <p className="text-slate-200">
                🎤 Uploading your recording...
              </p>

              <p className="mt-2 text-sm text-slate-500">
                We are calculating the
                usage and payment amount.
              </p>

            </div>
          )}

          {/* Error */}
          {error && (
            <div className="rounded-2xl bg-rose-950/90 px-4 py-3 text-sm text-rose-300">
              {error}
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default GeneratePage;