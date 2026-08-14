from mcp.server.fastmcp import FastMCP
import pydantic

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


# Tool: leer un doc
@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_document(doc_id: str = pydantic.Field(description="Id of the document to read")):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


# Tool: editar un doc (find & replace simple)
@mcp.tool(
    name="edit_doc_contents",
    description="Edit a document by replacing a string in its contents with a new string.",
)
def edit_document(
    doc_id: str = pydantic.Field(description="Id of the document to edit"),
    old_str: str = pydantic.Field(description="Text to replace, must match exactly"),
    new_str: str = pydantic.Field(description="New text to replace old_str with"),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)


# Resource: listar todos los ids de docs
@mcp.resource(
    "docs://documents",
    mime_type="application/json",
)
def list_docs() -> list[str]:
    return list(docs.keys())


# Resource: contenido de un doc puntual (template con {doc_id})
@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain",
)
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


# Prompt: reescribir un doc en formato markdown
@mcp.prompt(
    name="format",
    description="Rewrites the contents of a document into markdown format.",
)
def format_document(
    doc_id: str = pydantic.Field(description="Id of the document to format"),
) -> list:
    prompt = f"""
Your goal is to reformat the document identified by doc_id [{doc_id}] to be written in markdown format.

Steps:
1. Read the contents of the doc using the read_doc_contents tool
2. Examine the content and reformat it in valid, well-structured markdown
3. Use the edit_doc_contents tool to overwrite the doc with the markdown version

Only use tools you were given to complete this task.
""".strip()

    return [
        {"role": "user", "content": {"type": "text", "text": prompt}}
    ]


# Prompt: resumir un doc
@mcp.prompt(
    name="summarize",
    description="Summarizes the contents of a document.",
)
def summarize_document(
    doc_id: str = pydantic.Field(description="Id of the document to summarize"),
) -> list:
    prompt = f"""
Read the document identified by doc_id [{doc_id}] using the read_doc_contents tool,
then produce a concise summary (2-3 sentences) of its contents.
""".strip()

    return [
        {"role": "user", "content": {"type": "text", "text": prompt}}
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")