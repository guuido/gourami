import click
from gourami.utils.logging import setup_logging
from gourami.cli.server import run_server
from gourami.core.config import configure_settings

@click.group()
def cli():
    """Command-line interface for the chatbot framework."""
    pass

@click.command()
@click.option('-p','--port', type=int)
@click.option('-h','--host', type=str)
@click.option('-f','--config-file', type=click.Path(exists=True))
def start(port, host, config_file):
    """
    Start the Gourami server.
    """
    cli_params = {
        k.upper(): v 
        for k, v in locals().items() 
        if v is not None and k not in ['config_file']
    }

    configure_settings(params=cli_params, config_path=config_file)

    run_server()

cli.add_command(start)

if __name__ == '__main__':
    cli()