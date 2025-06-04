# Sentence Alignment Evaluation with OpusFilter

## Description

This project uses **OpusFilter** to apply filters to sentence pairs that are **supposedly aligned (English/French)** in order to clean and assess their alignment quality. The main goal is to develop a tool to evaluate the quality of corpora provided on the website [https://opus.nlpl.eu/](https://opus.nlpl.eu/).

The filters were selected based on **benchmarks** we conducted (on ./scripts/benchmark-filters-test.py) and are considered to be the most relevant for detecting **misaligned or erroneous sentence pairs**.

The project also includes a **React user interface** that allows the user to view misaligned sentence pairs and choose to either **accept or delete** them.

---

## Features

- **Sentence Pair Filtering**: Apply filters to English and French sentence pairs to detect alignment errors.
- **User Interface**: Allows the user to **validate or delete** misaligned sentence pairs through a simple interface.
- **Save Results**: Validated sentence pairs are saved for future use.
- **Alignment Quality Evaluation**: The project enables the evaluation of alignment quality for corpora from the Opus website.

---

## Installation

### Prerequisites

- **Node.js** (version 14 or above)
- **OpusFilter** (must be installed on your system)
- **Python** (for the backend)

### 1. Install requiered Python libraries for running the backend (optionnal - create a venv environnement)

```
cd backend
python -m venv venv
source venv/bin/activate
cd ..
pip install -r requirements.txt
```

### 2. Run the backend (Fastapi)

```
uvicorn app.main:app
```

### 3. Install Node.js dependencies

```
cd frontend/
npm install
```

### 4. Run the app

```
npm start
```

---

Feel free to contact me if you have any questions, suggestions, or want to contribute to the project.
You can also open an issue here on GitHub for bug reports or feature requests.
