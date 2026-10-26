# GTD Responsible Group Classification Research App

This project packages a local Random Forest research model for classifying the reported responsible organization in historical Global Terrorism Database (GTD) incident records. It follows the full stack workflow in the laboratory manual: a versioned model pipeline, a Flask JSON API, an Angular 22 form, automated tests, GitHub Actions, and a static GitHub Pages demonstration.

The model is based on the Random Forest baseline family evaluated in Abdalsalam et al. (2024). The article's main BiGRU-SA result uses DistilBERT summary embeddings and SMOTE-T; this project uses the paper's Random Forest comparator to keep the model small enough to train and serve locally. Its results are a local adaptation, not a reproduction of the paper's reported scores. See [methodology](docs/methodology.md) and the generated [local evaluation](docs/model-evaluation.md).

This is a research and teaching demonstration. It classifies historical incident records and must not be used for operational attribution, legal decisions, security decisions, or targeting.

## Project contents

- `backend/train_model.py` trains the preprocessing and Random Forest pipeline from the supplied GTD CSV, then saves the local model bundle and one-row smoke-test payload.
- `backend/app.py` serves `GET /health` and `POST /predict` on `127.0.0.1:5000`.
- `frontend/` contains the Angular 22 user interface. In local development, its `/api` proxy forwards requests to Flask.
- `.github/workflows/ci.yml` checks the API contract and Angular production build without uploading or downloading the GTD data or model.
- `.github/workflows/pages.yml` publishes only the Angular static site. GitHub Pages cannot run Flask or load the local model.
- `peerj-cs-2252.pdf` and the GTD CSV are local reference/input files and are excluded from Git.

## Requirements

- Windows 10/11, PowerShell, Git, and Python 3.11 or 3.12.
- Node.js 22.22.3 or newer in the 22.x line, or 24.15.0 or newer in the 24.x line, as required by Angular 22.
- The GTD release file `globalterrorismdb_0718dist.csv` in the project root. Obtain it through the [GTD Kaggle dataset page](https://www.kaggle.com/datasets/START-UMD/gtd) under its access terms. Do not commit the dataset.

## Train the model

Open PowerShell in the project root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python backend\train_model.py
```

The training script selects known organizations with at least 500 incidents, creates a stratified 80/20 holdout, fits a 200-tree Random Forest pipeline, and writes:

- `backend/models/model_bundle.joblib` (local artifact; ignored by Git)
- `backend/test_payload.json` and `data/sample_inputs.csv` (safe coded sample, no target column)
- `frontend/src/app/feature-schema.ts` (Angular form fields and category labels derived from this GTD release)
- `docs/model-evaluation.json` and `docs/model-evaluation.md`

This version of GTD contains 1970–2017 records. The group threshold produces the groups available in that release; the number of groups may differ from the paper's dataset version.

## Run the app locally

Install the Angular dependencies once:

```powershell
cd frontend
npm ci
```

Use two terminals from the project root. Terminal 1 starts Flask:

```powershell
.\.venv\Scripts\Activate.ps1
python backend\app.py
```

Terminal 2 starts Angular with the API proxy:

```powershell
cd frontend
npm start
```

Open <http://localhost:4200>. Confirm the API status is healthy, enter every required field, and submit. The interface displays the predicted group and the five highest class probabilities. Keep both servers running during local tests.

## Verify

From the project root, with the virtual environment active:

```powershell
python -m pytest -q backend\tests
python backend\test_pipeline.py
```

With Flask still running in another terminal:

```powershell
python backend\test_api.py
curl.exe --noproxy "*" http://127.0.0.1:5000/health
curl.exe --noproxy "*" http://localhost:4200/api/health
```

Build Angular for production:

```powershell
cd frontend
npm run build
```

## GitHub Pages boundary

GitHub Pages serves the Angular files only. It does not host Python, Flask, the model, or live inference. The deployed page shows a static-only notice and disables prediction. The app enables live inference only on localhost while the local Flask service is running.

For the `Doc-Mic/Project_DevOps` repository, the Pages URL is expected to be `https://doc-mic.github.io/Project_DevOps/` after the repository's Pages source is set to **GitHub Actions** and the deployment workflow succeeds.

## Research source

Abdalsalam, M., Li, C., Dahou, A., & Kryvinska, N. (2024). *Terrorism group prediction using feature combination and BiGRU with self-attention mechanism*. PeerJ Computer Science, 10, e2252. <https://doi.org/10.7717/peerj-cs.2252>. The paper is from 2024 and reports Random Forest among its comparison models.