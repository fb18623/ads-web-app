# ads-web-app

## Downloading and running

Clone or download the repository.

```bash
python -m venv venv
source venv/bin/activate  # Windows: \venv\scripts\activate
pip install -r requirements.txt
```

then run the app:
```bash
python app.py
```

## Deploy to Heroku

All pushes to the main branch are automatically deployed to Heroku here: https://covid-19-uk-twitter-sentiment.herokuapp.com/.

Debug some problems using
```bash
heroku logs --tail
```
