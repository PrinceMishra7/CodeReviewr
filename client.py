import asyncio
from mcp import ClientSession,types
from mcp.client.streamable_http import streamable_http_client


async def main():
    async with streamable_http_client("http://127.0.0.1:8000/code-reviewer") as (read_stream, write_stream,_):
        async with ClientSession(read_stream,write_stream) as session:
            await session.initialize()
            print("Session initialized")
            tools = await session.list_tools()
            print(f"Available tools\n")
            for tool in tools.tools:
                print(f"Tool : {tool.name}\n")
                '''
                Tool : name='get_pull_request_context' title=None description="Retrieves core metadata, operational statuses, structural stats, and description \nfor a specific GitHub Pull Request.\n\nCRITICAL RULES FOR THE AI AGENT:\n1. READ BEFORE ACTING: Use this tool first before generating or modifying code reviews. It provides \n   the target base/head branch mapping and structural details necessary to contextualize changes.\n2. STATE MONITORING: Check the 'Mergeable' status in the output report to see if the PR has \n   active merge conflicts (`dirty`) or is ready to merge (`clean`).\n3. CHANGELOG OVERVIEW: Review the 'Technical Stats' section (additions, deletions, files changed) \n   to calibrate the scale and scope of the code review before pulling individual files." inputSchema={'additionalProperties': False, 'properties': {'owner': {'type': 'string', 'description': 'The account owner of the repository (case-insensitive).'}, 'repo': {'type': 'string', 'description': "The name of the repository without the '.git' extension (case-insensitive)."}, 'pr_number': {'type': 'integer', 'description': 'The numeric ID identifying the target pull request.'}}, 'required': ['owner', 'repo', 'pr_number'], 'type': 'object'} outputSchema={'properties': {'result': {'type': 'string'}}, 'required': ['result'], 'type': 'object', 'x-fastmcp-wrap-result': True} icons=None annotations=None meta={'fastmcp': {'tags': []}} execution=None
                '''
            
            # call a tool
            result = await session.call_tool("get_pull_request_context",{"owner":"PrinceMishra7","repo":"CodeReviewr","pr_number":3})

            # print(f"Tool Result\n\n{result}")
            '''
            meta={'fastmcp': {'wrap_result': True}} 
            content=[
            TextContent
            (
            type='text', 
            text='# Pull Request Details: SCRUM-5 : Added a tool to get the folder stucture of the project (#3)\n- **Status**: open | **Mergeable**: clean\n- **Author**: PrinceMishra7\n- **Branch**: `folder_struct` -> `main`\n- **Assignees**: None\n- **Reviewers**: devK0der\n\n## Technical Stats\n- **Files Changed**: 2\n- **Commits**: 3\n- **Line Changes**: +193 / -4\n\n## Description\n"\n\n## Links\n- [View PR on GitHub](https://github.com/PrinceMishra7/CodeReviewr/pull/3)\n- [Raw Diff](https://github.com/PrinceMishra7/CodeReviewr/pull/3.diff)',
            annotations=None, 
            meta=None
            )
            ] 
            structuredContent={
            'result': '# Pull Request Details: SCRUM-5 : Added a tool to get the folder stucture of the project (#3)\n- **Status**: open | **Mergeable**: clean\n- **Author**: PrinceMishra7\n- **Branch**: `folder_struct` -> `main`\n- **Assignees**: None\n- **Reviewers**: devK0der\n\n## Technical Stats\n- **Files Changed**: 2\n- **Commits**: 3\n- **Line Changes**: +193 / -4\n\n## Description\n"\n\n## Links\n- [View PR on GitHub](https://github.com/PrinceMishra7/CodeReviewr/pull/3)\n- [Raw Diff](https://github.com/PrinceMishra7/CodeReviewr/pull/3.diff)'
            } 
            isError=False
            '''
            result_unstructured = result.content[0]
            if isinstance(result_unstructured,types.TextContent):
                print(f"Tool Result\n{result_unstructured.text}")
            print(f"\nStructured Tool Result\n{result.structuredContent}")
        

if __name__ == "__main__":
    asyncio.run(main())