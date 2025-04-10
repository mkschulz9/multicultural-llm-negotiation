from typing import Any, Optional

from openai import OpenAI
from utilities.llm_utilities import prompt_llm_with_retry


class BusinessPersona:
    """
    A class to generate a business persona with realistic details, including cultural profile, authority dynamics, hidden interests, and financial info to facilitate M&A negotiations.
    """

    def __init__(
        self,
        role_in_acquisition: str,
        country_based: str,
        openAI_client: OpenAI,
        acquiring_business_descr: Optional[str],
        acquiring_business_financal_info: Optional[str],
        stream_content: bool,
    ):
        self.role_in_acquisition = role_in_acquisition
        self.country_based = country_based
        self.openAI_client = openAI_client
        self.acquiring_business_descr = acquiring_business_descr
        self.aquiring_business_financal_info = acquiring_business_financal_info
        self.stream_content = stream_content
        self.system_message = {
            "role": "system",
            "content": """You are a business strategy expert and a professional writer specialized in generating realistic company personas for M&A negotiations. 
Your task is to produce clear, concise, and well-structured responses that strictly adhere to the prompt instructions. 
Make sure to use the exact sentence count and format requested, and maintain a tone that is both professional and direct. 
Avoid extraneous commentary and ensure that each response contains only the necessary details.
""",
        }

    def _generate_business_persona(self) -> dict[str, Any]:
        """
        High-level function that controls persona construction.

        Args:
            None

        Returns:
            returns (dict[str, Any]): A dictionary containing generated business persona.
        """
        print(
            f"\nGENERATING {self.role_in_acquisition.upper()}'S BUSINESS PERSONA\n{'*'*50}"
        )

        # Begin building persona object
        persona = {}

        # Save company's role in negotiation and country based (passed parameters)
        persona["role_in_acquisition"] = self.role_in_acquisition
        persona["country_based"] = self.country_based

        # Generate business description
        persona["business_descr"] = self._get_business_description(
            self.acquiring_business_descr
        )

        # Generate business's cultural profile & authority dynamics
        persona["cultural_profile"] = self._get_cultural_profile(persona)
        persona["authority_dynamics"] = self._get_authority_dynamics(persona)

        # Generate financial info
        persona["financial_info"] = self._get_financial_info(
            persona, self.aquiring_business_financal_info
        )

        # Generate unspoken interests (hidden agenda)
        persona["unspoken_interests"] = self._get_unspoken_interests(persona)

        print("*" * 50)
        return persona

    def _get_business_description(
        self, aquiring_business_descr: Optional[str]
    ) -> tuple[str, str, str]:
        """
        Generates business description.

        Args:
            aquiring_business_descr (str, optional): Acquirer description to generate plausible target business description if generating target.

        Returns:
            returns (tuple[str, str, str]): A string with business description, LLM reasoning, and original user query.
        """
        print("Generating business description...")

        # Content to prompt LLM with (if generating target description)
        if aquiring_business_descr:
            prompt = f"""In exactly 2–3 sentences, create a brief description of a {self.country_based}-based company that would be a likely acquisition target for the acquiring business described below. 
The target company should be complementary in purpose or capability, but not identical. 
Use a realistic company name and a typical industry for the region for the target company. 
Only describe the target company itself.

Acquiring Business Description:
- {aquiring_business_descr}
"""
        # Otherwise prompt LLM with to generate acquirer description
        else:
            prompt = f"""In exactly 2–3 sentences, create a brief description of a {self.country_based}-based company. 
Use a realistic company name and a typical industry for the region for the company. 
Only describe the company itself.
"""
        # Construct OpenAI-style messages
        messages = [self.system_message, {"role": "user", "content": prompt}]

        # Prompt LLM
        return prompt_llm_with_retry(
            messages, self.openAI_client, stream_content=self.stream_content
        )

    def _get_cultural_profile(self, persona) -> tuple[str, str, str]:
        """
        Generates a cultural profile for a business (i.e., communication style, negotiation behavior, and business etiquette).

        Args:
            persona (dict[str, Any]): Current business persona.

        Returns:
            returns (tuple[str, str, str]): A string with cultural profile, LLM reasoning, and original user query.
        """
        print("\nGenerating cultural profile...")

        # Build prompt
        prompt = f"""Based on the business description below, write a cultural profile for the company in exactly 2–3 sentences. 
Focus on the company’s communication style, negotiation behavior, and business etiquette. 
Only describe the company's cultural profile.

Business Description:
- Country based: {persona["country_based"]}
- Business description: {persona["business_descr"][0]}
"""
        # Build messages and prompt LLM
        messages = [self.system_message, {"role": "user", "content": prompt}]
        return prompt_llm_with_retry(
            messages, self.openAI_client, stream_content=self.stream_content
        )

    def _get_authority_dynamics(self, persona) -> tuple[str, str, str]:
        """
        Generates authority dynamics for a business (i.e., how decision-making power is distributed when negotiating business deals).

        Args:
            persona (dict[str, Any]): Current business persona.

        Returns:
            returns (tuple[str, str, str]): A string with authority dynamics, LLM reasoning, and original user query.
        """
        print("\nGenerating authority dynamics...")

        # Build prompt
        prompt = f"""Based on the business description below, describe the company's authority dynamics in exactly 2–3 sentences. 
Specifically focus on how decision-making power is distributed when negotiating business deals — for example, whether representatives have full autonomy, require management approval, or follow a chain of command.

Business Description:
- Role in acquisition: {persona["role_in_acquisition"]}
- Country based: {persona["country_based"]}
- Business description: {persona["business_descr"][0]}
- Cultural profile: {persona["cultural_profile"][0]}
"""
        # Build messages and prompt LLM
        messages = [self.system_message, {"role": "user", "content": prompt}]
        return prompt_llm_with_retry(
            messages, self.openAI_client, stream_content=self.stream_content
        )

    def _get_financial_info(
        self, persona, acquiring_business_financal_info: Optional[str]
    ) -> tuple[str, str, str]:
        """
        Generates financial info for business (i.e., typical annual revenue, profit margin, and mention a general valuation range, etc.) based on whether they are the acquirer or target.

        Args:
            persona (dict[str, Any]): Current business persona.
            acquiring_business_financal_info (str, optional): Acquirer financial info used to generate plausible target business financial info if generating target.

        Returns:
            returns (tuple[str, str, str]): A string with financial info for company, LLM reasoning, and original user query.
        """
        print("\nGenerating financial info...")

        # Extract business's role and build prompt accordingly
        role = persona["role_in_acquisition"].lower()
        if role == "acquirer":
            # Acquirer prompt
            prompt = f"""In exactly 1–2 sentences, create sample financial info for the business described below. 
Include typical annual revenue, profit margin, and valuation range.
This company is large enough to acquire other companies - its financial info should reflect this ability.

Business Description: 
- {persona["business_descr"][0]}. 
"""
        else:
            # Target prompt
            prompt = f"""In exactly 1–2 sentences, generate plausible financial information for the business described below, ensuring it clearly represents a smaller acquisition target rather than a large acquiring company. 
Include typical annual revenue, profit margin, and valuation range. 

Business Description: 
- {persona["business_descr"][0]}

Reference – Acquiring Company’s Financial Info:
- {acquiring_business_financal_info}
"""
        # Build messages and prompt LLM
        messages = [self.system_message, {"role": "user", "content": prompt}]
        return prompt_llm_with_retry(
            messages, self.openAI_client, stream_content=self.stream_content
        )

    def _get_unspoken_interests(self, persona) -> tuple[str, str, str]:
        """
        Generates unspoken interests for business (i.e., information they might withold in a business acquisition deal)

        Args:
            persona (dict[str, Any]): Current business persona.

        Returns:
            returns (tuple[str, str, str]): A string with unspoken interests for company, LLM reasoning, and original user query.
        """
        print("\nGenerating unspoken interests...")

        # Build prompt
        content = f"""Based on the business description below, create a hidden agenda this company will have when participating in an international business acquisition deal. 
The response should be 2-3 sentences. 
Be direct and confident. 
Do not restate information from the cultural profile or authority dynamics unless it ties directly to the hidden motivation.

Business Persona:
- Role in acquisition: {persona["role_in_acquisition"]}
- Country based: {persona["country_based"]}
- Business description: {persona["business_descr"][0]}
- Cultural profile: {persona["cultural_profile"][0]}
- Authority dynamics: {persona["authority_dynamics"][0]}
- Financial info: {persona["financial_info"][0]}
"""
        # Build messages and prompt LLM
        messages = [self.system_message, {"role": "user", "content": content}]
        return prompt_llm_with_retry(
            messages, self.openAI_client, stream_content=self.stream_content
        )

    @classmethod
    def generate(
        cls,
        role_in_acquisition: str,
        country_based: str,
        openAI_client,
        acquiring_business_descr: Optional[str] = None,
        acquiring_business_financal_info: Optional[str] = None,
        stream_content: bool = True,
    ) -> dict[str, Any]:
        """
        Class method to generate a complete business persona dictionary.

        Args:
            role_in_acquisition (str): Either "acquirer" or "target".
            country_based (str): Country the business is based in.
            openAI_client (OpenAI): OpenAI client to use for generation.
            acquiring_business_descr (str, optional): Used only when generating a target persona.
            acquiring_business_financal_info (str, optional): Acquirer financial info used to generate plausible target business financial info if generating target.
            stream_content (bool, optional): If True, streams the LLM response token-by-token. Defaults to True.

        Returns:
            returns (dict[str, Any]): A dictionary representing the generated persona.
        """
        instance = cls(
            role_in_acquisition,
            country_based,
            openAI_client,
            acquiring_business_descr,
            acquiring_business_financal_info,
            stream_content,
        )
        return instance._generate_business_persona()
