# Static Assets

This folder contains static files served by the web interface.

## Structure

```
static/
├── images/
│   └── quizzer-logo.png    # Application logo
└── README.md               # This file
```

## Usage

Static files are served by Flask at `/static/` URL path.

Example: `quizzer-logo.png` is accessible at:
- `http://localhost:5000/static/images/quizzer-logo.png`
