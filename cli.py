import typer
import subprocess
import uvicorn
import os

# Initialize the CLI application
app = typer.Typer(
    name="eap",
    help="Enterprise Agentic Platform (EAP) Control CLI",
    add_completion=False,
)

@app.command()
def seed():
    """
    🌱 Seed the ChromaDB Vector Database with enterprise policies.
    """
    typer.secho("Starting Knowledge Seeder...", fg=typer.colors.GREEN, bold=True)
    subprocess.run(["uv", "run", "knowledge_seeder.py"])

@app.command()
def chat():
    """
    💬 Start the multi-agent swarm in interactive terminal mode.
    """
    typer.secho("Booting Local Agent Swarm...", fg=typer.colors.BLUE, bold=True)
    subprocess.run(["uv", "run", "agent.py"])

@app.command()
def serve(port: int = 8000):
    """
    🚀 Start the production FastAPI REST Gateway.
    """
    typer.secho(f"Starting API Gateway on port {port}...", fg=typer.colors.MAGENTA, bold=True)
    # We use uvicorn to run the API we built yesterday
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    app()