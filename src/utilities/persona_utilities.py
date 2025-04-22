import os
import json
import datetime
import random
import uuid

from typing import Any, Optional
from openai import OpenAI

from resources.business_persona import BusinessPersona


def load_random_personas(
    folder: str = "generated_personas",
) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
    """
    Attempts to load random acquirer and target business personas from a JSON file in `folder`, otherwise returns empty personas.

    Args:
        folder (str, optional): The path to the folder containing previously saved persona JSON files.
                                Defaults to "generated_personas".

    Returns:
        returns (tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]): A tuple containing the loaded acquirer and target personas.
        Each element is either a dictionary representing the persona (if successfully loaded), or None if loading failed.
    """
    # Return empty personas if folder DNE
    if not os.path.exists(folder):
        return None, None

    # Get list of files in personas folder
    files = [f for f in os.listdir(folder) if f.endswith(".json")]

    # Return empty personas if no persona files exist
    if not files:
        return None, None

    # Randomly choose file and build filepath
    chosen_file = random.choice(files)
    filepath = os.path.join(folder, chosen_file)

    # Load personas from selected file
    loaded_acquirer, loaded_target = load_personas_from_file(filepath)

    # Print sucess and personas' descriptions if personas are not empty
    if loaded_acquirer and loaded_target:
        print(f"\nPersonas successfully loaded from {filepath}:")
        print("- ACQUIRER:", loaded_acquirer["business_descr"][0])
        print("- TARGET:", loaded_target["business_descr"][0], "\n")

    return loaded_acquirer, loaded_target


def load_personas_from_file(
    filepath: str,
) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
    """
    Loads acquirer and target personas from a specified filepath.

    Args:
        filepath (str): The filepath to load personas from.

    Returns:
        returns (tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]): A tuple containing the loaded acquirer and target personas.
        Each element is either a dictionary representing the persona (if successfully loaded), or None if the file is not found.
    """
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data.get("acquirer"), data.get("target")
    except FileNotFoundError:
        return None, None


def create_personas(
    acquiring_countries: list,
    target_countries: list,
    openAI_client: OpenAI,
    folder: str = "src/generated_personas",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Creates and saves new acquirer-target personas with random countries in ONE unique file in specified folder.

    Args:
        acquiring_countries (list[str]): A list of country names to randomly select from for the acquiring business persona.
        target_countries (list[str]): A list of country names to randomly select from for the target business persona.
        openAI_client (OpenAI): An instance of the OpenAI client used to access LLM via API.
        folder (str, optional): The folder path where the generated persona file will be saved. Defaults to "generated_personas".

    Returns:
        returns (tuple[dict[str, Any], dict[str, Any]]): A tuple containing two dictionaries — the generated acquirer persona and target persona.
    """
    # Randomly choose an acquiring and target country for businesses
    acquirer_country = random.choice(acquiring_countries)
    target_country = random.choice(target_countries)

    # Generate two sets of personas (one for acquirer and one for target business)
    acquirer_persona = BusinessPersona.generate(
        "acquirer", acquirer_country, openAI_client
    )
    target_persona = BusinessPersona.generate(
        "target",
        target_country,
        openAI_client,
        acquiring_business_descr=acquirer_persona["business_descr"][0],
        acquiring_business_financal_info=acquirer_persona["financial_info"][0],
    )

    # Save generated personas
    filepath = save_personas(
        acquirer_persona=acquirer_persona, target_persona=target_persona, folder=folder
    )
    print(f"New personas created and saved to: {filepath}\n")

    return acquirer_persona, target_persona


def save_personas(
    acquirer_persona: dict[str, Any],
    target_persona: dict[str, Any],
    folder: str,
) -> str:
    """
    Saves the given acquirer and target business personas to a single JSON file in specified folder.

    Args:
        acquirer_persona (dict[str, Any]): The dictionary representing the acquirer's persona.
        target_persona (dict[str, Any]): The dictionary representing the target's persona.
        folder (str): The path to the folder where the JSON file will be saved.

    Returns:
        returns (str): The file path where the personas were saved.
    """
    # Check if either persona is empty and print warning if so
    if not acquirer_persona or not target_persona:
        print("Warning: Either acquirer or target persona is empty.")

    # Ensure directory exists
    os.makedirs(folder, exist_ok=True)

    # Get current timestamp and short ID for naming file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]

    # Create unique filename and define filepath
    unique_filename = f"personas_{timestamp}_{short_uuid}.json"
    filepath = os.path.join(folder, unique_filename)

    # Create object to store personas
    data = {}
    data["acquirer"] = acquirer_persona
    data["target"] = target_persona

    # Save object as json to filepath
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    return filepath
