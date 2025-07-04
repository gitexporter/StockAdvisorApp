import asyncio
import os
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent, SequentialAgent
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext
from typing import AsyncGenerator, Optional
from google.adk.events import Event, EventActions
from agents.sub_agents.reviewer1trading_agent import create_reviewer1_trading_agent

# --- State Keys ---
#STATE_CURRENT_DOC = "current_document"
#STATE_CRITICISM = "criticism"
# Define the exact phrase the Critic should use to signal completion
COMPLETION_REVIEW = "No_stock_shortlisted."

# --- Tool Definition ---
def exit_loop(tool_context: ToolContext):
  """Call this function ONLY when the reviewer tells that none of the stock is shortlisted , signaling the iterative process should end."""
  print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
  tool_context.actions.escalate = True
  # Return empty dict as tools should typically return JSON-serializable output
  return {}

# --- 1. Define Sub-Agents for Each Pipeline Stage ---

stock_advisor = LlmAgent(
    name="StockAdvisorAgent",
    model="gemini-2.0-flash",
    # Change 3: Improved instruction
    instruction="""You are a stock advisor.
Based *only* on the user's personal details, You will suggest him Low risk stocks that are suitable for the user's age,
dependecies and monthly savings. 

* Suggest 40% Large Cap stocks, 30% Mid Cap and 30% Low Cap stocks to the investor if his age is more than 40years, he has more than 
  2 dependents and mothly saving is less than 60000 INR.
* Suggest 30% Large Cap , 30% Mid Cap and 40% Low cap stocks if the investor is less than 30 years age , less dependecies.

Output the *type* of stocks to be invested based on user's profile , enclosed in triple backticks (```suggested_stocks ... ```). 
Do not add any other text before or after the block.
""",
    description="Share the type of stocks alongwith their sectors based on user's profile'.",
    output_key="stocks_types" # Stores output in state['suggested_stock']
)

# CoStock suggestion Agent
# Takes the initial specification (from user query) and writes code.
stock_agent = LlmAgent(
    name="StockAgent",
    model="gemini-2.0-flash",
    # Change 3: Improved instruction
    instruction="""You are a stock broker.
Based *only* on the type of stocks suggested by StockAdvisorAgent, You will suggest atleast 10 high performing stocks in different sectors using yFinance API's
details in NSE stock market.

**type of stocks**
```
      {{stocks_types}}
    ```

Output the *list* of stocks in yahoo ticker format with their sector name and summarized explaination in just 20-30 words  , enclosed in triple backticks (```suggested_stocks ... ```). 
Do not add any other text before or after the block.
""",
    description="Share the details of stocks alongwith their sectors based on user's request'.",
    output_key="suggested_stock" # Stores output in state['suggested_stock']
)

# Code Reviewer Agent
# Takes the code generated by the previous agent (read from state) and provides feedback.
stock_reviewer_agent1 = LlmAgent(
    name="StockReviewerAgent1",
    model="gemini-2.0-flash",
    # Change 3: Improved instruction, correctly using state key injection
    instruction=f"""You are an expert first level Stock Reviewer. 
    Your task is to review the stocks suggested by stock_agent using sub agent reviewer1_trading_agent.

    **Stocks to Review:**
    ```
      {{suggested_stock}}
    ```

**Task**

    Prepare a *list* of shortlisted stocks using key "shortlisted_stocks". 

     
**Output:**
Provide your feedback as a concise, bulleted list of stocks. Focus on the most important points for improvement.
Keep a record of your analysis and the rationale behind selection of each stock.
Output *only* the list of selected stocks based on your review criteria or the "No Stock shortlisted" statement.
""",
    description="Reviews stocks based on review criteria mentioned in instructions and provides a list of shortlisted stocks.",
    output_key="shortlisted_stocks",
    sub_agents=[create_reviewer1_trading_agent()], # Stores output in state['shortlisted_stocks']
)


# Code Refactorer Agent
# Takes the original code and the review comments (read from state) and refactors the code.
stock_reviewer_agent2 = LlmAgent(
    name="StockReviewerAgent2",
    model="gemini-2.0-flash",
    include_contents='none',
    # Change 3: Improved instruction, correctly using state key injection
    instruction=f"""You are a stock advisory agent that suggests the stocks suggested by StockReviewerAgent1 in understanding terms
Your goal is to review the *stocks shortlisted* by StockReviewerAgent1 and suggest user for investment by reviewing their portfolio.
You should *Allocate* the total amount for investment across these shortlisted stocks for optimal diversification.
Carefully review the stocks shortlisted from StockReviewerAgent1 to advice users for further investments.
 
**Original Suggestion:**
  ```
  {{suggested_stock}}
  ```

  **Shortlisted Stocks:**
'''
  {{shortlisted_stocks}}
'''

**Task**

 Your task is to allocate the total amount for investment across these shortlisted stocks for optimal diversification.
 
   
**Output:**
Output *only* the final list of selected stocks with *allocated amount* to be invested across those stocks enclosed in triple backticks (```Final_stocks ... ```). 
Do not add any other text before or after the code block.


""",
    description="You should be able to *Allocate* the total amount for investment across these shortlisted stocks for optimal diversification.",
   # tools=[exit_loop], # Provide the exit_loop tool
    output_key="shortlisted_stock2", # Stores output in state['shortlisted_final_stocks']
)

# STEP 2: Refinement Loop Agent
#refinement_loop = LoopAgent(
 #   name="RefinementLoop",
    # Agent order is crucial: Critique first, then Refine/Exit
  #  sub_agents=[
   #     stock_reviewer_agent1,
    #    stock_reviewer_agent2,
   # ],
   # max_iterations=3 # Limit loops
#)

# --- 2. Create the SequentialAgent ---
# This agent orchestrates the pipeline by running the sub_agents in order.
code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[stock_advisor,stock_agent, stock_reviewer_agent1,stock_reviewer_agent2 ],
    description="Executes a sequence of code writing, reviewing, and refactoring.",
    # The agents will run in the order provided: Writer -> Reviewer -> Refactorer
)

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = code_pipeline_agent
