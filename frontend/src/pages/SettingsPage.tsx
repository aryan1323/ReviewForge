import { useState, useEffect } from 'react'
import { Copy, Check, Settings } from 'lucide-react'
import { fetchConfig, saveConfig, UserConfig } from '../api/config'

function Field({ label, name, value, onChange, placeholder, type = 'text', readOnly = false }: {
  label: string; name: string; value: string; onChange?: (v: string) => void
  placeholder?: string; type?: string; readOnly?: boolean
}) {
  return (
    <div>
      <label className="block text-xs text-slate-400 mb-1">{label}</label>
      <input
        type={type}
        name={name}
        value={value}
        readOnly={readOnly}
        onChange={e => onChange?.(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-white/5 border border-border rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-accent disabled:opacity-60 read-only:opacity-60 read-only:cursor-default"
      />
    </div>
  )
}

export function SettingsPage() {
  const [config, setConfig] = useState<Partial<UserConfig>>({})
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchConfig().then(setConfig).finally(() => setLoading(false))
  }, [])

  function set(field: string, value: string) {
    setConfig(c => ({ ...c, [field]: value }))
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    const { webhook_url, ...rest } = config as UserConfig
    try {
      const updated = await saveConfig(rest)
      setConfig(updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
    } catch {
      setError('Failed to save settings')
    }
  }

  function copyWebhook() {
    if (!config.webhook_url) return
    const base = import.meta.env.VITE_API_URL || window.location.origin
    const full = `${base}${config.webhook_url}`
    navigator.clipboard.writeText(full)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading) return <div className="p-6 text-slate-500 text-sm">Loading…</div>

  return (
    <div className="p-6 max-w-2xl">
      <div className="flex items-center gap-2 mb-6">
        <Settings className="w-5 h-5 text-accent" />
        <h1 className="text-lg font-semibold text-slate-100">Settings</h1>
      </div>

      {/* Webhook URL */}
      <div className="card mb-6">
        <h2 className="text-sm font-semibold text-slate-200 mb-1">Your Webhook URL</h2>
        <p className="text-xs text-slate-500 mb-3">Paste this into GitHub repo → Settings → Webhooks → Payload URL</p>
        <div className="flex gap-2">
          <input
            readOnly
            value={config.webhook_url ? `${import.meta.env.VITE_API_URL || window.location.origin}${config.webhook_url}` : ''}
            className="flex-1 bg-white/5 border border-border rounded-lg px-3 py-2 text-xs text-slate-300 font-mono"
          />
          <button onClick={copyWebhook} className="px-3 py-2 rounded-lg border border-border text-slate-400 hover:text-slate-200 hover:border-accent transition-colors">
            {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
          </button>
        </div>
      </div>

      <form onSubmit={handleSave} className="card space-y-4">
        <h2 className="text-sm font-semibold text-slate-200">API Keys</h2>

        <div>
          <Field label="GitHub Token" name="github_token"
            value={config.github_token ?? ''} onChange={v => set('github_token', v)}
            placeholder="ghp_... (leave empty for public repos)" />
          <p className="text-xs text-slate-500 mt-1">Only required for <span className="text-amber-400">private repositories</span>. Public repos work without a token.</p>
        </div>

        <div>
          <Field label="GitHub Webhook Secret" name="github_webhook_secret"
            value={config.github_webhook_secret ?? ''} onChange={v => set('github_webhook_secret', v)}
            placeholder="any secret string you choose" />
          <p className="text-xs text-slate-500 mt-1">Set this same value in your GitHub webhook → <span className="text-slate-300">Settings → Webhooks → Edit → Secret</span> field.</p>
        </div>

        <div className="border-t border-border pt-4">
          <p className="text-xs text-slate-500 mb-4">Azure OpenAI</p>
          <div className="space-y-4">
            <Field label="API Key" name="azure_openai_api_key"
              value={config.azure_openai_api_key ?? ''} onChange={v => set('azure_openai_api_key', v)}
              placeholder="A72ty..." type="password" />
            <Field label="Endpoint" name="azure_openai_endpoint"
              value={config.azure_openai_endpoint ?? ''} onChange={v => set('azure_openai_endpoint', v)}
              placeholder="https://your-resource.openai.azure.com/" />
            <Field label="Deployment" name="azure_deployment"
              value={config.azure_deployment ?? ''} onChange={v => set('azure_deployment', v)}
              placeholder="o4-mini" />
            <Field label="API Version" name="azure_api_version"
              value={config.azure_api_version ?? ''} onChange={v => set('azure_api_version', v)}
              placeholder="2025-01-01-preview" />
            <Field label="Embedding Deployment (optional)" name="azure_embedding_deployment"
              value={config.azure_embedding_deployment ?? ''} onChange={v => set('azure_embedding_deployment', v)}
              placeholder="text-embedding-3-small" />
          </div>
        </div>

        {error && <p className="text-xs text-red-400">{error}</p>}

        <button type="submit"
          className="bg-accent hover:bg-accent/90 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors">
          {saved ? 'Saved!' : 'Save settings'}
        </button>
      </form>
    </div>
  )
}
