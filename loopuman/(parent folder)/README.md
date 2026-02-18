# 🧠 Loopuman Python SDK

**The Human Layer for AI** — Route tasks to real verified humans worldwide. One function call, result in minutes.

When your AI agent hits a wall — CAPTCHAs, phone calls, physical world verification, subjective judgment — Loopuman connects it to a real human who solves it.

## Install

```bash
pip install loopuman
```

## Quick Start

```python
from loopuman import Loopuman

client = Loopuman()  # reads LOOPUMAN_API_KEY from env

# Ask a human anything
result = client.ask("Is the cafe at 123 Main St, Nairobi open right now?")
print(result)  # "Yes, it's open. Hours are 7am-8pm. Photo attached."
```

## Get an API Key (Free)

```python
from loopuman import Loopuman

# Register and get $5 free credit
account = Loopuman.register(
    email="you@example.com",
    company_name="YourApp",
    promo_code="CLAW500"  # $5 free credit
)
print(account["api_key"])  # Set as LOOPUMAN_API_KEY
```

Or visit [loopuman.com](https://loopuman.com).

## Usage

### Simple (blocking)

```python
result = client.ask("Call +254-XXX-XXXX and ask if they deliver to Westlands")
```

### With control

```python
# Create task (returns immediately)
task = client.create_task(
    description="Take a photo of the storefront at 456 Kenyatta Ave",
    category="local",
    budget_vae=100,  # 100 VAE = $1.00 USD
    estimated_seconds=600,  # ~10 min task
    priority="high"
)

# Wait for result
task = client.wait(task.id, max_wait=900)
print(task.result)
print(task.budget_usd)  # $1.00
```

### Bulk tasks

```python
results = client.create_bulk_tasks(
    tasks=[
        {"description": f"Label image: {url}", "category": "image", "budget_vae": 50, "estimated_seconds": 30}
        for url in image_urls
    ],
    webhook_url="https://your-server.com/webhook"
)
```

### Check balance

```python
bal = client.balance()
print(f"${bal['balance_usd']:.2f} remaining")
```

## Framework Integrations

### LangChain

```python
from loopuman.tools import langchain_tool
from langchain.agents import initialize_agent

tools = [langchain_tool()]
agent = initialize_agent(tools=tools, llm=llm, agent="zero-shot-react-description")
agent.run("Verify if this business address is real: 789 Commerce Blvd, Lagos")
```

### CrewAI

```python
from loopuman.tools import crewai_tool
from crewai import Agent, Task, Crew

verifier = Agent(
    role="Field Verifier",
    goal="Verify real-world information using human workers",
    tools=[crewai_tool()],
    llm=llm,
)
```

### AutoGen

```python
from loopuman.tools import autogen_function_map, OPENAI_FUNCTION_SCHEMA

assistant = autogen.AssistantAgent(
    "assistant",
    llm_config={"functions": [OPENAI_FUNCTION_SCHEMA]},
    function_map=autogen_function_map(),
)
```

### OpenAI Function Calling

```python
from loopuman.tools import OPENAI_FUNCTION_SCHEMA, ask_human

# Add to your OpenAI tools
tools = [{"type": "function", "function": OPENAI_FUNCTION_SCHEMA}]

# When the model calls ask_human_worker:
result = ask_human(task_description, category=category, budget_vae=budget_vae, estimated_seconds=estimated_seconds)
```

## Task Categories

| Category | Use For |
|----------|---------|
| `writing` | Write copy, reports, descriptions, emails |
| `research` | Find information, competitive analysis, fact-checking |
| `data` | Data entry, labeling, classification, annotation |
| `survey` | Collect opinions, feedback, research responses |
| `image` | Label images, verify photos, screenshot tasks |
| `local` | Location visits, phone calls, local verification |
| `translation` | Translate or review translations |
| `audio` | Transcribe audio, voice tasks |
| `other` | Anything else |

## Pricing

| Task Type | Cost |
|-----------|------|
| CAPTCHA solve | $0.50 |
| SMS verification | $0.50 |
| Phone call | $0.60-$1.20 |
| Location visit + photo | $0.60-$1.20 |
| Content moderation | $0.50-$1.00 |
| Data labeling (per item) | $0.50-$1.00 |
| RLHF evaluation | $1.00-$2.40 |

Free trial: $5.00 with promo code `CLAW500`. Minimum task: $0.10. Platform enforces $6/hr minimum rate via `estimated_seconds`.

## Error Handling

```python
from loopuman import Loopuman, LoopumanError, InsufficientBalanceError

try:
    result = client.ask("verify this address")
except InsufficientBalanceError:
    print("Balance too low — top up at loopuman.com")
except LoopumanError as e:
    print(f"API error: {e}")
```

## Environment

```bash
export LOOPUMAN_API_KEY=lpm_your_key_here
```

## Links

- Website: [loopuman.com](https://loopuman.com)
- API Docs: [loopuman.com/docs](https://loopuman.com/docs)
- ERC-8004 Agent #17: [8004scan.io](https://www.8004scan.io)
- OpenClaw Skill: `clawhub install loopuman`

## License

MIT
