"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """GRPC Access Log."""


if __name__ == "__main__":
    main(prog_name="grpc-accesslog")  # pragma: no cover
