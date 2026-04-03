# 📚 Open Library MCP Server

An MCP (Model Context Protocol) server that integrates the [Open Library API](https://openlibrary.org/developers/api) with Claude Desktop, allowing you to search books, get book details, and explore authors — all from a natural language prompt.

---

## Features

This MCP server exposes three tools to Claude:

| Tool | Description |
|------|-------------|
| `search_books` | Search for books by title, author, or keyword |
| `get_book_details` | Get full details of a book using its Open Library Work ID |
| `search_author` | Look up an author's biography and notable works |

---

## Requirements

- Python 3.10+
- [Claude Desktop](https://www.anthropic.com/claude) app installed
- No API key needed (Open Library is free and open)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/openlibrary-mcp.git
cd openlibrary-mcp
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Note the full path to your Python executable

```bash
which python    # On Windows: where python
```

You'll need this path for the Claude Desktop config.

---

## Connecting to Claude Desktop

Open your Claude Desktop config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the following (replace paths with your actual paths):

```json
{
  "mcpServers": {
    "openlibrary": {
      "command": "/full/path/to/venv/bin/python",
      "args": ["/full/path/to/openlibrary-mcp/server.py"]
    }
  }
}
```

**Then restart Claude Desktop.**

---

## Example Prompts

Once connected, try these prompts in Claude Desktop:

- *"Search for books about machine learning"*
- *"Find books by George Orwell"*
- *"Get details for the book with work ID OL45804W"*
- *"Who is Tolkien and what are his famous works?"*

---

## Project Structure

```
openlibrary-mcp/
├── server.py          # Main MCP server
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

---

## License

MIT