# JMeter Executor Skill

Performance testing with Apache JMeter load generator.

## Features

- **Load Testing**: Configurable thread groups and ramp-up
- **Stress Testing**: Identify breaking points
- **HTML Reports**: Rich visualization of test results
- **CSV Results**: Machine-readable output for integration
- **Distributed Testing**: Support for remote JMeter servers
- **Custom Assertions**: Validate response data

## Installation

```bash
# macOS
brew install jmeter

# Linux (Debian/Ubuntu)
sudo apt install jmeter

# Manual
wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-5.6.3.tgz
tar -xzf apache-jmeter-5.6.3.tgz
export PATH=$PATH:/path/to/jmeter/bin
```

## Quick Start

```python
from metanoia.skills.jmeter_executor.executor import JMeterExecutor

executor = JMeterExecutor()
result = await executor.execute({
    "jmx_file": "load_test.jmx",
    "report_output": "./reports"
})
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `jmx_file` | string | required | Path to JMX test plan |
| `report_output` | string | - | HTML report output directory |
| `results_file` | string | "results.jtl" | Results file path |
| `jmeter_properties` | object | {} | Custom JMeter properties |
| `heap_size` | string | "512m" | JVM heap size |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success" or "error" |
| `report_path` | string | Path to HTML report |
| `metrics` | object | Parsed metrics |
| `summary` | string | Human-readable summary |
| `error` | string | Error message if failed |
