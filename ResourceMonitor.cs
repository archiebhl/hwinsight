using LibreHardwareMonitor.Hardware;
using System.Diagnostics;
using System;

namespace DataCollector
{
    public class UpdateVisitor : IVisitor
    {
        public void VisitComputer(IComputer computer)
        {
            computer.Traverse(this);
        }
        public void VisitHardware(IHardware hardware)
        {
            hardware.Update();
            foreach (IHardware subHardware in hardware.SubHardware) 
                subHardware.Accept(this);
        }
        public void VisitSensor(ISensor sensor) { }
        public void VisitParameter(IParameter parameter) { }
    }

    public class ResourceMonitor
    {
        public double CPU_TEMP { get; private set; }
        public double CPU_USAGE { get; private set; }
        public Dictionary<string, double> CPU_CLOCKS { get; private set; } = new Dictionary<string, double>();
        public double GPU_TEMP { get; private set; }
        public double GPU_USAGE { get; private set; }
        public double GPU_VRAM_MAX { get; private set; }
        public double GPU_VRAM_CURRENT { get; private set; }
        public List<double> gpuUsageData = new List<double>();
        public List<double> gpuTemperatureData = new List<double>();
        public List<double> gpuVramUsageData = new List<double>();
        public List<double> cpuUsageData = new List<double>();
        public List<double> cpuTemperatureData = new List<double>();
        public string? GPU_NAME;
        public string? CPU_NAME;
        private Guid clientId = Guid.NewGuid();
        public Dictionary<string, string> gpuExtraInfo = new Dictionary<string, string>();
        public Dictionary<string, string> cpuExtraInfo = new Dictionary<string, string>();
        // data file path
        private readonly string dataFilePath = "data.txt";

        static async Task Main(string[] args)
        {

            AppDomain.CurrentDomain.ProcessExit += new EventHandler(OnProcessExit);
            ResourceMonitor monitor = new ResourceMonitor();
    
            while (true)
            {
                monitor.Monitor();
                await Task.Delay(1000); 
            }
        }

        static void OnProcessExit(object? sender, EventArgs e)
        {
            Console.WriteLine("Process is exiting");
            
        }
                
        public void Monitor()
        {
            Computer computer = new Computer
            {
                IsCpuEnabled = true,
                IsGpuEnabled = true,
                IsMemoryEnabled = false,
                IsMotherboardEnabled = false,
                IsControllerEnabled = false,
                IsNetworkEnabled = false,
                IsStorageEnabled = false
            };

            try
            {
                computer.Open();
            }
            catch (NullReferenceException)
            {
                Debug.WriteLine("An exception of type 'System.NullReferenceException' occurred in LibreHardwareMonitorLib.dll");
                Debug.WriteLine("'Object reference not set to an instance of an object.'");
            }

            Debug.Flush();
            computer.Accept(new UpdateVisitor());

            CollectCpuData(computer);
            CollectGpuData(computer);

            try
            {
                computer?.Close();
            }
            catch (NullReferenceException)
            {
                Debug.WriteLine("An exception of type 'System.NullReferenceException' occurred in LibreHardwareMonitorLib.dll");
                Debug.WriteLine("'Object reference not set to an instance of an object.'");
            }
            LogDataToFile();
            Debug.Flush();
        }

        private void CollectCpuData(Computer computer)
        {
            foreach (IHardware hardware in computer.Hardware)
            {
                if (hardware.HardwareType.ToString().Equals("Cpu"))
                {
                    CPU_NAME = hardware.Name;
                    var clockData = new Dictionary<string, double>();

                    foreach (ISensor sensor in hardware.Sensors)
                    {
                        double sensorValue = sensor.Value.HasValue ? (double)Math.Round(sensor.Value.Value, 0) : 0;
                        if (sensor.SensorType.ToString().Equals("Temperature") && sensor.Name.ToString().Equals("Core Average"))
                        {
                            CPU_TEMP = sensorValue;
                            cpuTemperatureData.Add(CPU_TEMP);
                        }
                        else if (sensor.SensorType.ToString().Equals("Load") && sensor.Name.ToString().Equals("CPU Total"))
                        {
                            CPU_USAGE = sensorValue;
                            cpuUsageData.Add(CPU_USAGE);
                        }
                        else
                        {       
                            string units = getUnits(sensor);                     
                            cpuExtraInfo[sensor.Name] = string.Format("{0}{1}", sensorValue, units);
                        }
                    }
                }
            }
        }

        private void CollectGpuData(Computer computer)
        {   
            foreach (IHardware hardware in computer.Hardware)
            {
                if (hardware.HardwareType.ToString().Contains("Gpu"))
                {
                    GPU_NAME = hardware.Name;

                    foreach (ISensor sensor in hardware.Sensors)
                    {
                        double sensorValue = sensor.Value.HasValue ? (double)Math.Round(sensor.Value.Value, 0) : 0;

                        if (sensor.SensorType.ToString().Equals("Temperature") && sensor.Name.ToString().Equals("GPU Core"))
                        {
                            GPU_TEMP = sensorValue;
                            gpuTemperatureData.Add(GPU_TEMP);
                        }
                        else if (sensor.SensorType.ToString().Equals("Load") && sensor.Name.ToString().Equals("GPU Core"))
                        {
                            GPU_USAGE = sensorValue;
                            gpuUsageData.Add(GPU_USAGE);
                        }
                        else
                        {       
                            string units = getUnits(sensor);                     
                            gpuExtraInfo[sensor.Name] = string.Format("{0}{1}", sensorValue, units);
                        }
                    }
                }
            }
        }

        private string getUnits(ISensor sensor)
        {
            switch (sensor.SensorType.ToString())
            {
                case "Temperature":
                    return "°C";
                case "Clock":
                    return " MHz";
                case "Fan":
                    return " RPM";
                case "Control":
                    return "%";
                case "Load":
                    return "%";
                case "SmallData":
                    return " MB";
                case "Power":
                    return "";
                case "Throughput":
                    return " B/s";
                case "Voltage":
                    return " V";
                default:
                    return "";
            }
        }

        private void LogDataToFile()
        {
            try
            {   
                using (StreamWriter sw = new StreamWriter(dataFilePath, false))
                {
                    sw.WriteLine($"Timestamp: {DateTime.Now}");
                    sw.WriteLine($"CPU Name:  {CPU_NAME}");
                    sw.WriteLine($"GPU Name:  {GPU_NAME}");
                    sw.WriteLine($"CPU Temperature: {CPU_TEMP}°C");
                    sw.WriteLine($"CPU Usage: {CPU_USAGE}%");
                    sw.WriteLine($"GPU Temperature: {GPU_TEMP}°C");
                    sw.WriteLine($"GPU Usage: {GPU_USAGE}%");
                    foreach (var info in cpuExtraInfo)
                    {
                        sw.WriteLine($"{info.Key}: {info.Value}");
                    }
                    foreach (var info in gpuExtraInfo)
                    {
                        sw.WriteLine($"{info.Key}: {info.Value}");
                    }
                    sw.WriteLine(new string('-', 40));
                    sw.Flush();
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"An error occurred while writing to the log file: {ex.Message}");
            }
        }
    }
}
