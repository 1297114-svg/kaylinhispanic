# Hispanic Heritage Historical Data Explorer

A Streamlit app that displays historical indicators from the official World Bank API for 20 Spanish-speaking countries. Brazil is available as a separate Latin American comparison.

## Files
- `app.py` — application code
- `requirements.txt` — Python dependencies

## Run locally
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Upload `app.py` and `requirements.txt` to a GitHub repository.
2. Open Streamlit Community Cloud and choose **Create app**.
3. Select the repository, branch, and `app.py` as the main file.
4. Deploy.

## Deploy on Render
Create a Python Web Service and use:

Build command:
```bash
pip install -r requirements.txt
```

Start command:
```bash
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT
```

## Notes
- Data is retrieved live from the World Bank API and cached for one hour.
- Requested date range is current year minus 70 through current year minus 1.
- The app reports actual non-null observation count and actual coverage.
- This version includes country selection, indicator selection, visualization, optional Brazil comparison, and CSV export. It does not yet implement the full polynomial fitting/calculus feature set in the larger project specification.
