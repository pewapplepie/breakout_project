# Mini Quanta Project

A simple Python package for fetching historical stock data and analyzing breakout patterns.

I choose to use FastAPI for simplicity and Polygon.io for it's popular rest setups.

## Installation Setup

To set up a installation of this project, follow these steps:

1. Install requried packages

```bash
python -m venv venv
pip install -r requirements.txt
```

2. Set up your API key for Polygon.io:
   Create a .env file in your project directory and add the following line:

```
api_key=your_polygon_io_api_key
```

**NOTE**
Free account are limited to 1 year of historical data and 5 requests per minute

3.  Run the FastAPI application:

```bash
uvicorn main:app --reload
```

make sure user go to swagger UI with post requests at `/generate_report`
