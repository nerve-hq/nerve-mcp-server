from functools import wraps

from mcp.server.fastmcp import Context

from nerve_mcp.config import nerve_client, server


def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            return f"Encountered an error while processing request: {str(e)}.\n If the error is transient, please try again. Otherwise, please modify your query."
    return wrapper

@handle_errors
@server.resource(uri="search://{query}", name="search", description="A simple resource that searches for information.")
async def search(query: str) -> list[dict]:
    print(f"Searching for {query}")
    # return query
    resources = []
    results = await nerve_client.search(query)
    for result in results:
        resources.append({
            "uri": f"blob://{result['blob_id']}",
            "name": result["name"],
            "text": result["content"],
            "mime_type": "text/plain",
        })
    return resources

@handle_errors
@server.resource(uri="file://{file_id}", name="file", description="A simple resource that gets the text of a file.")
async def get_file(file_id: str) -> str:
    print(f"getting file for {file_id}")
    # return query
    file = await nerve_client.get_file(file_id)
    return file["content"]
    # resources = []
    # results = await nerve_client.get_file(file_id)
    # for result in results:
    #     resources.append({
    #         "uri": f"file://{result['blob_id']}",
    #         "name": result["name"],
    #         "text": result["content"],
    #         "mime_type": "text/plain",
    #     })
    # return resources

