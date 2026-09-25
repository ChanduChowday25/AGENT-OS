import { useRef, useState } from "react";
import { Check, FileSpreadsheet, LoaderCircle, Upload, X } from "lucide-react";

import { analyzeFile } from "../services/analyticsService.js";
import { uploadFile } from "../services/uploadService.js";

const supportedFileTypes = ".csv,.xlsx,.xls";

function getErrorMessage(error, fallback) {
  const detail = error?.response?.data?.detail;
  return typeof detail === "string" ? detail : fallback;
}

export default function Analytics() {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [fileId, setFileId] = useState(null);
  const [instructions, setInstructions] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleFileSelection(event) {
    const selectedFile = event.target.files?.[0];
    event.target.value = "";

    if (!selectedFile) {
      return;
    }

    setFile(selectedFile);
    setFileId(null);
    setResult(null);
    setError(null);
    setUploading(true);

    try {
      const response = await uploadFile(selectedFile);
      setFileId(response.file_id);
      setFile((currentFile) => ({
        ...currentFile,
        name: response.filename || currentFile.name,
      }));
    } catch (uploadError) {
      setFile(null);
      setError(getErrorMessage(uploadError, "The dataset could not be uploaded."));
    } finally {
      setUploading(false);
    }
  }

  function removeFile() {
    setFile(null);
    setFileId(null);
    setResult(null);
    setError(null);
  }

  async function handleAnalyze(event) {
    event.preventDefault();

    if (!fileId || !instructions.trim() || uploading || analyzing) {
      return;
    }

    setError(null);
    setResult(null);
    setAnalyzing(true);

    try {
      const response = await analyzeFile({
        file_id: fileId,
        instructions: instructions.trim(),
      });
      setResult(response);
    } catch (analysisError) {
      setError(getErrorMessage(analysisError, "The dataset could not be analyzed."));
    } finally {
      setAnalyzing(false);
    }
  }

  const analysis = result?.result;
  const datasetInfo = analysis?.dataset_info;
  const hasDatasetOverview = datasetInfo && (
    datasetInfo.rows !== undefined ||
    datasetInfo.columns !== undefined ||
    Array.isArray(datasetInfo.numeric_columns)
  );

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <header className="border-b border-white/[0.08] pb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center border border-cyan-200/15 bg-cyan-200/[0.06] text-cyan-100/80">
            <FileSpreadsheet size={19} strokeWidth={1.6} />
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200/55">AgentOS</p>
            <h1 className="mt-1 text-xl font-medium tracking-tight text-white/90">Analytics</h1>
          </div>
        </div>
        <p className="mt-4 max-w-2xl text-sm leading-6 text-white/45">
          Upload a dataset and direct the Analytics Agent with a focused question.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <section className="border border-white/[0.08] bg-[#0b121d]/75 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.14)] sm:p-7">
          <div className="mb-6">
            <h2 className="text-sm font-medium tracking-wide text-white/90">Dataset</h2>
            <p className="mt-2 text-xs leading-5 text-white/40">CSV and spreadsheet files are supported.</p>
          </div>

          {!file ? (
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex min-h-44 w-full flex-col items-center justify-center border border-dashed border-cyan-200/20 bg-cyan-200/[0.025] px-5 text-center transition-colors hover:border-cyan-200/40 hover:bg-cyan-200/[0.05]"
            >
              <Upload size={21} className="text-cyan-100/70" strokeWidth={1.5} />
              <span className="mt-3 text-sm text-white/75">Choose a dataset</span>
              <span className="mt-1 text-xs text-white/35">.csv, .xlsx, or .xls</span>
            </button>
          ) : (
            <div className="border border-white/[0.1] bg-[#080e17]/70 p-4">
              <div className="flex items-start gap-3">
                <FileSpreadsheet size={18} className="mt-0.5 shrink-0 text-teal-200/75" strokeWidth={1.6} />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm text-white/80">{file.name}</p>
                  <div className="mt-2 flex items-center gap-2 text-xs">
                    {uploading ? (
                      <>
                        <LoaderCircle size={13} className="animate-spin text-cyan-200/70" strokeWidth={1.7} />
                        <span className="text-white/45">Uploading dataset...</span>
                      </>
                    ) : fileId ? (
                      <>
                        <Check size={13} className="text-teal-200/80" strokeWidth={1.8} />
                        <span className="text-teal-100/65">Ready for analysis</span>
                      </>
                    ) : null}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={removeFile}
                  aria-label="Remove dataset"
                  className="shrink-0 text-white/35 transition-colors hover:text-white/80"
                >
                  <X size={16} strokeWidth={1.7} />
                </button>
              </div>
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept={supportedFileTypes}
            onChange={handleFileSelection}
            className="hidden"
          />

          <form onSubmit={handleAnalyze} className="mt-6">
            <label htmlFor="analysis-instructions" className="text-sm font-medium text-white/80">
              Analysis instructions
            </label>
            <textarea
              id="analysis-instructions"
              value={instructions}
              onChange={(event) => setInstructions(event.target.value)}
              placeholder="Describe what you want to analyze..."
              rows={6}
              className="mt-3 w-full resize-y border border-white/[0.1] bg-[#080e17]/80 px-3 py-3 text-sm leading-6 text-white/75 outline-none transition-colors placeholder:text-white/25 focus:border-cyan-200/35"
            />
            <p className="mt-3 text-xs leading-5 text-white/35">
              Examples: Find the top-performing products, show monthly revenue trends, identify unusual values.
            </p>
            <button
              type="submit"
              disabled={!fileId || uploading || analyzing || !instructions.trim()}
              className="mt-6 flex h-11 w-full items-center justify-center gap-2 bg-cyan-200/[0.1] text-sm text-cyan-100/80 transition-colors hover:bg-cyan-200/[0.17] hover:text-cyan-50 disabled:cursor-not-allowed disabled:opacity-35"
            >
              {analyzing && <LoaderCircle size={15} className="animate-spin" strokeWidth={1.7} />}
              {analyzing ? "Analyzing dataset..." : "Analyze Data"}
            </button>
          </form>
        </section>

        <section className="min-h-[24rem] border border-white/[0.08] bg-[#0b121d]/75 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.14)] sm:p-7">
          <div className="mb-6 flex items-start justify-between gap-4">
            <div>
              <h2 className="text-sm font-medium tracking-wide text-white/90">Analysis result</h2>
              <p className="mt-2 text-xs leading-5 text-white/40">The Analytics Agent response will appear here.</p>
            </div>
            {result && <span className="text-[11px] uppercase tracking-[0.16em] text-teal-200/55">Complete</span>}
          </div>

          {error ? (
            <div className="border border-red-300/15 bg-red-300/[0.05] px-4 py-3 text-sm leading-6 text-red-100/70">
              {error}
            </div>
          ) : analyzing ? (
            <div className="flex min-h-56 items-center justify-center gap-3 text-sm text-cyan-100/55">
              <LoaderCircle size={17} className="animate-spin" strokeWidth={1.6} />
              Processing the dataset...
            </div>
          ) : result ? (
            <div className="max-h-[34rem] overflow-auto border border-white/[0.08] bg-[#080e17]/80 p-5 sm:p-6">
              <div className="border-b border-white/[0.08] pb-6">
                <p className="text-[11px] uppercase tracking-[0.18em] text-teal-200/55">Analysis Complete</p>
                {analysis?.answer && (
                  <p className="mt-3 text-lg leading-8 text-white/90">{analysis.answer}</p>
                )}
              </div>

              {(analysis?.operation || analysis?.column || analysis?.result !== undefined) && (
                <div className="grid gap-4 border-b border-white/[0.08] py-5 sm:grid-cols-3">
                  {analysis.operation && (
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.16em] text-white/35">Operation</p>
                      <p className="mt-2 text-sm capitalize text-white/75">{analysis.operation}</p>
                    </div>
                  )}
                  {analysis.column && (
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.16em] text-white/35">Column</p>
                      <p className="mt-2 truncate text-sm text-white/75">{analysis.column}</p>
                    </div>
                  )}
                  {analysis.result !== undefined && analysis.result !== null && (
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.16em] text-white/35">Result</p>
                      <p className="mt-1 text-2xl font-medium tracking-tight text-cyan-100/90">{analysis.result}</p>
                    </div>
                  )}
                </div>
              )}

              {hasDatasetOverview && (
                <div className="pt-5">
                  <p className="text-[11px] uppercase tracking-[0.18em] text-teal-200/55">Dataset Overview</p>
                  <div className="mt-4 grid gap-4 sm:grid-cols-3">
                    {datasetInfo.rows !== undefined && (
                      <div>
                        <p className="text-[11px] uppercase tracking-[0.16em] text-white/35">Rows</p>
                        <p className="mt-2 text-sm text-white/75">{datasetInfo.rows}</p>
                      </div>
                    )}
                    {datasetInfo.columns !== undefined && (
                      <div>
                        <p className="text-[11px] uppercase tracking-[0.16em] text-white/35">Columns</p>
                        <p className="mt-2 text-sm text-white/75">{datasetInfo.columns}</p>
                      </div>
                    )}
                    {Array.isArray(datasetInfo.numeric_columns) && (
                      <div>
                        <p className="text-[11px] uppercase tracking-[0.16em] text-white/35">Numeric Columns</p>
                        <p className="mt-2 text-sm text-white/75">{datasetInfo.numeric_columns.length}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex min-h-56 items-center justify-center border border-dashed border-white/[0.08] px-6 text-center text-sm leading-6 text-white/30">
              Upload a dataset and describe the analysis you need.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
