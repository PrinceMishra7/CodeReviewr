from fastmcp import FastMCP
import os
from dotenv import load_dotenv
import logging
load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MCP_HOST = os.getenv("MCP_HOST")
MCP_PORT = int(os.getenv("MCP_PORT"))

mcp = FastMCP("Code-Reviewer")

@mcp.tool()
def sample_tool(input: str)->str:
    '''A sample tool that takes a string input and returns a string output.'''
    return f"Sample tool recieved : {input}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http",host=MCP_HOST,port=MCP_PORT,path="/code-reviewer",stateless_http=True)

# npx @modelcontextprotocol/inspector

