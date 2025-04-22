import datetime
import json
import os
import uuid


def save_negotiation_log(log, folder="src/negotiation_histories"):
    """
    Saves the negotiation log to a uniquely named JSON file.

    Args:
        log (list[dict]): Full negotiation log.
        folder (str, optional): Destination folder to store the file. Defaults to "negotiation_histories".

    Returns:
        returns (str): The full path to the saved JSON file.
    """
    # Make sure folder exists
    os.makedirs(folder, exist_ok=True)

    # Get timestamp, ID, and define filepath
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]
    unique_filename = f"negotiation_{timestamp}_{short_uuid}.json"
    filepath = os.path.join(folder, unique_filename)

    # Write log to filepath
    with open(filepath, "w") as f:
        json.dump(log, f, indent=2)

    print(f"Negotiation history saved to: {filepath}")
    return filepath
