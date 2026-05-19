import asyncio
# uv add langchain-mcp-adapters
from langchain_mcp_adapters.client import MultiServerMCPClient
# uv add langchain-google-genai
from langchain_google_genai import ChatGoogleGenerativeAI
# uv add langchain
from langchain.agents import create_agent

from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)
# response = llm.invoke("Say Hello")
# print(response.content)

async def main():
    client = MultiServerMCPClient(
        {
            "code-reviewer":{
                "transport":"http",
                "url":"http://127.0.0.1:8000/code-reviewer"
            }
        }
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
        You are a senior software engineer performing automated pull request reviews.

        Workflow:
        1. Use GitHub tools to fetch pull request details.
        2. Analyze the changes carefully.
        3. Post review comments to GitHub for actionable issues.
        4. Avoid posting duplicate or low-value comments.
        5. If no major issues are found, report that the PR is ready to merge.

        Focus on:
        - Correctness
        - Security
        - Performance
        - Maintainability
        - Testing
        """
    )

    response = await agent.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": """
        Review PR https://github.com/PrinceMishra7/CodeReviewr/pull/3.

        Use the available GitHub tools to analyze the pull request and post review comments directly to GitHub for any actionable issues you find.

        Only create comments for meaningful findings. If the PR looks good, state that it is ready to merge.
        """
                }
            ]
        })
    
    final_message = response["messages"][-1].content

    print("\n=== FINAL REVIEW SUMMARY ===\n")
    print(final_message)
    

if __name__ == "__main__":
    asyncio.run(main())



