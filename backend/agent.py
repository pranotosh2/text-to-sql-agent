import os
import re
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from database import get_schema_info, execute_query

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=GROQ_API_KEY,
)

# ── Tool 1: Schema introspection ──────────────────────────────────────────────
def schema_tool_fn(input_str: str = "") -> str:
    try:
        return get_schema_info()
    except Exception as e:
        return f"Error reading schema: {str(e)}"


schema_tool = Tool(
    name="get_schema",
    func=schema_tool_fn,
    description=(
        "Use this tool FIRST before anything else. "
        "It returns the full database schema: table names, column names, and data types. "
        "Input: any string (ignored). Output: schema as plain text."
    ),
)

# ── Tool 2: SQL generation ────────────────────────────────────────────────────
def sql_gen_tool_fn(input_str: str) -> str:
    """
    Expects input as: <question>|||<schema>
    Sends to LLM and extracts the SQL query.
    """
    if "|||" not in input_str:
        return "Error: input must be '<question>|||<schema>'"

    question, schema = input_str.split("|||", 1)

    prompt = f"""You are an expert PostgreSQL query writer.

Database schema:
{schema.strip()}

User question: {question.strip()}

Rules:
- Write ONLY a valid PostgreSQL SELECT query.
- Do NOT include any explanation, markdown, or code fences.
- Do NOT use DROP, DELETE, INSERT, UPDATE, ALTER, CREATE.
- Use proper JOINs when needed.
- Limit results to 100 rows unless the user asks for more.
- Output ONLY the raw SQL query, nothing else.

SQL:"""

    response = llm.invoke(prompt)
    sql = response.content.strip()

    # Strip markdown code fences if LLM includes them anyway
    sql = re.sub(r"^```(?:sql)?\n?", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\n?```$", "", sql)

    return sql.strip()


sql_gen_tool = Tool(
    name="generate_sql",
    func=sql_gen_tool_fn,
    description=(
        "Generates a PostgreSQL SELECT query from a natural-language question and schema. "
        "Input format MUST be: '<user_question>|||<schema_text>'. "
        "Output: raw SQL query string."
    ),
)

# ── Tool 3: SQL execution ─────────────────────────────────────────────────────
def sql_exec_tool_fn(sql: str) -> str:
    try:
        result = execute_query(sql.strip())
        if not result["rows"]:
            return "Query executed successfully but returned 0 rows."
        preview = result["rows"][:5]
        return (
            f"SUCCESS. Columns: {result['columns']}. "
            f"Total rows: {result['row_count']}. "
            f"Preview (first 5): {preview}"
        )
    except ValueError as e:
        return f"BLOCKED: {str(e)}"
    except Exception as e:
        return f"ERROR executing SQL: {str(e)}"


sql_exec_tool = Tool(
    name="execute_sql",
    func=sql_exec_tool_fn,
    description=(
        "Executes a validated PostgreSQL SELECT query against the database. "
        "Input: a raw SQL SELECT statement (no markdown). "
        "Output: column names, row count, and a preview of results. "
        "Only SELECT queries are allowed — dangerous statements are blocked."
    ),
)

# ── ReAct Agent ───────────────────────────────────────────────────────────────
TOOLS = [schema_tool, sql_gen_tool, sql_exec_tool]

REACT_PROMPT = PromptTemplate.from_template("""You are a Text-to-SQL agent. Your job is to answer the user's question by querying a PostgreSQL database.

You have access to the following tools:
{tools}

Follow this EXACT sequence every time:
1. Call get_schema to learn the database structure.
2. Call generate_sql with format: '<question>|||<schema>'
3. Call execute_sql with the generated SQL.
4. Return the final answer.

Use the following format:
Question: the input question you must answer
Thought: your reasoning about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have the final answer
Final Answer: the SQL query used, and a summary of the results

Begin!

Question: {input}
Thought: {agent_scratchpad}""")

agent = create_react_agent(llm=llm, tools=TOOLS, prompt=REACT_PROMPT)

agent_executor = AgentExecutor(
    agent=agent,
    tools=TOOLS,
    verbose=True,
    max_iterations=6,
    handle_parsing_errors=True,
)


def run_agent(question: str) -> dict:
    """
    Runs the full agent pipeline.
    Returns sql, results, columns, and summary.
    """
    try:
        agent_response = agent_executor.invoke({"input": question})
        final_answer = agent_response.get("output", "")

        # Re-execute to get structured results for the UI
        schema = get_schema_info()
        sql = sql_gen_tool_fn(f"{question}|||{schema}")
        result = execute_query(sql)

        return {
            "success": True,
            "question": question,
            "sql": sql,
            "columns": result["columns"],
            "rows": result["rows"],
            "row_count": result["row_count"],
            "summary": final_answer,
        }
    except Exception as e:
        return {
            "success": False,
            "question": question,
            "sql": "",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "summary": f"Agent error: {str(e)}",
        }
