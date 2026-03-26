import typer
import subprocess
import uvicorn
import os
import sys   
from dotenv import load_dotenv

app = typer.Typer(name="eap", help="Enterprise Agentic Platform (EAP) Control CLI", add_completion=False)

# NEW: A helper function to inject the correct environment
def load_environment(env: str):
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        load_dotenv(env_file)
        typer.secho(f"🔒 Environment Loaded: {env_file}", fg=typer.colors.YELLOW)
    else:
        typer.secho(f"⚠️ Warning: {env_file} not found. Falling back to system env.", fg=typer.colors.RED)

@app.command()
def seed(env: str = typer.Option("local", help="Environment to run in (local, prod, staging)")):
    """🌱 Seed the ChromaDB and Legacy SQL Databases."""
    load_environment(env)
    typer.secho("Starting Knowledge Seeder (ChromaDB)...", fg=typer.colors.GREEN, bold=True)
    subprocess.run([sys.executable, "-m", "eap.knowledge_seeder"])
    
    typer.secho("Starting Legacy Mainframe Seeder (SQL)...", fg=typer.colors.YELLOW, bold=True)
    subprocess.run([sys.executable, "-m", "eap.legacy_db"])

@app.command()
def chat(env: str = typer.Option("local", help="Environment to run in (local, prod, staging)")):
    """💬 Start the multi-agent swarm in interactive mode."""
    load_environment(env)
    typer.secho("Booting Local Agent Swarm...", fg=typer.colors.BLUE, bold=True)
    subprocess.run(["python", "-m", "eap.agent"])

@app.command()
def serve(
    port: int = 8000, 
    env: str = typer.Option("local", help="Environment to run in (local, prod, staging)")
):
    """🚀 Start the production FastAPI REST Gateway."""
    load_environment(env)
    typer.secho(f"Starting API Gateway on port {port} in {env.upper()} mode...", fg=typer.colors.MAGENTA, bold=True)
    uvicorn.run("eap.api:app", host="0.0.0.0", port=port, reload=(env == "local"))

@app.command()
def test(env: str = typer.Option("local", help="Environment to run evals in")):
    """🧪 Run the automated Eval-Driven Development (EDD) test suite."""
    load_environment(env)
    typer.secho("Initializing CI/CD Evaluation Pipeline...", fg=typer.colors.CYAN, bold=True)
    subprocess.run(["python", "-m", "eap.evals.run_evals"])

if __name__ == "__main__":
    app()