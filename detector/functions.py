import re


def atoi(text):
    return int(text) if text.isdigit() else text
# Function to split the filename into parts that are either digits or non-digits
def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]