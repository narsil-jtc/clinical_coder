# Clinical Coder — Public Hosted Deployment Plan

## Context

The app works locally with Ollama. The user wants to share a public URL with a friend who will use it with **real clinical notes**. This is a significant shift: Ollama can't run on free cloud hosting (no GPU, ~256MB–1GB RAM limits), so we switch to OpenAI for LLM inference. We use Streamlit Community Cloud (free) as the host — it auto-deploys from GitHub, provides HTTPS, and has viewer authentication so only the invited friend can access the app.

**Privacy shift to communicate clearly:** In local mode, notes never leave the machine. In hosted mode, notes flow through Streamlit's servers (Snowflake/AWS in-memory) before de-identification → then only the de-identified version goes to OpenAI. This is accepted practice for cloud-assisted clinical tools, but the user must be aware and the friend must consent.

---

## Architecture

```
Friend's browser ──HTTPS──► Streamlit Community Cloud (server-side Python)
                                      │
                        De-identify locally on server
                                      │
                             OpenAI API (gpt-5.4-mini)
                              (receives de-identified text only)
```

- **Host**: Streamlit Community Cloud (free tier, https://share.streamlit.io)
- **Auth**: Streamlit viewer authentication — invite friend by email, they need a free Streamlit account
- **LLM**: OpenAI API forced via Streamlit Secrets
- **Retrieval**: Chroma DB included in git (184KB, no patient data — remove from .gitignore)
- **Secrets**: Stored in Streamlit dashboard (never in git)

---

## Step 0 — Security First (Before Any Git Work)

1. **Revoke the exposed OpenAI API key** that is currently in `.env`:
   - Go to platform.openai.com → API Keys → revoke the exposed key
   - Generate a new one if needed for hosted mode
2. **Rotate the OpenAI API key** after revocation so hosted mode uses a fresh credential
3. **Confirm `.env` is not in git history** — if it was ever committed, use `git filter-repo` or BFG to purge it

---

## Files to Create

### 1. `requirements.txt` (project root)

Streamlit Community Cloud reads this for dependencies. Mirrors pyproject.toml core deps but excludes `ollama` (not needed) and adds `openai`.

```
streamlit>=1.39,<2.0
pydantic>=2.9,<3.0
pydantic-settings>=2.6,<3.0
pandas>=2.2,<3.0
chromadb>=0.6
langchain-chroma>=0.1.4
sentence-transformers>=3.4.1
openai>=1.0,<2.0
```

### 2. `.streamlit/config.toml`

Professional theme + required server settings for cloud hosting:

```toml
[theme]
primaryColor = "#0D6EFD"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F8F9FA"
textColor = "#212529"
font = "sans serif"

[browser]
gatherUsageStats = false

[server]
headless = true
enableCORS = false
```

### 3. `.streamlit/secrets.toml.example`

Template showing what to paste into the Streamlit dashboard (never commit the real file):

```toml
# Paste these into Streamlit Community Cloud → App Settings → Secrets
# Never commit the real secrets.toml

OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-5.4-mini"

REASONING_MODE = "hybrid"
REASONING_PROVIDER = "openai"
CLOUD_ALLOWED_TASKS = "extract,coding,explain"
DEIDENTIFY_REQUIRED_FOR_CLOUD = "true"
SEND_RAW_NOTES = "false"

HOSTED_MODE = "true"

HIGH_CONFIDENCE_THRESHOLD = "0.80"
LOW_CONFIDENCE_THRESHOLD = "0.50"
```

---

## Files to Modify

### 4. `.gitignore` — Track the Chroma DB

Remove `data/chroma_db/` from .gitignore so the pre-built 184KB index is included in git. It contains only ICD-10 terminology embeddings — no patient data.

```diff
-data/chroma_db/
+# data/chroma_db/ — included in git: ICD-10 terminology index only (no patient data)
```

### 5. `src/clinical_coder/config/settings.py` — Add hosted mode flag

Add one field after `debug_log_prompts`:

```python
hosted_mode: bool = False
```

This is read from `HOSTED_MODE=true` in Streamlit Secrets (which become env vars automatically).

### 6. `src/clinical_coder/ui/app.py` — Hosted mode UI adaptations

Three changes:

**A. Import settings at top of app.py** (already imported — verify it's `from clinical_coder.config.settings import settings`)

**B. Privacy consent banner** — Add at the very start of `main()`, before any layout:

```python
if settings.hosted_mode:
    st.info(
        "**Privacy notice:** This app processes clinical notes using cloud AI. "
        "Notes are automatically de-identified on this server before being sent to OpenAI. "
        "Your original note is never stored. "
        "By continuing you acknowledge this data flow.",
        icon="🔒",
    )
```

**C. Sidebar adjustments** — Wrap Ollama-specific controls in `if not settings.hosted_mode:`:
- Hide the "Use cloud AI" toggle (replace with a static label "Cloud AI: OpenAI (de-identified)")
- Hide "AI engine settings" expander (Ollama ctx/tokens/keep-alive — irrelevant in hosted mode)
- Keep: code list selector, note type selector

Approximate change in the sidebar section:

```python
# Replace the hybrid toggle with this block:
if settings.hosted_mode:
    st.caption("Cloud AI: OpenAI · Notes de-identified before sending")
    use_cloud = True  # forced
else:
    use_cloud = st.toggle("Use cloud AI ...")  # existing toggle

# Wrap AI engine settings expander:
if not settings.hosted_mode:
    with st.expander("AI engine settings"):
        ...  # existing Ollama controls
```

---

## Deployment Steps

### Step 1 — Set up GitHub repository

```bash
cd "c:/Users/nhojt/Projects/Clinical Coder"
git init
git add .
git commit -m "Initial commit: Clinical Coder hosted deployment"
```

Create a new GitHub repo (can be private), then push:

```bash
git remote add origin https://github.com/<your-username>/clinical-coder.git
git push -u origin main
```

### Step 2 — Deploy to Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub
2. Click **New app**
3. Set:
   - Repository: your GitHub repo
   - Branch: `main`
   - Main file path: `src/clinical_coder/app/streamlit_app.py`
4. Click **Advanced settings → Secrets** and paste contents from `.streamlit/secrets.toml.example` (with real values filled in)
5. Click **Deploy**

First deploy takes ~3–5 minutes (installs deps, downloads sentence-transformers model).

### Step 3 — Enable viewer authentication

1. In Streamlit Community Cloud, open your app → **Settings → Sharing**
2. Change from "Public" to **"Only specific people"**
3. Enter your friend's email address
4. They'll need to create a free Streamlit account (takes 1 minute, any Google/GitHub/email login)

### Step 4 — Share the URL

Send your friend:
- The app URL (e.g. `https://yourusername-clinical-coder-streamlit-app.streamlit.app`)
- A note that they need to log in with the email address you invited

---

## Verification

1. Visit the app URL while logged in as yourself — check it loads and the privacy banner appears
2. Log out, visit as the friend's invited email — confirm access works
3. Try visiting while NOT logged in — confirm it requires login
4. Paste the built-in sample note, click Run
5. Verify:
   - Codes appear with correct labels
   - Privacy panel shows redacted items
   - "De-identified text" in privacy panel matches expected output (names/dates replaced)
   - No raw identifiers visible in the OpenAI call (check privacy panel)
6. Try submitting with no note — confirm graceful error, no crash
7. Test the "Start over" button resets state cleanly

---

## Notes & Trade-offs

| Concern | Mitigation |
|---------|------------|
| Raw notes pass through Streamlit's servers (Snowflake/AWS) | De-identification is server-side in Python before any external API call; HTTPS in transit; no persistent storage |
| OpenAI sees de-identified text | Expected and documented; only de-identified content is sent externally |
| Sentence-transformers model downloads at startup (~80–200MB) | Streamlit Community Cloud has 1GB RAM; first cold start takes ~2 min; subsequent starts are faster |
| Friend needs a Streamlit account | One-time setup taking ~60 seconds; free |
| No audit log persistence | Audit log writes to ephemeral filesystem on Streamlit Cloud — entries are lost on restart. Acceptable for this phase. |
