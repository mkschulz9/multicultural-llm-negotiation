# LLM-Based International M&A Negotiation Simulator (Multicultural Negotiation)

This project simulates international **business acquisition negotiations** between two AI-generated company personas using a large language model (LLM). It combines realistic company modeling (cultural norms, financials, hidden motives) with interactive negotiation rounds where each company advocates for its interests.

---

## Features

- **Persona Generation**: Automatically creates realistic acquirer and target company profiles, including:
  - Business descriptions  
  - Cultural norms  
  - Authority structures  
  - Financial summaries  
  - Hidden agendas  

- **LLM-Powered Negotiation**: Each company is guided by an LLM and negotiates:
  - Valuation  
  - Payment structure  
  - Synergies & friction  
  - Timeline for due diligence  
  - Term sheets in JSON  

- **Replayability**: Load past personas or generate new ones for each run. All negotiations are logged and saved for future analysis.

---

## Requirements

- An API key for [Inference API](https://inference.net) or compatible OpenAI-style endpoint.

### Install dependencies

- Create and activate virtual environment if desired. Then install project dependencies by running:

```bash
pip install -r requirements.txt
```

---

## Setup

1. **Create a `.env` file** in the root directory:

   ```env
   INFERENCE_API_KEY=your_api_key_here
   ```

## Running the Simulator

- Move inside the `src` folder and run:

```bash
python main.py
```

You will be prompted to:

1. **Load or generate** new company personas  
2. **Start a negotiation session** between the acquirer and target personas  
3. View the negotiation in real time and receive a term sheet at the end  

---

## Output

After a successful negotiation session:

- The **full negotiation log** (with term sheets and reasoning) is saved to a JSON file under:

  ```
  src/negotiation_histories/
  ```

---

## Example Use Cases

- Simulating M&A dynamics across different cultural or geographic settings  
- Stress-testing acquisition scenarios with AI agents  
- Business education and negotiation training tools  
- LLM reasoning evaluation through structured dialogue and goal-seeking behavior  

---

## Notes

- The simulation relies on consistent formatting from the LLM (e.g., proper JSON and negotiation state lines). It's robust, but not bulletproof.
- If a model times out or fails to produce the first token in time, Inference.net or OpenAI Chat API might be down.

---

## Contact

For improvements, bugs, or ideas, feel free to open an issue or reach out!
