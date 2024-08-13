# HWInsight

A real-time system monitoring tool that provides detailed insights into your CPU and GPU performance metrics. It utilises `LibreHardwareMonitor` to collect data and PyQt6 for the GUI, offering a user-friendly and visually appealing interface.

![](https://github.com/archiebhl/hwinsight/blob/master/gui.png?raw=true)

## Running executable
1. Download the relevant release.
2. Unzip the file into a single folder and run HWInsight.exe as administrator.

NOTE: CPU temperature readings will not work without administrator privileges.

## Building from source
### Prerequisites

- **.NET SDK** (for backend data collection)
- **Python 3.x** with the following libraries:
  - PyQt6
  - pyqtgraph
  - pglive
  - LibreHardwareMonitor

### Steps
1. **Clone the Repository**

`git clone https://github.com/archiebhl/hwinsight.git`

`cd hwinsight`

2. **Install Python dependencies**

`pip install -r requirements.txt`

3. **Run**

`dotnet build`

`python main.py`

## Contributing
Contributions are welcome. Please fork the repository and submit a pull request.

