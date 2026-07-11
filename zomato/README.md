# Culinary Compass

Project code and docs live in this folder. For the full project README (setup, API, phases), see the repository root:

**[../README.md](../README.md)**

Quick links:

| Doc | Path |
|---|---|
| Architecture | [architecture.md](./architecture.md) |
| Problem statement | [problemstatement.md](./problemstatement.md) |
| Next.js frontend | [phase7/README.md](./phase7/README.md) |
| Streamlit deploy | [phase9/README.md](./phase9/README.md) |

```powershell
# From this directory
pip install -r requirements.txt
python -m phase6.validate --serve          # API :8000
# other terminal:
cd phase7; npm install; npm run dev        # UI :3000
# or:
python -m streamlit run phase9/app.py      # Streamlit :8501
```
