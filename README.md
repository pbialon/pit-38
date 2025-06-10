## How to prepare environment
1. Install python3
2. Install pip3
3. Install dependencies (best in virtualenv)
    ```bash
    pip3 install -r requirements.txt
    ```

## How to calculate tax on stocks in Poland / Jak obliczyć podatek od akcji w Polsce

### English

1. Prepare environment (see "How to prepare environment" section above)

2. Prepare data in standardized format:
   - Use appropriate plugin for your broker:
     ```bash
     python -m plugins.stock.revolut --input-path <export_path> --output-path <output_path>
     ```
     ```bash
     python -m plugins.stock.etrade --input-path <export_path> --output-path <output_path>
     ```
   - You can prepare multiple files from different brokers
   - You can also prepare a file manually in the format matching the example in `src/data_sources/stock_loader/example_format.csv`

3. Run the tax calculation script:
   ```bash
   python -m stock -f <file1> -f <file2> -f <file3> -y 2022
   ```
   where:
   - `-f` specifies files with transactions in standardized format
   - `-y 2022` specifies the year for tax calculation (optional, defaults to previous year)

4. For more options use:
   ```bash
   python -m stock --help
   ```

### Polski

1. Przygotuj środowisko (patrz sekcja "How to prepare environment" powyżej)

2. Przygotuj dane w ustandaryzowanym formacie:
   - Użyj odpowiedniego pluginu dla swojego brokera:
     ```bash
     python -m plugins.stock.revolut --input-path <sciezka_do_eksportu> --output-path <sciezka_wyjsciowa>
     ```
   - Możesz przygotować kilka plików od różnych brokerów
   - Możesz też przygotować plik ręcznie w formacie zgodnym z przykładem w `src/data_sources/stock_loader/example_format.csv`

3. Uruchom skrypt obliczający podatek:
   ```bash
   python -m stock -f <plik1> -f <plik2> -f <plik3> -y 2022
   ```
   gdzie:
   - `-f` określa pliki z transakcjami w ustandaryzowanym formacie
   - `-y 2022` określa rok, dla którego obliczany jest podatek (opcjonalne, domyślnie poprzedni rok)

4. Więcej opcji znajdziesz używając:
   ```bash
   python -m stock --help
   ```

## How to calculate tax on crypto in Poland/ Jak obliczyć podatek od kryptowalut w Polsce 

### English

1. Prepare environment (see "How to prepare environment" section above)

2. Prepare data in standardized format:
   - Use appropriate plugin for your broker:
     ```bash
     python -m plugins.crypto.revolut --input-path <export_path> --output-path <output_path>
     ```
   - You can prepare multiple files from different brokers
   - You can also prepare a file manually in the format matching the example in `src/data_sources/crypto_loader/example_format.csv`

3. Run the tax calculation script:
   ```bash
   python -m crypto -f <file1> -f <file2> -f <file3> -y 2022
   ```
   where:
   - `-f` specifies files with transactions in standardized format
   - `-y 2022` specifies the year for tax calculation (optional, defaults to previous year)

4. For more options use:
   ```bash
   python -m crypto --help
   ```

### Polski

1. Przygotuj środowisko (patrz sekcja "How to prepare environment" powyżej)

2. Przygotuj dane w ustandaryzowanym formacie:
   - Użyj odpowiedniego pluginu dla swojego brokera (np. Revolut):
     ```bash
     python -m plugins.crypto.revolut --input-path <sciezka_do_eksportu> --output-path <sciezka_wyjsciowa>
     ```
   - Możesz przygotować kilka plików od różnych brokerów
   - Możesz też przygotować plik ręcznie w formacie zgodnym z przykładem w `src/data_sources/crypto_loader/example_format.csv`

3. Uruchom skrypt obliczający podatek:
   ```bash
   python -m crypto -f <plik1> -f <plik2> -f <plik3> -y 2022
   ```
   gdzie:
   - `-f` określa pliki z transakcjami w ustandaryzowanym formacie
   - `-y 2022` określa rok, dla którego obliczany jest podatek (opcjonalne, domyślnie poprzedni rok)

4. Więcej opcji znajdziesz używając:
   ```bash
   python -m crypto --help
   ```



<a href="https://www.buymeacoffee.com/pbialon" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
