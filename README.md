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
    where $REVOLUT is the path to the file containing the list of stocks to be analyzed (csv exported from Revolut), as well as $ETRADE is the path to the **csv** file containing tax summary exported from Etrade. 
4. You can check --help for more options
   ```bash
   python -m stock --help
   ```

## How to calculate tax on crypto in Poland
Currently only Revolut is supported as a datasource.

1. Prepare environment
2. Export statement on your crypto from Revolut to csv file.
3. Run the script
   ```bash
   python -m crypto -f $CRYPTO -y 2022
   ```
    where $CRYPTO is the path to the file containing the list of crypto to be analyzed (csv exported from Revolut).
4. You can check --help for more options
   ```bash
   python -m crypto --help
   ```