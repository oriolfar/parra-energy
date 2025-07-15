# Parra Energy - Intelligent Solar Monitoring System

A comprehensive home energy management system designed for 2.2kW solar installations. Provides real-time monitoring, intelligent device automation, weather-aware optimization, and dual-mode dashboards for both technical and elderly users.

## 🌟 Features

### Core Functionality
- **Real-time Solar Monitoring**: Live tracking of solar production, consumption, and grid interaction
- **Smart Device Automation**: Automatic control based on solar surplus availability
- **Weather Integration**: Real weather data for accurate solar forecasting (Agramunt, Spain)
- **Dual Dashboard Modes**: Technical interface and simplified elderly-friendly Catalan interface
- **Historical Analytics**: Energy optimization insights and performance analysis

### Technical Features
- **Intelligent Inverter Detection**: Automatic fallback between real Fronius inverter and enhanced mock
- **Modular Architecture**: Clean separation of concerns with utils, config, and CLI modules
- **Comprehensive Testing**: Unit, integration, and system tests
- **Centralized Configuration**: Environment-aware configuration management
- **Advanced Logging**: Colored console output with configurable levels and file rotation

## 🏗️ Architecture

```
parra_energy/
├── api/                    # Fronius inverter communication
│   ├── fronius.py         # Real inverter client
│   ├── smart_fronius.py   # Intelligent detection system
│   └── enhanced_mock_fronius.py  # Advanced simulation
├── web/                    # Flask web application
│   ├── app.py             # Main web server and API
│   └── templates/         # Dashboard HTML templates
├── automations/            # Device automation system
│   └── manager.py         # Solar surplus-based control
├── analytics/              # Energy optimization engine
│   └── optimizer.py       # Recommendations and insights
├── weather/                # Weather integration
│   └── weather_service.py # Open-Meteo API integration
├── simulators/             # Device simulation
│   └── device.py          # Smart device modeling
├── utils/                  # Shared utilities
│   ├── database.py        # Database operations
│   ├── logger.py          # Logging system
│   ├── helpers.py         # Utility functions
│   └── validators.py      # Data validation
├── config/                 # Configuration management
│   └── settings.py        # System configuration
└── cli/                    # Command-line interface
    ├── main.py            # CLI commands
    └── commands.py        # Command implementations
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd parra-energy
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### First Run

1. **Initialize the system**:
   ```bash
   python cli.py setup --init-db
   ```

2. **Start the web server**:
   ```bash
   python run.py
   # OR use the CLI
   python cli.py start
   ```

3. **Access the dashboard**:
   - Open http://localhost:5001 in your browser
   - The system will automatically detect your Fronius inverter or use realistic mock data

## 🖥️ Usage

### Web Interface

The system provides two dashboard modes:

- **Technical Dashboard**: Detailed metrics, charts, manual controls, and system information
- **Elderly Dashboard**: Simplified Catalan interface with large fonts and actionable advice

Switch between modes using the toggle in the top-right corner.

### Command Line Interface

The CLI provides comprehensive system management:

```bash
# Start the system
python cli.py start

# Check system status
python cli.py status

# Export data
python cli.py data export 2024-01-15 --format csv

# Manage configuration
python cli.py config show
python cli.py config validate

# Run tests
python cli.py test --test-type unit

# Manage automation
python cli.py automation --list-devices
```

### API Endpoints

- `GET /api/status` - Real-time system status
- `GET /api/history/<date>` - Historical data for date
- `GET /api/analytics/tips` - Energy optimization recommendations
- `GET /api/weather/forecast` - Weather forecast data
- `POST /api/mock/controls` - Testing controls (mock mode)

## ⚙️ Configuration

The system uses environment-aware configuration:

- **Development**: `Config("development")` - Debug mode, verbose logging
- **Production**: `Config("production")` - Optimized for deployment
- **Testing**: `Config("testing")` - Fast intervals, test database

### Configuration Options

```python
# System configuration
solar_capacity_watts = 2200
inverter_host = "192.168.1.128"
location = "Agramunt, Spain"

# Web server
host = "localhost"
port = 5001
auto_open_browser = True

# Database
main_db_path = "data/energy_data.db"
keep_raw_data_days = 365

# Weather service
forecast_days = 7
api_base_url = "https://api.open-meteo.com/v1/forecast"
```

Environment variables can override configuration:
```bash
export INVERTER_HOST=192.168.1.100
export WEB_PORT=8080
export LOG_LEVEL=DEBUG
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# All tests
python cli.py test

# Specific test types
python cli.py test --test-type unit
python cli.py test --test-type integration

# Direct pytest usage
pytest tests/unit/ -v
pytest tests/integration/ -v
```

Test structure:
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for component interaction
- `tests/system/` - End-to-end system tests

## 📊 Database Schema

The system uses SQLite with comprehensive tables:

- **energy**: 5-minute energy readings
- **daily_energy**: Daily summaries
- **weather_forecast**: Weather data and forecasts
- **devices**: Automation device registry
- **automation_events**: Device control history
- **optimization_insights**: Generated recommendations

## 🌤️ Weather Integration

Real weather data for Agramunt, Spain (41.7869°N, 1.0968°E):
- Solar radiation and UV index
- Cloud cover and precipitation
- Temperature and wind speed
- 7-day forecasts for energy planning

## 🤖 Device Automation

Solar surplus-based device control:
- **Water Heater**: High priority, activated when significant surplus
- **EV Charger**: Medium priority, scheduled charging
- **Pool Pump**: Low priority, operates during peak solar hours
- **Smart Appliances**: Automated timing optimization

## 🧓 Elderly User Features

Special interface designed for older users:
- **Catalan Language**: Native language interface
- **Large Fonts**: Easy-to-read typography
- **Simple Advice**: Actionable energy recommendations
- **Minimal Complexity**: Focus on essential information

## 📈 Analytics & Optimization

Intelligent energy analysis:
- **Historical Patterns**: Usage trend identification
- **Efficiency Scoring**: Daily performance metrics
- **Optimization Tips**: Personalized recommendations
- **Weather Correlation**: Solar production forecasting
- **Cost Savings**: Economic impact analysis

## 🔧 Development

### Adding New Features

1. **API Endpoints**: Add to `web/app.py`
2. **CLI Commands**: Add to `cli/main.py`
3. **Configuration**: Update `config/settings.py`
4. **Database Tables**: Modify `utils/database.py`

### Code Quality

- **Type Hints**: All functions include type annotations
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Graceful failure and recovery
- **Logging**: Structured logging throughout
- **Testing**: High test coverage

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the logs: `logs/parra_energy.log`
- Run diagnostics: `python cli.py status`
- Review configuration: `python cli.py config show`

## 🏠 System Requirements

- **Python**: 3.8+
- **Operating System**: Linux, macOS, Windows
- **Hardware**: 2.2kW solar installation (recommended)
- **Network**: Access to Fronius inverter (optional - mock mode available)
- **Storage**: 100MB for database and logs

---

**Parra Energy** - Intelligent solar energy management for modern homes 🌞⚡🏠
