# SmartEntry

**SmartEntry** is a facial recognition-based access management system for residential societies. It verifies the identity of domestic help at the entrance, checks if they are assigned to a specific apartment, and ensures they arrive within the permitted time frame.

## Features

- Face recognition using known and test images
- SQLite database for resident and domestic help data
- Time-bound entry validation
- Streamlit-based user interface
- Modular and scalable design

## Prerequisites

Make sure the following are installed:

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

## Installation

Follow these steps to install and run SmartEntry on your system:

# Clone the repository
```
git clone https://github.com/Aaryan-Poria/smartEntry.git
cd smartEntry
```
# Create a virtual environment
```
python -m venv venv
```
# Activate the virtual environment
## On Windows:
```
venv\Scripts\activate
```
## On macOS/Linux:
```
source venv/bin/activate
```
# Install required packages
```
pip install -r requirements.txt
```
# Run the Streamlit application
```
streamlit run streamlit_app.py
```
