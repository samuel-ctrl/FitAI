from datetime import datetime
import logging
import csv

# Create a logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prompt_logger")

# CSV file to store the logs
CSV_FILE = "logs.csv"


# Initialize the CSV with headers if the file doesn't exist
def initialize_csv():
    try:
        with open(CSV_FILE, "x", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Time", "Prompt", "Response"])
    except FileExistsError:
        pass  # The file already exists


# Function to log data to CSV
def log_to_csv(prompt: str, response: str):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([current_time, prompt, response])

