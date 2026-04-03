import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

app = Server("openlibrary-mcp")

BASE_URL = "https://openlibrary.org"


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_books",
            description="Search for books on Open Library by title, author, or keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query (title, author, or keyword)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return (default 5, max 10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_book_details",
            description="Get detailed information about a specific book using its Open Library Work ID (e.g. OL45804W).",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_id": {
                        "type": "string",
                        "description": "The Open Library Work ID (e.g. OL45804W)"
                    }
                },
                "required": ["work_id"]
            }
        ),
        Tool(
            name="search_author",
            description="Search for an author on Open Library and get their biography and list of works.",
            inputSchema={
                "type": "object",
                "properties": {
                    "author_name": {
                        "type": "string",
                        "description": "The name of the author to search for"
                    }
                },
                "required": ["author_name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    async with httpx.AsyncClient(timeout=15.0) as client:

        if name == "search_books":
            query = arguments["query"]
            limit = min(arguments.get("limit", 5), 10)

            response = await client.get(
                f"{BASE_URL}/search.json",
                params={"q": query, "limit": limit, "fields": "key,title,author_name,first_publish_year,number_of_pages_median,subject"}
            )
            response.raise_for_status()
            data = response.json()

            docs = data.get("docs", [])
            if not docs:
                return [TextContent(type="text", text="No books found for that query.")]

            results = []
            for doc in docs:
                work_id = doc.get("key", "").replace("/works/", "")
                title = doc.get("title", "Unknown Title")
                authors = ", ".join(doc.get("author_name", ["Unknown Author"]))
                year = doc.get("first_publish_year", "N/A")
                pages = doc.get("number_of_pages_median", "N/A")
                subjects = ", ".join(doc.get("subject", [])[:3])

                results.append(
                    f"📖 **{title}**\n"
                    f"   Author(s): {authors}\n"
                    f"   First Published: {year}\n"
                    f"   Pages: {pages}\n"
                    f"   Subjects: {subjects if subjects else 'N/A'}\n"
                    f"   Work ID: {work_id}"
                )

            output = f"Found {data.get('numFound', 0)} total results. Showing top {len(docs)}:\n\n"
            output += "\n\n".join(results)
            return [TextContent(type="text", text=output)]

        elif name == "get_book_details":
            work_id = arguments["work_id"].strip()
            if not work_id.startswith("/works/"):
                work_id_path = f"/works/{work_id}"
            else:
                work_id_path = work_id

            response = await client.get(f"{BASE_URL}{work_id_path}.json")
            response.raise_for_status()
            data = response.json()

            title = data.get("title", "Unknown Title")
            description = data.get("description", "No description available.")
            if isinstance(description, dict):
                description = description.get("value", "No description available.")

            subjects = ", ".join(data.get("subjects", [])[:5]) or "N/A"
            subject_places = ", ".join(data.get("subject_places", [])[:3]) or "N/A"
            subject_times = ", ".join(data.get("subject_times", [])[:3]) or "N/A"
            first_publish = data.get("first_publish_date", "N/A")

            # Fetch author names
            author_refs = data.get("authors", [])
            author_names = []
            for a in author_refs[:3]:
                author_key = a.get("author", {}).get("key", "")
                if author_key:
                    try:
                        a_resp = await client.get(f"{BASE_URL}{author_key}.json")
                        a_data = a_resp.json()
                        author_names.append(a_data.get("name", "Unknown"))
                    except Exception:
                        pass

            authors_str = ", ".join(author_names) if author_names else "N/A"

            output = (
                f"📚 **{title}**\n\n"
                f"**Author(s):** {authors_str}\n"
                f"**First Published:** {first_publish}\n"
                f"**Subjects:** {subjects}\n"
                f"**Places:** {subject_places}\n"
                f"**Time Periods:** {subject_times}\n\n"
                f"**Description:**\n{description}"
            )
            return [TextContent(type="text", text=output)]

        elif name == "search_author":
            author_name = arguments["author_name"]

            response = await client.get(
                f"{BASE_URL}/search/authors.json",
                params={"q": author_name, "limit": 1}
            )
            response.raise_for_status()
            data = response.json()

            docs = data.get("docs", [])
            if not docs:
                return [TextContent(type="text", text=f"No author found with the name '{author_name}'.")]

            author = docs[0]
            author_key = author.get("key", "")

            # Fetch full author details
            author_resp = await client.get(f"{BASE_URL}/authors/{author_key}.json")
            author_data = author_resp.json()

            name = author_data.get("name", "Unknown")
            birth = author_data.get("birth_date", "N/A")
            death = author_data.get("death_date", "Still alive / N/A")
            bio = author_data.get("bio", "No biography available.")
            if isinstance(bio, dict):
                bio = bio.get("value", "No biography available.")

            # Fetch their works
            works_resp = await client.get(
                f"{BASE_URL}/authors/{author_key}/works.json",
                params={"limit": 5}
            )
            works_data = works_resp.json()
            works = works_data.get("entries", [])
            work_titles = [w.get("title", "Unknown") for w in works]

            output = (
                f"✍️ **{name}**\n\n"
                f"**Born:** {birth}\n"
                f"**Death:** {death}\n\n"
                f"**Biography:**\n{bio[:800]}{'...' if len(str(bio)) > 800 else ''}\n\n"
                f"**Notable Works:**\n" +
                "\n".join(f"- {t}" for t in work_titles)
            )
            return [TextContent(type="text", text=output)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())