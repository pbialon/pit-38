# Plugins

## README in English

Plugins are designed to transform transaction data from various brokers into a standardized format that can be processed by this repository. Each plugin handles a specific broker's export file format and converts it to a unified CSV structure.

### Purpose

The main purpose of plugins is to:

1. Read transaction data from broker-specific export files
2. Transform this data into a standardized format
3. Save the transformed data as a CSV file that can be loaded by the generic loader and processed further

### Usage

Each plugin can be run from the command line with specific parameters. Typically, plugins require:

- Input path: Path to the broker's export file
- Output path: Where to save the standardized CSV file
- Optional parameters: Such as logging level

### Available Plugins

The repository includes plugins for various brokers. Check individual plugin directories for specific documentation.

### Adding New Broker Support

If your broker is not supported:

1. You can create a new plugin following the existing patterns
2. Request support by opening a GitHub issue
3. Submit a pull request with your implementation

---

## README po polsku

Wtyczki służą do przekształcania danych transakcyjnych z różnych brokerów w ustandaryzowany format, który może być przetwarzany przez to repozytorium. Każda wtyczka obsługuje specyficzny format pliku eksportu danego brokera i konwertuje go do ujednoliconej struktury CSV.

### Cel

Głównym celem wtyczek jest:

1. Odczytanie danych transakcyjnych z plików eksportu specyficznych dla brokera
2. Przekształcenie tych danych w ustandaryzowany format
3. Zapisanie przekształconych danych jako plik CSV, który może być wczytany przez generyczny loader i dalej procesowany

### Użycie

Każda wtyczka może być uruchomiona z linii poleceń z określonymi parametrami. Zazwyczaj wtyczki wymagają:

- Ścieżki wejściowej: Ścieżka do pliku eksportu brokera
- Ścieżki wyjściowej: Gdzie zapisać ustandaryzowany plik CSV
- Opcjonalnych parametrów: Takich jak poziom logowania

### Dostępne wtyczki

Repozytorium zawiera wtyczki dla różnych brokerów. Sprawdź dokumentację w katalogach poszczególnych wtyczek, aby uzyskać szczegółowe informacje.

### Dodawanie obsługi nowych brokerów

Jeśli Twój broker nie jest obsługiwany:

1. Możesz utworzyć nową wtyczkę, wzorując się na istniejących
2. Poprosić o wsparcie, otwierając zgłoszenie (issue) na GitHubie
3. Przesłać pull request ze swoją implementacją
