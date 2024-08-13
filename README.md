# HWInsight

<<<<<<< HEAD
A real-time system monitoring tool that provides detailed insights into your CPU and GPU performance metrics. It utilixes `LibreHardwareMonitor` to collect data and PyQt6 for the GUI, offering a user-friendly and visually appealing interface.

![](https://github.com/archiebhl/hwinsight/blob/master/gui.png?raw=true)

## Features

- **Real-time Monitoring**: Obtains information from various CPU and GPU sensors to enable real-time monitoring.
- **Customizable UI**: A more modernised GUI to monitor this data. 
- **Data Logging**: Logs system performance data to a text file for future analysis.

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
  - LibreHardwareMonitor (for backend)

### Steps
1. **Clone the Repository**
`git clone https://github.com/archiebhl/hwinsight.git`
`cd hwinsight`

2. **Install Python dependencies**
`pip install -r requirements.txt`

3. **Run**
`dotnet run --project DataCollector.csproj`
`python main.py`

## Contributing
Contributions are welcome. Please fork the repository and submit a pull request.
=======
A program to monitor real-time sensor data of PC components, with a focus on emphasising frquently useful metrics in a clean GUI.   

![](https://github.com/archiebhl/hwinsight/blob/master/gui.png?raw=true)

## Running Executable
1. Download the relevant release.
2. Unzip the file into a single folder and run HWInsight.exe as administrator.

NOTE: CPU temperature readings will not work without administrator privileges.
>>>>>>> a3f8d62570d42af3cf1f831a3ef3c387825512ff

