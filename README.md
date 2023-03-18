## How to prepare environment
1. Install python3
2. Install pip3
3. Install dependencies
    ```bash
    pip3 install -r requirements.txt
    ```

## How to calculate tax on stocks in Poland
1. Prepare environment
2. Export statement on your stocks from Revolut to csv file.
3. Run the script
    ```bash
    python -m stock -f $STOCKS -y 2022
    ```
    where $STOCKS is the path to the file containing the list of stocks to be analyzed (csv exported from Revolut).
4. You can check --help for more options
   ```bash
   python -m stock --help
   ```

## How to calculate tax on crypto in Poland
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