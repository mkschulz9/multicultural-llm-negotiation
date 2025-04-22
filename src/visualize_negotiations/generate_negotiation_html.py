import json
from pathlib import Path

# Set up base directories
base_path = Path(__file__).resolve().parents[1]
history_dir = base_path / "negotiation_histories"
persona_dir = base_path / "generated_personas"
output_dir = base_path / "visualize_negotiations"
output_dir.mkdir(parents=True, exist_ok=True)

# Gather matching JSON files
negotiation_files = sorted(history_dir.glob("*.json"))
persona_files = sorted(persona_dir.glob("*.json"))

if len(negotiation_files) != len(persona_files):
    raise ValueError("Mismatch between negotiation and persona files.")


# Format a persona section with role-based coloring
def format_persona_section(title, data, role_class):
    bg_color = "#e6f4ea" if role_class == "acquirer" else "#e8f0fe"
    return f"""
    <details style="background: {bg_color}; padding: 10px; border-radius: 8px; margin-bottom: 24px;" open>
      <summary><span style="font-size: 20px; font-weight: bold;">{title}</span></summary>
      <p><strong>Country:</strong> {data.get("country_based", "")}</p>
      <p><strong>Description:</strong> {data.get("business_descr", [""])[0]}</p>
      <p><strong>Cultural Profile:</strong> {data.get("cultural_profile", [""])[0]}</p>
      <p><strong>Authority Dynamics:</strong> {data.get("authority_dynamics", [""])[0]}</p>
      <p><strong>Financial Info:</strong> {data.get("financial_info", [""])[0]}</p>
      <p><strong>Unspoken Interests:</strong> {data.get("unspoken_interests", [""])[0]}</p>
    </details>
    """


# Generate HTML for each file pair
for neg_file, per_file in zip(negotiation_files, persona_files):
    negotiation_file_name = neg_file.stem
    output_path = output_dir / f"{negotiation_file_name}.html"

    with open(neg_file, "r") as nf, open(per_file, "r") as pf:
        log = json.load(nf)
        persona = json.load(pf)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>LLM Negotiation Log</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f9f9f9;
      padding: 40px;
      color: #333;
      line-height: 1.6;
    }
    h1 {
      text-align: center;
      margin-bottom: 24px;
    }
    .entry {
      margin-bottom: 32px;
      padding: 0;
      border-radius: 8px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .entry summary {
      padding: 16px;
      font-size: 18px;
      font-weight: bold;
      border-radius: 8px;
    }
    .entry.acquirer summary {
      background: #e6f4ea;
      border-left: 6px solid #4caf50;
    }
    .entry.target summary {
      background: #e8f0fe;
      border-left: 6px solid #1a73e8;
    }
    .entry .content {
      padding: 16px;
      background: #fff;
      border-top: 1px solid #ddd;
    }
    details {
      margin-top: 12px;
    }
    summary {
      cursor: pointer;
      color: #007acc;
    }
    pre {
      background: #f4f4f4;
      padding: 12px;
      border-radius: 6px;
      overflow-x: auto;
    }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
  <h1>LLM Negotiation Transcript</h1>
"""

    # Add persona sections
    html += format_persona_section("Acquirer Persona", persona["acquirer"], "acquirer")
    html += format_persona_section("Target Persona", persona["target"], "target")

    # Add conversation entries
    for i, entry in enumerate(log, start=1):
        role = entry.get("role", "Unknown").capitalize()
        message = entry.get("message", "").strip()
        reasoning = entry.get("reasoning", "").strip()
        query = entry.get("query", "").strip()
        role_class = "acquirer" if role.lower() == "acquirer" else "target"

        html += f"""
<details class="entry {role_class}" closed>
  <summary>Turn {i} - {role}</summary>
  <div class="content">
    <div class="message" data-markdown>{json.dumps(message)}</div>
    <details>
      <summary style="background: none">Show LLM Reasoning</summary>
      <pre>{reasoning}</pre>
    </details>
    <details>
      <summary style="background: none">Show Prompt</summary>
      <pre>{query}</pre>
    </details>
  </div>
</details>
"""

    # Markdown conversion script
    html += """
<script>
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-markdown]").forEach(el => {
      const raw = JSON.parse(el.textContent);
      el.innerHTML = marked.parse(raw);
    });
  });
</script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Generated: {output_path.name}")
