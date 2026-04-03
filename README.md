# OpenLibrary MCP Server

For this quiz, I built an MCP server that connects the Open Library API to Claude Desktop. The idea is simple — instead of going to a browser to search for books, you can just ask Claude directly.

I picked Open Library because I'm genuinely interested in books and libraries, and I liked that it's completely free and open — no API key needed, no sign-up, just data.

---

## What it does

Once connected to Claude Desktop, you can ask Claude things like:
- "Search for books about artificial intelligence"
- "Who is George Orwell and what did he write?"
- "Get me details about this book"

Claude will use the MCP server to fetch real results from Open Library and respond with actual data.

There are 3 tools available:

- **search_books** — search for books by title, keyword, or topic
- **get_book_details** — get full info on a specific book using its Open Library Work ID
- **search_author** — look up an author's bio and list of works

---

## How to set it up

### Requirements
- Python 3.10+
- Claude Desktop (make sure you download the direct installer from claude.ai/download, NOT the Microsoft Store version — the Store version doesn't support custom MCP servers)

### Steps

1. Clone the repo
```bash
git clone https://github.com/oluwadamilola-lgtm/openlibrary-mcp.git
cd openlibrary-mcp
```

2. Create a virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Find your Python path
```bash
# Mac/Linux
which python

# Windows
Get-Command python | Select-Object -ExpandProperty Source
```

4. Add this to your Claude Desktop config file
   - On Windows: `C:\Users\YOUR_NAME\AppData\Roaming\Claude\claude_desktop_config.json`
   - On Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openlibrary": {
      "command": "/full/path/to/your/venv/python",
      "args": ["/full/path/to/server.py"]
    }
  }
}
```

5. Restart Claude Desktop — you should see it say "used openlibrary integration" when you ask about books

---

## Dependencies

- `mcp` — the Model Context Protocol SDK
- `httpx` — for making HTTP requests to the Open Library API

---

## Notes

One thing I ran into during setup: if you install Claude Desktop from the Microsoft Store, it runs in a sandboxed environment and won't load custom MCP servers at all. You have to use the direct installer from claude.ai/download. Took a while to figure that out but it works perfectly once you use the right version.