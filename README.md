# AUTOMATED-SIGNAL-GENERATOR
AUTOMATED SIGNAL GENERATOR FOR STOCKS/FX-PAIRS. A research oriented project to design a benchmark deep learning algorithm for Financial Market prediction and forecast.

```bash
+-- DATASSET
|    +-- AUD_CAD
|    +-- AUD_USD
|    +-- BTC_USD
|    +-- EUR_CAD
|    +-- EUR_GBP
|    +-- EUR_NZD
|    +-- EUR_USD
|    +-- GBP_USD
|    +-- NZD_USD
|    +-- USDCHF
+-- PREDICTED
|    +--H1
     |  +--AUD_CAD
     |  +--AUD_USD
     |  +-- ..etc
|    +-- H2
     |  +-- AUD_CAD
     |  +-- AUD_USD
     |  +-- ..etc
|    +-- H3
     |  +-- AUD_CAD
     |  +-- AUD_USD
     |  +-- ..etc
|    +-- H4
     |  +-- AUD_CAD
     |  +-- AUD_USD
     |  +-- ..etc
|    H6
|    H8
|    H12
|    M30
|    W
+-- SOURCE
|    | +-- Automated_Sugnal_generator.py
|    | +-- STOCK.py
```

## Requirement

```bash
pandas
pip install pandas
numpy
pip install numpy
OR
install anaconda/miniconda
```

## How to use

Ensure that you already have your dataset downloaded. For this project i used the Oanda API to download historical price.
See [How to Download historical stock/fx prices from oanda](https://github.com/fibai/OANDA-API-WRAPPER/tree/master/HISTORICAL%20PRICES)

```python
After the above process is completed
Run STOCK.py
$ python STOCK.py

Finally run 
$ python Automated_Signla_generator.py

This process initiates every 30mins. You can change the timer as desired.
```

## Demo GUI

![Image 1](https://github.com/fibai/AUTOMATED-SIGNAL-GENERATOR/blob/master/AI-signal.gif)
