import { useCallback, useEffect, useMemo, useState } from 'react'
import { accessToken, keycloak } from './auth'

type Priority = 'standard' | 'elevated' | 'urgent'
type Prediction = {
  prediction_id: string
  predicted_severity: number
  priority_band: Priority
  model_version: string
  top_factors: string[]
  created_at: string
}
type Claim = {
  claim_id: string
  status: string
  features: Record<string, string | number>
  selected_priority: Priority | null
  decision_reason: string | null
  updated_at: string
  predictions: Prediction[]
}

const demoClaim = {
  claim_id: 'clm_web_demo',
  policy_tenure_days: 842,
  claim_type: 'collision',
  reporting_delay_hours: 4.5,
  initial_estimate: 7200,
  prior_claim_count_365d: 1,
  prior_paid_amount_730d: 1500,
  damage_indicator_count: 3,
  region_code: 'ON_METRO',
  channel: 'mobile',
  asset_age_years: 5,
  coverage_type: 'standard',
  deductible_band: 'medium',
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await accessToken()
  const response = await fetch(path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(init?.headers ?? {}),
    },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(body.detail ?? 'Request failed')
  }
  return response.json() as Promise<T>
}

function PriorityBadge({ value }: { value: Priority }) {
  return <span className={`priority priority-${value}`}>{value}</span>
}

export default function App() {
  const [claims, setClaims] = useState<Claim[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [message, setMessage] = useState('Loading the shared review queue…')
  const [busy, setBusy] = useState(false)
  const [decision, setDecision] = useState<Priority>('elevated')
  const [reason, setReason] = useState('Manual inspection needs specialist review')
  const username = keycloak.tokenParsed?.preferred_username ?? 'signed-in user'
  const role = ['reviewer', 'supervisor', 'audit-reader'].find((candidate) =>
    keycloak.hasRealmRole(candidate),
  )
  const canWrite = role === 'reviewer' || role === 'supervisor'

  const selected = useMemo(
    () => claims.find((claim) => claim.claim_id === selectedId) ?? claims[0],
    [claims, selectedId],
  )
  const latest = selected?.predictions.at(-1)

  const refresh = useCallback(async () => {
    const data = await request<Claim[]>('/api/claims')
    setClaims(data)
    setSelectedId((current) => current ?? data[0]?.claim_id ?? null)
    setMessage(data.length ? `${data.length} claim${data.length === 1 ? '' : 's'} ready` : 'Queue is empty')
  }, [])

  useEffect(() => {
    refresh().catch((error: Error) => setMessage(error.message))
  }, [refresh])

  const act = async (action: () => Promise<unknown>, success: string) => {
    setBusy(true)
    try {
      await action()
      await refresh()
      setMessage(success)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Action failed')
    } finally {
      setBusy(false)
    }
  }

  const addDemo = () =>
    act(
      () => request('/api/claims', { method: 'POST', body: JSON.stringify(demoClaim) }),
      'Synthetic claim added to the queue',
    )

  return (
    <div className="shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">Claims operations</span>
          <h1>Review intelligence</h1>
        </div>
        <div className="identity">
          <span className="status-dot" /> {username} · {role ?? 'no application role'}
          <button className="logout" onClick={() => keycloak.logout({ redirectUri: window.location.origin })}>Log out</button>
        </div>
      </header>

      <main>
        <section className="hero">
          <div>
            <p className="eyebrow">Shared queue</p>
            <h2>See the signal. Keep the judgment human.</h2>
            <p>Severity estimates help order review work; they never approve or reject a claim.</p>
          </div>
          <button className="primary" onClick={addDemo} disabled={!canWrite || busy || claims.some((c) => c.claim_id === demoClaim.claim_id)}>
            Add demo claim
          </button>
        </section>

        <div className="notice">{message}</div>

        <section className="workspace">
          <aside className="queue panel">
            <div className="panel-title"><h3>Claims</h3><span>{claims.length}</span></div>
            {claims.map((claim) => {
              const prediction = claim.predictions.at(-1)
              return (
                <button key={claim.claim_id} className={`queue-item ${selected?.claim_id === claim.claim_id ? 'active' : ''}`} onClick={() => setSelectedId(claim.claim_id)}>
                  <span><strong>{claim.claim_id}</strong><small>{String(claim.features.claim_type)} · {String(claim.features.region_code)}</small></span>
                  {prediction ? <PriorityBadge value={prediction.priority_band} /> : <span className="unscored">unscored</span>}
                </button>
              )
            })}
            {!claims.length && <p className="empty">Add the demo claim to begin the reviewer workflow.</p>}
          </aside>

          <section className="detail panel">
            {!selected ? <div className="empty-state"><h3>No claim selected</h3><p>The detail workspace will show evidence, predictions, and reviewer decisions.</p></div> : <>
              <div className="claim-heading">
                <div><p className="eyebrow">Open claim</p><h3>{selected.claim_id}</h3></div>
                <span className="claim-status">{selected.status}</span>
              </div>

              <div className="metric-grid">
                <article><span>Initial estimate</span><strong>${Number(selected.features.initial_estimate).toLocaleString()}</strong></article>
                <article><span>Predicted severity</span><strong>{latest ? `$${latest.predicted_severity.toLocaleString()}` : 'Not scored'}</strong></article>
                <article><span>Model recommendation</span><strong>{latest ? <PriorityBadge value={latest.priority_band} /> : '—'}</strong></article>
                <article><span>Reviewer priority</span><strong>{selected.selected_priority ? <PriorityBadge value={selected.selected_priority} /> : 'Not decided'}</strong></article>
              </div>

              <div className="columns">
                <div>
                  <h4>Evidence at report time</h4>
                  <dl className="facts">
                    {Object.entries(selected.features).map(([key, value]) => <div key={key}><dt>{key.replaceAll('_', ' ')}</dt><dd>{String(value)}</dd></div>)}
                  </dl>
                </div>
                <div>
                  <h4>Prediction history</h4>
                  {!selected.predictions.length && <p className="empty">No prediction has been requested.</p>}
                  {selected.predictions.map((prediction) => <article className="history" key={prediction.prediction_id}>
                    <div><PriorityBadge value={prediction.priority_band} /><strong>${prediction.predicted_severity.toLocaleString()}</strong></div>
                    <small>Model {prediction.model_version} · {new Date(prediction.created_at).toLocaleString()}</small>
                    <p>Leading factors: {prediction.top_factors.join(', ')}</p>
                  </article>)}
                  <button className="primary full" disabled={!canWrite || busy} onClick={() => act(() => request(`/api/claims/${selected.claim_id}/predictions`, { method: 'POST' }), 'Prediction saved with its input snapshot')}>Request prediction</button>
                </div>
              </div>

              <form className="decision" onSubmit={(event) => {
                event.preventDefault()
                act(() => request(`/api/claims/${selected.claim_id}/decision`, { method: 'PUT', body: JSON.stringify({ priority: decision, reason }) }), 'Reviewer decision recorded in the audit trail')
              }}>
                <div><h4>Human review decision</h4><p>The reviewer may disagree with the model. A reason makes that judgment inspectable.</p></div>
                <select value={decision} onChange={(event) => setDecision(event.target.value as Priority)}><option value="standard">Standard</option><option value="elevated">Elevated</option><option value="urgent">Urgent</option></select>
                <input value={reason} onChange={(event) => setReason(event.target.value)} minLength={5} required />
                <button className="secondary" disabled={!canWrite || busy}>Save decision</button>
              </form>
            </>}
          </section>
        </section>
      </main>
    </div>
  )
}
