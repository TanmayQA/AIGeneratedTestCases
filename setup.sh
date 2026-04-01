#!/bin/bash

echo "🚀 Setting up QA Agent..."

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo "Run: source venv/bin/activate && streamlit run app.py"