from typing import Optional
import typer
from mutant_client import Mutant

typer_app = typer.Typer()


@typer_app.command()
def hello(name: Optional[str] = None):
    if name:
        typer.echo(f"Hello, {name}")
    else:
        typer.echo("Hello world!")


@typer_app.command()
def count(model_space: Optional[str] = typer.Argument(None)):
    mutant = Mutant()
    typer.echo(mutant.count(model_space=model_space))


# for being called directly
if __name__ == "__main__":
    typer_app()


# for the setup.cfg entry_pint
def run():
    typer_app()