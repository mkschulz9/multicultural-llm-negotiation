# LLM-Based International M&A Negotiation Simulator (Multicultural Negotiation)

This project simulates international **business acquisition negotiations** between two AI-generated company personas using a large language model (LLM).
It combines realistic company personas, complete with cultural norms, financials, and hidden motives, with interactive negotiation rounds where each company advocates for its interests.
Example personas and negotiations can be visualized by rendering any HTML file in the `src/visualize_negotiations` folder using an online HTML renderer.

An OpenAI client from the OpenAI Python client library is used to access a language model via the `chat.completions.create()` endpoint. Specifically, DeepSeek's `DeepSeek-R1-Distill-Llama-70B` is used and accessed through a third-party inference API hosted by Inference.net.

Continue reading for more information on how to run the code, metrics used to evaluate negotiations, an analysis of the results, and potential future work.

## Running the Code

1. **Install dependencies**: install the project's dependencies by running the commnd below in the project's root directory. Recommended: setup a virtual environment and activate it before installing the dependencies.

    ```bash
    pip install -r requirements.txt
    ```

2. **Setup API key**: an API key from [Inference.net](https://inference.net) is needed to run LLM inferences. Visit the link and follow the directions in "Get Started" to create an account and generate a key.

3. **Environment file**: create a `.env` file in the root directory and populate it with your inference key generated in step 2.

   ```env
   INFERENCE_API_KEY=your_api_key_here
   ```

4. **Run code**: move inside the `src` folder and run the command below to run the persona generation and negotiation code.

   ```bash
   python main.py
   ```

   You will be prompted to:

    1. **Load or generate company personas**: you can decide whether to generate new acquirer-target personas or reuse a random, exisiting persona pair in the `generated_personas` folder.
    2. **Start negotiation session**: you can then run a negotiation simulation using the newly generated persona or existing persona pair.
    3. **Persona and negotiation saving**: after the negotiation terminates, newly generated persona pairs will be saved in the `generated_personas` folder and the full negotiation log will be saved in the `negotiation_histories` folder.
    4. **Persona and negotiation visualization**: running the `visualize_negotiations/generate_negotiation_html` file will generate HTML files for each negotiation session present in the `generated_personas` folder. These HTML file can then be ran on an online HTML viewer to visualize the personas and negotiations in a user friendly interface.

## Evaluation Metrics

The completed negotiations are manually evaluated on five axes. Scores fall in the [0, 1] range (except T, which is categorical).

| Metric | Purpose | Formula | Notes |
|--------|---------|---------|---------|
| **Persona-Cue Fidelity (F)** | Measures how consistently each negotiation statement remains aligned with the assigned company persona, such as cultural profile, authority structure, financial strategy, and hidden agendas. | F = Number of cue-positive negotiation turns / Total negotiation turns | "Cue-positive" means the negotiation turn explicitly reflects or reinforces the predefined company persona elements. |
| **Reasoning & Planning Depth (D)** | Evaluates the quality and complexity of explicit reasoning in each negotiation turn. This includes quantitative logic, justification of positions, and forward-looking planning. | D = Sum of points across all turns / 3 x Total turns | Each turn can earn up to 3 points: Quantitative Logic (1 point): Explicitly includes numeric or financial reasoning. Multi-step Justification (1 point): Explains positions or counteroffers using multiple logical steps. Forward Planning (1 point): Anticipates future negotiation moves, consequences, or explicitly plans future negotiation steps. |
| **Reciprocity (R)** | Measures how proportionally responsive each party is to the concessions or adjustments made by the other side, particularly in headline economics (valuation and cash/stock payment structure). | For each negotiation turn i, r(i) is calculated as r(i) = abs(Δ Acquirer Offer(i)) / abs(Δ Target Offer (i)), R = mean(r(i)) across all turns | Δ Offer refers to changes made between consecutive negotiation turns. Reciprocity is highest when both sides respond with concessions of roughly equal proportional magnitude. A value closer to 1.0 indicates ideal reciprocity (balanced concessions), while values significantly above or below indicate imbalance or unilateral concession patterns. |
| **Tone Stability (T)** | Tracks the emotional stability or volatility of negotiation language throughout the session. Stable, positive tone suggests cooperative and productive interactions. | If sentiment standard deviation (𝜎) < 0.10 and sentiment slope is non-negative (≥ 0), T = "stable-positive". Otherwise, T = "variable". | Performed on negotiation text each turn. Sentiment standard deviation (𝜎) and slope (trend) are precomputed. |
| **Total Turns (N)** | The total number of turns in a negotiation gives an idea of the negotiation length. | N/A | N/A |

## Results from 5 negotiation simulations (saved in `src/negotiation_histories` folder)

| Negotiation Index | Acquirer ↔ Target (Country) | Persona-Cue Fidelity (F) | Reasoning & Planning Depth (D) | Reciprocity (R) | Tone Stability (T) | Total Turns (N) |
|----|-------------------|----------|-------|-------------|------|--------|
| 0 | Northern Timber Corp. (Canada) ↔ GreenPak Solutions Pte. Ltd. (Singapore) | 1.0 | 0.814 | 0.58 | stable-positive | 9 |
| 1 | Midwest Steel Solutions (U.S.) ↔ Mumbai Steel Engineering Pvt. Ltd. (India) | 1.0 | 0.958 | 0.56 | stable-positive | 16 |
| 2 | True North Timber Co. (Canada) ↔ Verde Madera Industries (Brazil) | 1.0 | 0.958 | 0.55 | stable-positive | 8 |
| 3 | AéroTech France S.A. (France) ↔ AgriTech Brasil Sistemas S.A. (Brazil) | 1.0 | 0.927 | 0.38 | stable-positive | 9 |
| 4 | Northern Timber Resources Inc. (Canada) ↔ GreenWood Solutions Pvt. Ltd. (India) | 1.0 | 1.0 | 1.0 | stable positive | 4 |

**Averages**  

- Persona-Cue Fidelity (F): **1**
- Reasoning & Planning Depth (D): **0.931**
- Reciprocity (R): **0.614**
- Tone Stability (T): **stable-positive**
- Total Turns (N): **9.2**

## Negotiation Analysis

1. **Perfect Persona Consistency (F = 1.00)**

    The LLM never strayed from the defined company personas—every turn reinforced the cultural, strategic, and authority cues. This suggests that the prompting and system-level guidance effectively anchored the model’s responses in each party’s identity.

2. **Strong Reasoning & Planning (D ≈ 0.93)**

    With an average depth score above 0.9, the model routinely: incorporated quantitative logic (e.g. multiples, percentages), laid out multi-step justifications, and anticipated future moves (earn-outs, committees, timelines).

3. **Moderate Reciprocity (R ≈ 0.61)**

   A mean ratio of ~0.6 shows that the acquirer’s concessions averaged just 60% of the target’s, meaning the acquirer secured the more favorable terms, which makes sense since the acquirer has more leverage in the negotiation.

4. **Consistently Cooperative Tone (T = stable-positive)**

    Across all sessions the sentiment stayed upbeat, collaborative, and low-volatility. This “stable-positive” profile is ideal for negotiations that aim to build trust and long-term partnerships.

5. **Concise Yet Substantive Dialogues (N ≈ 9.2 turns)**

    Around nine exchanges per deal strikes a balance between brevity and thoroughness: enough back-and-forth to negotiate details without dragging the conversation out.

Overall, the LLM generated responses in the negotiation sessions were perfectly persona-aligned, demonstrated high-quality reasoning and proactive planning, maintained a consistently cooperative tone, and facilitated reasonably balanced concessions within concise dialogues.

## Future Work

There are several promising directions for future work. One extension introduces a third-party "analyzer" LLM into the negotiation process. This analyzer would enter early in the negotiation, equipped with a partial view of each company's background (excluding full hidden agendas). Its role would be to monitor the exchange for linguistic signals that hint at hidden motives or authority constraints—such as repeated references to “I need approval from corporate” or concerns about IP retention. Upon identifying these signals, the analyzer would intervene by offering strategic recommendations to just one party in the negotiation (e.g., the acquirer), aiming to enhance its negotiation strategy or leverage perceived weaknesses in the opposing side's position. Additionally, the evaluation metrics used to analyze the negotiations could be automated and extended as the evaluation currently involves manual examination.

## Contact

For improvements, bugs, or ideas, feel free to open an issue or reach out!
