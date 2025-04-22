import os

from openai import OpenAI
from dotenv import load_dotenv

from resources.negotiation_session import NegotiationSession
from utilities.persona_utilities import (
    create_personas,
    load_random_personas,
)
from utilities.negotiation_utilities import save_negotiation_log


def main():
    # Load local env variables
    load_dotenv()

    # Initialize OpenAI client instance used for accessing LLM
    openAI_client = OpenAI(
        base_url="https://api.inference.net/v1",
        api_key=os.getenv("INFERENCE_API_KEY"),
    )

    # List of typical acquiring and target business countries of origin in negotiation
    acquiring_countries = ["US", "UK", "France", "Japan", "Canada"]
    target_countries = ["Africa", "Russia", "Singapore", "China", "India", "Brazil"]

    # Either randomly load existing personas or generate new ones
    load_create_personas_choice = (
        input("Load existing personas (L) or create new (N)? [L/N]: ").strip().lower()
    )
    if load_create_personas_choice.startswith("l"):
        acquirer_persona, target_persona = load_random_personas()
        if not acquirer_persona or not target_persona:
            print("No valid personas found. Creating new ones...")
            acquirer_persona, target_persona = create_personas(
                acquiring_countries,
                target_countries,
                openAI_client,
            )
    else:
        acquirer_persona, target_persona = create_personas(
            acquiring_countries, target_countries, openAI_client
        )

    # After loading or generating personas, optionally run an acquisition negotiation
    run_negotiation_choice = (
        input("Run negotiation session now? (Y/N): ").strip().lower()
    )
    if run_negotiation_choice.startswith("y"):
        # Final negotiation log gets returned and saved
        negotiation_log = NegotiationSession.run(
            acquirer=acquirer_persona,
            target=target_persona,
            openAI_client=openAI_client,
        )
        save_negotiation_log(negotiation_log)
    else:
        print("Skipping negotiation session.")


if __name__ == "__main__":
    main()
