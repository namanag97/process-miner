# Process Mining Platform - Technology Demo

A scratch demo showcasing key technologies for the Process Mining & Business Automation Platform.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the demo
streamlit run app.py
```

## 📦 Demos Included

| Demo                     | Technology            | Description                        |
| ------------------------ | --------------------- | ---------------------------------- |
| **Predictive Analytics** | scikit-learn, XGBoost | Next activity & outcome prediction |
| **Process Simulation**   | SimPy                 | Digital twin DES simulation        |
| **Process Optimization** | PuLP                  | Resource allocation optimization   |
| **Document Processing**  | spaCy, pytesseract    | NER & entity extraction            |
| **Process Graph**        | NetworkX              | Process model visualization        |

## 🏗️ Structure

```
process_platform_demo/
├── app.py                 # Streamlit main app
├── demos/
│   ├── predictive.py      # ML prediction demo
│   ├── simulation.py      # SimPy simulation demo
│   ├── optimization.py    # PuLP optimization demo
│   ├── document.py        # IDP demo
│   └── graph.py           # Process graph demo
├── data/
│   └── sample_log.csv     # Sample event log
└── utils/
    └── generators.py      # Synthetic data generators
```

## 🎯 Use Cases Demonstrated

1. **Predict if a case will complete on time** using ML
2. **Simulate process changes** before implementation
3. **Optimize staffing levels** to minimize cost
4. **Extract entities** from business documents
5. **Visualize process flows** as interactive graphs
