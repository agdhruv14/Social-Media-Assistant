# Social Media Post Reviewer

## Setup Instructions

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m textblob.download_corpora
cp .env.example .env  
python app.py
```