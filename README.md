
## Salary statistics for programmers in Moscow

This script provides statistics on the average salaries of programmers in Moscow using data from HeadHunter and SuperJob.

## Installation

1. Make sure you have Python installed. You can download it from [official website](https://www.python.org/downloads/).

2. Download or clone the repository:

   ```bash
   git clone https://github.com/abfalexs/Vacancies-for-programmers.git
   ```

3. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Create a `.env` file in the project root and add your SuperJob key to it:

   ```
   SECRET_KEY_SUPERJOB=your_key
   ```

## Launch

To get statistics, run the script:

```bash
python main.py
```

## Results

After executing the script, you will receive statistics on the average salary, the number of vacancies found and processed for each programming language.

## Note

The script uses the HeadHunter and SuperJob APIs to obtain data. Please note that a key from SuperJob is required to access their API.
You can get the SuperJob key from the [official website](https://api.superjob.ru/info/?from_refresh=1).
