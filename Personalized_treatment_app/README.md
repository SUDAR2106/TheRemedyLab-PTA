# 🧠 Personalized Treatment App

A Streamlit-based application for document analysis using OCR, NLP, and PDF/Word processing tools.

---

## 📦 Features

- Extract text from PDFs (PyMuPDF, pdfplumber, PyPDF2)
- Read Word documents (`python-docx`)
- OCR from scanned images (`pytesseract`, `opencv-python`, `Pillow`)
- Named Entity Recognition with `spaCy`
- User login with password hashing (`bcrypt`)
- Integration with OpenAI for smart processing
- Streamlit web UI

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/personalized-treatment-app.git
cd personalized-treatment-app
``` 
### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate.bat  # On Windows
``` 
### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
### 4. Set Up Environment Variables
Create a `.env` file in the root directory with the following content:

```
OPENAI_API_KEY=your_openai_api_key
```
### 5. Run the Application

```bash
streamlit run main_app.py
```
