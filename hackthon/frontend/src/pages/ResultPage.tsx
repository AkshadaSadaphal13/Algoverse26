import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface ActionItem {
  task: string;
  owner: string | null;
  deadline: string | null;
}

interface Slide {
  slide_number: number;
  layout: string;
  title: string;
  bullets: string[];
}

interface PipelineResult {
  success: boolean;
  filename: string;
  pptx_filename: string;
  transcript: string;
  ai_result: {
    title: string;
    summary: string;
    key_topics: string[];
    strategic_insights: string[];
    decisions: string[];
    action_items: ActionItem[];
    important_points: string[];
    slides: Slide[];
  };
}

const ResultPage = () => {
  const navigate = useNavigate();

  const [result, setResult] = useState<PipelineResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const storedResult = sessionStorage.getItem('pipelineResult');

      if (!storedResult) {
        setError('No generated presentation was found.');
        return;
      }

      const parsedResult: PipelineResult = JSON.parse(storedResult);

      setResult(parsedResult);
    } catch (err) {
      console.error(err);
      setError('Unable to load the generated presentation.');
    }
  }, []);

  if (error) {
    return (
      <div className="py-10">
        <div className="rounded-3xl border border-rose-900 bg-rose-950/60 p-8">
          <h2 className="text-2xl font-semibold text-rose-200">
            Something went wrong
          </h2>

          <p className="mt-3 text-rose-300">
            {error}
          </p>

          <button
            type="button"
            onClick={() => navigate('/generate')}
            className="mt-6 rounded-3xl bg-sky-500 px-6 py-3 font-semibold text-slate-950 hover:bg-sky-400"
          >
            Generate a New Deck
          </button>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="py-10">
        <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8">
          <p className="text-slate-300">
            Loading generated presentation...
          </p>
        </div>
      </div>
    );
  }

  const { ai_result } = result;

const downloadPowerPoint = () => {
  if (!result.pptx_filename) {
    setError('PowerPoint file is not available.');
    return;
  }

  const downloadUrl =
    `http://127.0.0.1:8000/api/pipeline/download/${encodeURIComponent(
      result.pptx_filename
    )}`;

  window.open(downloadUrl, '_blank');
};

return (
    <div className="space-y-8 py-10">

      {/* Header */}
      <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8 shadow-xl shadow-slate-900/20">

        <p className="text-sm uppercase tracking-[0.24em] text-sky-400">
          AI Generated Presentation
        </p>

        <h1 className="mt-3 text-4xl font-bold text-white">
          {ai_result.title}
        </h1>

        <p className="mt-4 max-w-3xl text-slate-400">
          {ai_result.summary}
        </p>

        <div className="mt-5 flex flex-wrap gap-3">
          <span className="rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-300">
            🎤 {result.filename}
          </span>

          <span className="rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-300">
            🧠 Qwen2.5-7B-Instruct
          </span>

          <span className="rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-300">
            📊 {ai_result.slides.length} Slides
          </span>
        </div>

      </div>

      {/* Transcript */}
      <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8">

        <h2 className="text-2xl font-semibold text-white">
          Transcript
        </h2>

        <p className="mt-4 whitespace-pre-line leading-7 text-slate-400">
          {result.transcript}
        </p>

      </div>

      {/* Key Topics */}
      {ai_result.key_topics.length > 0 && (
        <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8">

          <h2 className="text-2xl font-semibold text-white">
            Key Topics
          </h2>

          <div className="mt-5 flex flex-wrap gap-3">
            {ai_result.key_topics.map((topic, index) => (
              <span
                key={index}
                className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-300"
              >
                {topic}
              </span>
            ))}
          </div>

        </div>
      )}

      {/* Insights */}
      {ai_result.strategic_insights.length > 0 && (
        <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8">

          <h2 className="text-2xl font-semibold text-white">
            Strategic Insights
          </h2>

          <ul className="mt-5 space-y-3">
            {ai_result.strategic_insights.map((insight, index) => (
              <li
                key={index}
                className="rounded-2xl bg-slate-900 p-4 text-slate-300"
              >
                {insight}
              </li>
            ))}
          </ul>

        </div>
      )}

      {/* Decisions + Action Items */}
      <div className="grid gap-6 lg:grid-cols-2">

        {/* Decisions */}
        {ai_result.decisions.length > 0 && (
          <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8">

            <h2 className="text-2xl font-semibold text-white">
              Decisions
            </h2>

            <ul className="mt-5 space-y-3">
              {ai_result.decisions.map((decision, index) => (
                <li
                  key={index}
                  className="rounded-2xl bg-slate-900 p-4 text-slate-300"
                >
                  {decision}
                </li>
              ))}
            </ul>

          </div>
        )}

        {/* Action Items */}
        {ai_result.action_items.length > 0 && (
          <div className="rounded-3xl border border-slate-700 bg-slate-950/90 p-8">

            <h2 className="text-2xl font-semibold text-white">
              Action Items
            </h2>

            <div className="mt-5 space-y-4">

              {ai_result.action_items.map((item, index) => (
                <div
                  key={index}
                  className="rounded-2xl bg-slate-900 p-4"
                >

                  <p className="font-medium text-white">
                    {item.task}
                  </p>

                  <div className="mt-2 flex flex-wrap gap-3 text-sm text-slate-400">

                    {item.owner && (
                      <span>
                        Owner: {item.owner}
                      </span>
                    )}

                    {item.deadline && (
                      <span>
                        Deadline: {item.deadline}
                      </span>
                    )}

                  </div>

                </div>
              ))}

            </div>

          </div>
        )}

      </div>

      {/* Slides */}
      <div className="space-y-6">

        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-sky-400">
            Generated Deck
          </p>

          <h2 className="mt-2 text-3xl font-bold text-white">
            Presentation Slides
          </h2>
        </div>

        {ai_result.slides.map((slide) => (
          <div
            key={slide.slide_number}
            className="overflow-hidden rounded-3xl border border-slate-700 bg-slate-950 shadow-xl"
          >

            {/* Slide header */}
            <div className="border-b border-slate-800 bg-slate-900 px-8 py-5">

              <div className="flex items-center justify-between gap-4">

                <span className="text-sm font-medium uppercase tracking-wider text-sky-400">
                  Slide {slide.slide_number}
                </span>

                <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">
                  {slide.layout}
                </span>

              </div>

            </div>

            {/* Slide content */}
            <div className="min-h-[260px] p-10">

              <h3 className="text-3xl font-bold text-white">
                {slide.title}
              </h3>

              {slide.bullets.length > 0 && (
                <ul className="mt-8 space-y-4">

                  {slide.bullets.map((bullet, index) => (
                    <li
                      key={index}
                      className="flex gap-3 text-lg leading-7 text-slate-300"
                    >
                      <span className="mt-3 h-2 w-2 shrink-0 rounded-full bg-sky-400" />

                      <span>{bullet}</span>
                    </li>
                  ))}

                </ul>
              )}

            </div>

          </div>
        ))}

      </div>

      {/* Bottom actions */}
<div className="flex flex-wrap gap-4">

  <button
    type="button"
    onClick={downloadPowerPoint}
    disabled={!result.pptx_filename}
    className="rounded-3xl bg-emerald-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
  >
    📥 Download PowerPoint
  </button>

  <button
    type="button"
    onClick={() => navigate('/generate')}
    className="rounded-3xl bg-sky-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-sky-400"
  >
    Create Another Deck
  </button>

  <button
    type="button"
    onClick={() => {
      sessionStorage.removeItem('pipelineResult');
      navigate('/generate');
    }}
    className="rounded-3xl border border-slate-700 px-6 py-3 font-semibold text-slate-300 transition hover:bg-slate-900"
  >
    Clear Result
  </button>

</div>

    </div>
  );
};

export default ResultPage;