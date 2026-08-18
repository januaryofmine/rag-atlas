"use client";

import { FormEvent, useState } from "react";

type EvidenceRepo = {
  full_name: string;
  github_url: string;
  match_score: number;
  contribution_score: number;
  rag_types: string[];
  use_cases: string[];
  domains: string[];
};

type Developer = {
  github_id: number;
  login: string;
  github_url: string;
  avatar_url: string | null;
  match_score: number;
  profile_evidence_score: number;
  rag_types: string[];
  use_cases: string[];
  domains: string[];
  evidence_repos: EvidenceRepo[];
};

type SearchResponse = {
  repo_candidates: number;
  elapsed_ms: number;
  results: Developer[];
};

const API_URL = process.env.NEXT_PUBLIC_RAG_ATLAS_API_URL ?? "http://localhost:8000";

const RAG_TYPES = [
  ["GRAPH_RAG", "GraphRAG"],
  ["AGENTIC_RAG", "Agentic RAG"],
  ["SELF_RAG", "Self-RAG"],
  ["CORRECTIVE_RAG", "Corrective RAG"],
  ["HYBRID_RETRIEVAL", "Hybrid Retrieval"],
  ["MULTIMODAL_RAG", "Multimodal RAG"]
] as const;

export function SearchPage() {
  const [description, setDescription] = useState(
    "legal contract review and question answering over internal documents"
  );
  const [ragTypes, setRagTypes] = useState<string[]>([]);
  const [data, setData] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function toggle(value: string) {
    setRagTypes((current) =>
      current.includes(value) ? current.filter((item) => item !== value) : [...current, value]
    );
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/v1/search`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          product_description: description.trim(),
          rag_types: ragTypes,
          limit: 10
        })
      });
      if (!response.ok) throw new Error(await response.text());
      setData((await response.json()) as SearchResponse);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <header>
        <p className="eyebrow">RAG ATLAS</p>
        <h2>Find RAG engineers on Github</h2>
        <p className="lede">Repo-first search: match RAG projects first, then rank their contributors.</p>
      </header>

      <form className="card" onSubmit={submit}>
        <label htmlFor="description">Engineer who built:</label>
        <textarea
          id="description"
          rows={4}
          required
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />

        <p className="label">Optional RAG type soft boost</p>
        <div className="chips">
          {RAG_TYPES.map(([value, label]) => (
            <button
              type="button"
              key={value}
              className={ragTypes.includes(value) ? "chip selected" : "chip"}
              onClick={() => toggle(value)}
            >
              {label}
            </button>
          ))}
        </div>

        <button className="search" disabled={loading} type="submit">
          {loading ? "Searching…" : "Find engineers"}
        </button>
      </form>

      {error ? <p className="error">{error}</p> : null}

      {data ? (
        <section className="results">
          <p className="meta">{data.repo_candidates} repo candidates · {data.elapsed_ms} ms</p>
          {data.results.map((developer, index) => (
            <article className="card developer" key={developer.github_id}>
              <div className="developerHead">
                <div>
                  <span className="rank">#{index + 1}</span>{" "}
                  <a href={developer.github_url} target="_blank" rel="noreferrer">
                    @{developer.login}
                  </a>
                </div>
              </div>
              <p className="meta">{developer.rag_types.join(" · ") || "RAG evidence"}</p>
              <h3>Repos</h3>
              {developer.evidence_repos.map((repo) => (
                <a className="repo" key={repo.full_name} href={repo.github_url} target="_blank" rel="noreferrer">
                  <span>{repo.full_name}</span>
                </a>
              ))}
            </article>
          ))}
        </section>
      ) : null}
    </main>
  );
}
