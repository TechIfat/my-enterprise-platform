import typer
import subprocess
import uvicorn

app = typer.Typer(name="eap", help="Enterprise Agentic Platform (EAP) Control CLI", add_completion=False)

@app.command()
def seed():
    """🌱 Seed the ChromaDB Vector Database."""
    typer.secho("Starting Knowledge Seeder...", fg=typer.colors.GREEN, bold=True)
    subprocess.run(["python", "-m", "eap.knowledge_seeder"])

@app.command()
def chat():
    """💬 Start the multi-agent swarm in interactive mode."""
    typer.secho("Booting Local Agent Swarm...", fg=typer.colors.BLUE, bold=True)
    subprocess.run(["python", "-m", "eap.agent"])

@app.command()
def serve(port: int = 8000):
    """🚀 Start the production FastAPI REST Gateway."""
    typer.secho(f"Starting API Gateway on port {port}...", fg=typer.colors.MAGENTA, bold=True)
    # Notice we changed "api:app" to "eap.api:app"
    uvicorn.run("eap.api:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    app()