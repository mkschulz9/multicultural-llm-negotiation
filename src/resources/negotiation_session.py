import json
import re
from typing import Any, Optional

from openai import OpenAI
from utilities.llm_utilities import prompt_llm_with_retry


class NegotiationSession:
    """
    A class to simulate an international business acquisition negotiation session between two companies represented by LLM-generated personas.
    """

    def __init__(
        self,
        acquirer: dict[str, Any],
        target: dict[str, Any],
        openAI_client: OpenAI,
        num_rounds: int,
        stream_content: bool,
    ):
        self.acquirer = acquirer
        self.target = target
        self.openAI_client = openAI_client
        self.num_rounds = num_rounds
        self.stream_content = stream_content

        # Create system prompts for each side
        self.acquirer_system_message = self._create_system_prompt(
            self.acquirer, self.target
        )
        self.target_system_message = self._create_system_prompt(
            self.target, self.acquirer
        )

    def _run_negotiation(self) -> list[dict[str, Any]]:
        """
        High-level function that executes a full negotiation between acquirer and target for up to `num_rounds` rounds.

        Returns:
            returns (list[dict[str, Any]]): A complete log of the negotiation, including:
                - role (str): Who responded.
                - message (str): The LLM's full response.
                - reasoning (str): Internal LLM reasoning.
                - query (str): The LLM prompt.
                - negotiation_state (str): Either 'pending' or 'complete'.
                - term_sheet_snapshot (dict[str, Any]): Latest cumulative deal terms.
        """
        print(f"\nRUNNING NEGOTIATION\n{"*" * 50}")

        # Get acquiring and target company names from their descriptions and save in list
        acquirer_name = self._extract_company_name(self.acquirer["business_descr"][0])
        target_name = self._extract_company_name(self.target["business_descr"][0])
        company_names = [acquirer_name, target_name]

        # Print company roles in negotiation and their names
        print(f"{self.acquirer['role_in_acquisition'].upper()}: {acquirer_name}")
        print(f"{self.target['role_in_acquisition'].upper()}: {target_name}")

        # Init objects for storing negotiation details
        negotiation_history = []
        negotiation_log = []
        current_term_sheet = {}

        # Store business' information
        participants = [
            (self.acquirer, self.acquirer_system_message),
            (self.target, self.target_system_message),
        ]

        # Used for tracking negotiation states (pending or complete) and early stopping
        last_negotiation_state = None
        last_role_in_acquisition = None
        stop_negotiation = False

        # Negotiation loop
        for round_index in range(1, self.num_rounds + 1):
            print(f"\n{"="*50}\nRound {round_index}/{self.num_rounds}\n{"="*50}")

            # Allow each business to negotiate
            for i, (party, system_msg) in enumerate(participants):
                # Print which company is negotiating
                company_name = company_names[0] if i == 0 else company_names[1]
                role_in_acquisition = party["role_in_acquisition"]
                print(
                    f"\n{role_in_acquisition.upper()} ({company_name})"
                    if role_in_acquisition == "target"
                    else f"{role_in_acquisition.upper()} ({company_name})"
                )

                # Get messages to pass to LLM
                messages = self._get_messages(system_msg, negotiation_history)

                # Get LLM response (negotiators response), its reasoning, and the query
                response, reasoning, query = prompt_llm_with_retry(
                    messages, self.openAI_client, stream_content=self.stream_content
                )

                # Extract terms json object from LLM response (if present) and update terms if it is not empty
                new_terms = self._extract_term_sheet_from_response(response)
                if new_terms:
                    current_term_sheet.update(new_terms)

                # Extract negotiation state from response
                negotiation_state = self._extract_negotiation_state(response)

                # Checks if both company's consecutively returned negotiation state as complete
                if (
                    negotiation_state == "complete"
                    and last_negotiation_state == "complete"
                    and last_role_in_acquisition != role_in_acquisition
                ):
                    stop_negotiation = True

                # Update last state and role
                last_negotiation_state = negotiation_state
                last_role_in_acquisition = role_in_acquisition

                # Update negotiation history and log
                negotiation_history.append(
                    {"role": role_in_acquisition, "message": response}
                )
                negotiation_log.append(
                    {
                        "role": role_in_acquisition,
                        "message": response,
                        "reasoning": reasoning,
                        "query": query,
                        "negotiation_state": negotiation_state,
                        "term_sheet_snapshot": current_term_sheet.copy(),
                    }
                )

                # Break out of inner loop if negotiations have ended
                if stop_negotiation:
                    break

            # Break out of outer loop if negotiations have ended
            if stop_negotiation:
                print(
                    "\nBoth parties have declared the negotiation complete. Ending early."
                )
                break

        print(f"{"*" * 50}\nNEGOTIATION COMPLETE")

        # Convert last term sheet into str and print
        current_term_sheet_str = "\n".join(
            f"{key.upper()}: {value}" for key, value in current_term_sheet.items()
        )
        print(f"\nLast Term Sheet:\n{current_term_sheet_str}\n")

        return negotiation_log

    def _get_messages(
        self, system_message: str, negotiation_history: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """
        Combines the system and user prompts into an OpenAI messages structure.

        Args:
            system_message (str): System-level instructions for the LLM.
            negotiation_history (list[dict[str, str]]): List of messages so far in the negotiation.

        Returns:
            returns (list[dict[str, str]]): Formatted message list suitable for OpenAI's chat API.
        """
        # Retrieve user prompt
        user_prompt = self._create_user_prompt(negotiation_history)

        # Build and return messages
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
        ]

    def _create_system_prompt(
        self, company_persona: dict[str, Any], other_company_persona: dict[str, Any]
    ) -> str:
        """
        Generates a system prompt tailored to a company's persona.

        Args:
            company_persona (dict[str, Any]): The company initiating the message.
            other_company_persona (dict[str, Any]): The opposing company's persona.

        Returns:
            returns (str): A full system prompt describing the company's role, style, goals, and instructions.
        """
        # Build and return system message
        return f"""You are a representative in an international business acquisition negotiation. 
Your role: strongly advocate for your company's best interests and finalize a binding acquisition agreement.

Your Company:
- Role in the Acquisition: {company_persona['role_in_acquisition'].upper()}
- Location: {company_persona['country_based']}
- Company Description: {company_persona['business_descr'][0]}
- Financial Info: {company_persona["financial_info"][0]}
- Cultural Profile: {company_persona['cultural_profile'][0]}
- Authority Dynamics: {company_persona['authority_dynamics'][0]}
- Unspoken Interests: {company_persona['unspoken_interests'][0]}

Counterparty (Other Company):
- Role in the Acquisition: {other_company_persona['role_in_acquisition'].upper()}
- Location: {other_company_persona['country_based']}
- Description: {other_company_persona['business_descr'][0]}
- Financial Info: {other_company_persona["financial_info"][0]}

Instructions
1. Deal Terms: Always propose or respond with concrete terms – e.g., valuation, payment structure (cash vs. stock, earn-outs), synergy targets, timelines for due diligence, etc.
2. Push for Advantage: Try to secure the best possible outcome for your company.
3. Hidden Agenda: Weave in your company's unspoken interests without explicitly stating them as "hidden."
4. Negotiate: Ask for clarifications, counter suboptimal terms, highlight concerns (like potential risks or synergy limits).
5. Response Format: Provide only official negotiation statements (no salutations, sign-offs, or extraneous text).
6. Professional Tone: Keep it concise and direct, reflecting your company's communication style.
"""

    def _create_user_prompt(self, negotiation_history: list[dict[str, str]]) -> str:
        """
        Generates a user prompt based on the current negotiation history.

        Args:
            negotiation_history (list[dict[str, str]]): List of all previous negotiation exchanges.

        Returns:
            returns (str): Formatted user message to prompt the next LLM response.
        """
        # Build prompt with negotitation history prompt (if history is present)
        if negotiation_history:
            history_str = "\n".join(
                f"{entry['role'].upper()}:\n{entry['message']}"
                for entry in negotiation_history
            )
            prompt = f"""Below is the ongoing negotiation history between your company and the other party. 
Continue the conversation by providing your company's official negotiation response. 

Focus on these M&A deal points:
- Valuation (provide a numeric figure or multiple, e.g. $XX million, X times revenue, etc.)
- Payment Structure (cash, stock, earn-out terms, etc.)
- Key Synergies and Potential Friction (where do you see alignment or conflict?)
- Due Diligence / Timeline (how long for diligence, when to sign definitive agreements?)
- Any Pending Requests from the other side not yet addressed

Remember:
- Push for your company's best interests
- Reflect your company's culture, authority dynamics, and unspoken interests
- Do not include salutations or sign-offs
- Maintain a professional, concise tone

If you propose or change any terms, please append an updated term sheet in **JSON** at the end of your response. 
Use a structure like:
```json
{{
  "valuation": "...",
  "payment_structure": "...",
  "earn_out": "...",
  "due_diligence_timeline": "...",
  "other_key_terms": "...",
  ...
}}
```
If you do not propose any changes, you can reaffirm existing terms or omit the JSON.

Finally, be sure to end with:

Company Negotiation State: [pending or complete].

- pending: your company still wishes to negotiate the terms
- complete: your company is satified and will agree to the terms

Negotiation History: 
{history_str}
"""
        # Build prompt without negotiation history (i.e., Acquiring company begins negotiations)
        else:
            prompt = """No prior negotiation history exists. 
Begin the negotiation to acquire the TARGET company by providing your initial official statement. 

Focus on these M&A deal points:
- Valuation (provide a numeric figure or multiple, e.g. $XX million, X times revenue, etc.)
- Payment Structure (cash, stock, earn-out terms, etc.)
- Key Synergies and Potential Friction (where do you see alignment or conflict?)
- Due Diligence / Timeline (how long for diligence, when to sign definitive agreements?)

Remember:
- Push for your company's best interests
- Reflect your company's culture, authority dynamics, and unspoken interests
- Do not include salutations or sign-offs
- Maintain a professional, concise tone

Please append a term sheet in **JSON** at the end of your response. 
Use a structure like:
```json
{{
  "valuation": "...",
  "payment_structure": "...",
  "earn_out": "...",
  "due_diligence_timeline": "...",
  "other_key_terms": "...",
  ...
}}
```

Finally, be sure to end with:

Company Negotiation State: [pending or complete].

- pending: your company still wishes to negotiate the terms
- complete: your company is satified and will agree to the terms
"""
        return prompt

    def _extract_term_sheet_from_response(
        self,
        response_text: str,
    ) -> Optional[dict[str, str]]:
        """
        Extracts a JSON-formatted term sheet from an LLM response string.

        Args:
            response_text (str): Full response text generated by the LLM.

        Returns:
            returns (Optional[dict[str, str]]): Parsed JSON object as a dictionary if found and valid; otherwise, returns None.
        """
        # Look for '```json` string in response
        match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, flags=re.DOTALL)

        # If not found return None
        if not match:
            return None

        # Attempt to parse json_str into Python dict, return None if error occurs
        json_str = match.group(1)
        try:
            parsed = json.loads(json_str)
            return parsed
        except json.JSONDecodeError:
            return None

    def _extract_negotiation_state(self, response_text: str) -> Optional[str]:
        """
        Extracts the current negotiation state from a formatted LLM response (pending or complete)

        Args:
            response_text (str): The full LLM response text.

        Returns:
            returns: (Optional[str]): The negotiation state, either "pending" or "complete", in lowercase. Returns None if no valid state is found.
        """
        # Remove all '*' (Markdown bold)
        text = response_text.replace("*", "")

        # Look for “Company Negotiation State” then optional colon or bracket, then capture pending or complete (with or without surrounding [ ])
        pattern = r"""
            (?:Company\s+)?Negotiation\s+State    # optional “Company ” prefix
            \s*[:\[]?                             # optional ':' or '['
            \s*                                   # any whitespace
            (pending|complete)                    # capture either pending or complete
            \]?                                   # optional closing ']'
        """

        # Look for matching patterns in text and return if found else return None
        match = re.search(pattern, text, flags=re.IGNORECASE | re.VERBOSE)
        if match:
            return match.group(1).lower()
        return None

    def _extract_company_name(self, description: str) -> str:
        """
        Extracts the company name from a business description.

        Args:
            description (str): The full business description.

        Returns:
            str: The extracted company name.
        """
        # Remove markdown formatting (e.g., **text**)
        cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", description).strip()

        # Regex pattern to capture the company name at the beginning
        pattern = re.compile(
            r"^(.+?)\s*(?:(?:is a)|(?:, based)|(?:headquartered))", flags=re.IGNORECASE
        )

        # Find and return non-empty match
        match = pattern.search(cleaned)
        if match:
            return match.group(1).strip()
        else:
            # Fallback: use text up to the first period
            fallback = cleaned.split(".")[0].strip()
            return fallback

    @classmethod
    def run(
        cls,
        acquirer: dict[str, Any],
        target: dict[str, Any],
        openAI_client: OpenAI,
        num_rounds: int = 10,
        stream_content: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Class method for running a negotiation session.

        Args:
            acquirer (dict[str, Any]): Acquirer company persona.
            target (dict[str, Any]): Target company persona.
            openAI_client (OpenAI): OpenAI client for communication.
            num_rounds (int, optional): Max number of negotiation rounds. Defaults to 10.
            stream_content (bool, optional): If True, streams the LLM response token-by-token. Defaults to True.

        Returns:
            returns (list[dict[str, Any]]): Full log of negotiation exchanges and terms.
        """
        instance = cls(acquirer, target, openAI_client, num_rounds, stream_content)
        return instance._run_negotiation()
