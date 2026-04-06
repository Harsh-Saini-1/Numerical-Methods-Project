# CPU Usage Area Calculator
### Real-Time CPU Usage Analysis Using Numerical Integration

## Overview
The CPU Usage Area Calculator is a Python-based desktop application that monitors CPU utilization in real time and computes the cumulative workload using the Trapezoidal Rule (Numerical Integration).

Unlike traditional monitoring tools that only display instantaneous CPU usage, this project provides a quantitative measure of CPU workload over time (%·s) along with a live graphical visualization.

---

## Features

- Real-Time CPU Monitoring using psutil  
- Live Graph Visualization using matplotlib  
- Area Calculation using Trapezoidal Rule  
- GUI built with PyQt6  
- Dark / Light Mode Toggle  
- Pause / Resume Monitoring  
- Reset Functionality  
- Lightweight and Efficient  

---

## Tech Stack

Language: Python  

Libraries:
- psutil  
- PyQt6  
- matplotlib  
- numpy  

---

## Project Structure

cpu-usage-analyzer/
│── cpu_analyzer.py  
│── requirements.txt  
│── README.md  

---

## Installation

1. Clone the repository:
git clone https://github.com/Harsh-Saini-1/Numerical-Methods-Project.git

2. Navigate to the project folder:
cd cpu-usage-analyzer

3. Create a virtual environment (optional but recommended):
python -m venv env

Activate environment:
For Windows:
env\Scripts\activate

For Linux/macOS:
source env/bin/activate

4. Install dependencies:
pip install -r requirements.txt

---

## Usage

Run the application:
python cpu_analyzer.py

After running:
- GUI will open  
- CPU usage updates in real-time  
- Graph displays CPU trends  
- Area is calculated automatically  

---

## How It Works

1. CPU usage is collected every second using psutil  
2. Time difference between readings is calculated  
3. Trapezoidal Rule is applied:

Area = ((CPU_previous + CPU_current) / 2) * delta_time

4. Values are accumulated to compute total workload  
5. Results are shown in GUI and graph  

---

## Screenshots

(Add your screenshots here)

- GUI Dashboard  
- Real-Time Graph  
- Area Calculation Display  

---

## Applications

- System performance analysis  
- Resource usage tracking  
- Educational demonstration of numerical methods  
- Debugging CPU-intensive applications  

---

## Future Improvements

- Multi-core CPU analysis  
- GPU monitoring  
- Data export (CSV/Excel)  
- Web-based dashboard  
- Predictive analytics  
- Custom sampling intervals  

---

## Contributing

Contributions are welcome. Feel free to fork the repository and submit a pull request.

---

## License

This project is open-source and available under the MIT License.

---

## Author

Harsh  
Computer Science Engineering  
Chandigarh University  
