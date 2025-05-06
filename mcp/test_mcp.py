# Code bellow written following examples here: https://llama-stack.readthedocs.io/en/latest/building_applications
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client import LlamaStackClient
from termcolor import cprint
import argparse
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--remote", help="Uses the remote_url", action="store_true")
parser.add_argument("-s", "--session-info-on-exit", help="Prints agent session info on exit", action="store_true")
parser.add_argument("-a", "--auto", help="Automatically runs examples, and does not start a chat session", action="store_true")
args = parser.parse_args()

model="meta-llama/Llama-3.2-3B-Instruct"

# Connect to a llama stack server

base_url=os.getenv("BASE_URL","http://localhost:8321")
mcp_url=os.getenv("MCP_ENDPOINT")

client = LlamaStackClient(base_url=base_url)
logger.info(f"Connected to Llama Stack server @ {base_url} \n")

# Get tool info and register tools
registered_tools = client.tools.list()
registered_tools_identifiers = [t.identifier for t in registered_tools]
registered_toolgroups = [t.toolgroup_id for t in registered_tools]



if "mcp::auto_quote"in registered_toolgroups:
    client.toolgroups.unregister("mcp::auto_quote")

if "mcp::auto_quote" not in registered_toolgroups:
    # Register MCP tools
    client.toolgroups.register(
        toolgroup_id="mcp::auto_quote",
        provider_id="model-context-protocol",
        mcp_endpoint={"uri":mcp_url},
        )
mcp_tools = [t.identifier for t in client.tools.list(toolgroup_id="mcp::auto_quote")]

logger.info(f"""Your Server has access the the following toolgroups:
{set(registered_toolgroups)}
""")

# Create simple agent with tools
agent = Agent(
    client,
    model=model,
    instructions = """You are a helpful assistant. You have access to a number of tools.
    Whenever a tool is called, be sure return the Response in a friendly and helpful tone.
    When you are asked to search the web you must use a tool.
    """ ,
    tools=["mcp::auto_quote"],
    tool_config={"tool_choice":"auto"}
)

if args.auto:
    user_prompts = [
                    "Can I get the quote for Roger, who has id Q1?",
                    #"Can you add a new quote based on his info?"
                    #"Can you update the premium of Q1 to be $100.00?. All Values MUST be strings",
                    #"Send an email with quote information to Q1?",
                    "Can you calculate a new quote for Roger Lopez and then tell me the new premium?"
                    "Can you give me the difference between his new premium and current premium?"
                    ]

    session_id = agent.create_session(session_name="Auto_demo")
    for prompt in user_prompts:  
        turn_response = agent.create_turn(
            messages=[
                {
                    "role":"user",
                    "content": prompt
                }
            ],
            session_id=session_id,
            stream=True,
        )
        for log in EventLogger().log(turn_response):
            log.print()

else:
    #Create a chat session
    session_id = agent.create_session(session_name="Conversation_demo")
    while True:
        user_input = input(">>> ")
        if "/bye" in user_input:
            if args.session_info_on_exit:
                agent_session = client.agents.session.retrieve(session_id=session_id, agent_id=agent.agent_id)
                print( agent_session.to_dict())
            break
        turn_response = agent.create_turn(
            session_id=session_id,
            messages=[{"role": "user", "content": user_input}],
        )

        for log in EventLogger().log(turn_response):
            log.print()