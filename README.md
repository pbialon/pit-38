## How to prepare environment
1. Install python3
2. Install pip3
3. Install dependencies
    ```bash
    pip3 install -r requirements.txt
    ```

## How to calculate tax on stocks in Poland
Currently two data sources are supported - ETRADE (basic support) and Revolut.

1. Prepare environment
2. Export statement on your stocks from Revolut to csv file.
3. Run the script
    ```bash
    python -m stock --revolut $REVOLUT --etrade $ETRADE -y 2022
    ```
    where 
    `$REVOLUT` is the path to the file containing the list of stocks to be analyzed (csv exported from Revolut)
    `$ETRADE` is the path to the **csv** file containing tax summary exported from Etrade. 
    `-y 2022` is the year for which the tax should be calculated. With no `-y` option, the script will calculate tax for the past year.
4. You can check --help for more options
   ```bash
   python -m stock --help
   ```

## How to calculate tax on crypto in Poland
Currently only Revolut is supported as a datasource.

1. Prepare environment
2. Export statement from your Revolut account to csv file (from `Start` page in Revolut app, not from `Crypto` page).
3. Run the script
   ```bash
   python -m crypto -f $CRYPTO -y 2022
   ```
    where 
    `$CRYPTO` is the path to the file containing the list of crypto to be analyzed (csv exported from Revolut).
    `-y 2022` is the year for which the tax should be calculated. With no `-y` option, the script will calculate tax for the past year.
4. You can check --help for more options
   ```bash
   python -m crypto --help
   ```
   
<a href="https://www.buymeacoffee.com/pbialon" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
