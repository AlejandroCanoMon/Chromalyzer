# 🧠 Chromalyzer

**Chromalyzer** is an interactive forensic analysis tool that extracts sensitive browser data such as history, passwords, cookies, and more. It is designed to assist cybersecurity professionals and researchers in analyzing browser activity for forensic purposes. This project was developed as part of a Bachelor's Thesis in Software Engineering with a focus on Cybersecurity.

## 🚀 Features

- Extracts data from Chromium-based browsers (e.g. Chrome, Edge, Brave):
  - 🧠 Browsing history
  - 🔐 Stored credentials
  - 🍪 Cookies
  - 🧾 Autofill information
  - ⬇️ Download history
  - 🧩 Installed extensions
- ☣️ Verifies visited URLs using [VirusTotal](https://www.virustotal.com/)
- 🕵️‍♂️ Checks stored credentials against known breaches via [LeakCheck.io](https://leakcheck.io/)
- 📄 Generates a full forensic report in PDF format
- 💬 Interactive terminal-based interface with step-by-step prompts

## 📁 File Structure

```
Chromalyzer/
│
├── .gitattributes
├── LICENSE
├── README.md
│
├── main.py            # Entry point - interactive flow
├── config.py          # API keys and config variables
├── utils.py           # Shared utility functions
│
├── autofill.py        # Autofill data module
├── cookies.py         # Cookies extraction
├── credentials.py     # Passwords extraction
├── downloads.py       # Download history
├── extensions.py      # Installed extensions
├── history.py         # Browsing history
├── pdf_generator.py   # PDF report generation
```

## 🧪 How to Use

1. Clone this repository and enter the folder:

```
git clone https://github.com/yourusername/Chromalyzer.git
cd Chromalyzer
```

2. Create a virtual environment and activate it:

```
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

3. Install required packages:

```
pip install -r requirements.txt
```

4. Open `config.py` and set your API keys:

```python
# config.py
VT_API_KEY = "your_virustotal_api_key"
LEAKCHECK_API_KEY = "your_leakcheck_api_key"
```

5. Run the tool:

```
python main.py
```

6. Follow the interactive prompts to perform the forensic analysis.

## ⚠️ Legal Disclaimer

This tool is intended for **educational and authorized forensic use only**. Do not use it on systems you do not own or have explicit permission to analyze. Unauthorized use may be illegal.

## 📄 License

This project is licensed under the MIT License. See `LICENSE` for more details.

## 👨‍💻 Author

**Alex** — Final Year Software Engineering Student  
Specialization in Cybersecurity  
Project: Bachelor’s Thesis (TFG)  
Tool: *Chromalyzer*

---
