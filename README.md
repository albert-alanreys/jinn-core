# Jinn

Jinn is a framework for algorithmic trading strategies.

**Current version:** `3.1.2`

---

## Key Features

- 📈 **Optimization:** Finds optimal parameters for trading strategies to maximize performance.
- 🔍 **Backtesting:** Tests strategies on historical data with detailed trading statistics.
- 🤖 **Automation:** Executes strategies in real-time market conditions.

---

## Installation and Setup

### Requirements

1. Python version **3.13**.
2. Dependencies installed from `requirements.txt`.
3. Valid API keys from Binance and/or Bybit.
4. Telegram bot for notifications.

### Getting Started

#### 1. Install Python

Download and install [Python](https://www.python.org/downloads/). Ensure the **Add Python to PATH** option is enabled during installation.

#### 2. Install Dependencies

- **Using** `requirements.txt`

Open a terminal (or command prompt), navigate to the `Jinn` directory (e.g., `cd C:\Trading\Jinn`), and run:

```bash
pip install -r requirements.txt
```

- **Manually**

Open a terminal and install each package listed in `requirements.txt` individually:

```bash
pip install "package_name"
```

#### 3. Create `.env` File

Create a `.env` file in the project root and fill it with your credentials, using the example file at `help\.env.example` as a template. This file stores all sensitive project data.

## Running the Program

### Optimization

#### Optimizing a Single Strategy

1. In `settings.py`, set the `MODE` variable:

```python
MODE = enums.Mode.OPTIMIZATION
```

2. Specify optimization parameters in the `OPTIMIZATION_CONFIG` dictionary:

```python
OPTIMIZATION_CONFIG = {
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2019-01-01',
    'end': '2025-01-01',
    'strategy': enums.Strategy.NUGGET_V2,
}
```

Valid parameter values are listed in `help\config_enums.txt`.

3. Launch the program from the project's root directory using the terminal:

```bash
py main.py
```

#### Optimizing Multiple Strategies

1. In `settings.py`, set:

```python
MODE = enums.Mode.OPTIMIZATION
```

2. Create JSON optimization files named `optimization.json` inside each strategy folder (e.g., `Jinn\src\strategies\nugget_v2\optimization`). Example JSON (`help\optimization.json`):

```json
[
  {
    "exchange": "BINANCE",
    "market": "SPOT",
    "symbol": "BTCUSDT",
    "interval": "1h",
    "start": "2020-01-01",
    "end": "2025-01-01"
  },
  {
    "exchange": "BINANCE",
    "market": "SPOT",
    "symbol": "ETHUSDT",
    "interval": "1h",
    "start": "2020-01-01",
    "end": "2025-01-01"
  },
  {
    "exchange": "BINANCE",
    "market": "SPOT",
    "symbol": "XRPUSDT",
    "interval": "1h",
    "start": "2020-01-01",
    "end": "2025-01-01"
  }
]
```

Allowed keys and values are documented in `help\json_enums.txt`.

3. Launch the program from the project's root directory using the terminal:

```bash
py main.py
```

### Backtesting

#### Backtesting a Single Strategy

1. Set the mode in `settings.py`:

```python
MODE = enums.Mode.BACKTESTING
```

2. Specify testing parameters in the `BACKTESTING_CONFIG` dictionary:

```python
BACKTESTING_CONFIG = {
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2017-01-01',
    'end': '2019-12-01',
    'strategy': enums.Strategy.NUGGET_V2,
}
```

Refer to `help\config_enums.txt` for valid values.

3. Launch the program from the project's root directory using the terminal:

```bash
py main.py
```

4. Open your browser and navigate to http://127.0.0.1:5000 to view results.

#### Backtesting Multiple Strategies

1. Set the mode in `settings.py`:

```python
MODE = enums.Mode.BACKTESTING
```

2. Move the optimized parameter files from the `optimization` folder into the `backtesting` folder of the corresponding strategies. Adjust time periods if necessary.

3. Launch the program from the project's root directory using the terminal:

```bash
py main.py
```

4. Open your browser and navigate to http://127.0.0.1:5000 to view results.

### Automation

#### Automating a Single Strategy

1. Set the mode in `settings.py`:

```python
MODE = enums.Mode.AUTOMATION
```

2. Define automation parameters in `AUTOMATION_CONFIG`:

```python
AUTOMATION_CONFIG = {
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': 1,
    'strategy': enums.Strategy.DEVOURER_V3,
}
```

Refer to `help\config_enums.txt` for valid values.

3. Launch the program from the project's root directory using the terminal:

```bash
py main.py
```

4. Open your browser and navigate to http://127.0.0.1:5000 to view results.

#### Automating Multiple Strategies

1. Set the mode in `settings.py`:

```python
MODE = enums.Mode.AUTOMATION
```

2. Place automation JSON files in the respective strategy folders (e.g., `Jinn\src\strategies\nugget_v2\automation`). Two approaches:

- **Option 1:** Files with complete strategy parameters and their values. File names must include exchange, ticker, and interval (e.g., `BYBIT_BTCUSDT_1.json`). Parameters are defined in respective modules (e.g., `nugget_v2.py`). Example files are available in `help`.
- **Option 2:** Files with optimal parameters from the `optimization` folder, which can be reused in `automation`. The first parameter set will be applied.

3. Launch the program from the project's root directory using the terminal:

```bash
py main.py
```

4. Open your browser and navigate to http://127.0.0.1:5000 to view results.

## Additional Information

- A stable internet connection is required for proper operation.
- It is recommended to keep your system time synchronized regularly.
