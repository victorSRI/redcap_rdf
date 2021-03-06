""" Command line interface to the REDCap Data Utilities.

@author: Victor Meyerson
"""

import click
import sys

from redcap_rdf.datadict_validator import Validator
from redcap_rdf.transform_to_cube import Transformer


@click.group()
def cli():
    pass


@cli.command()
@click.option("--datadict",
              help="The data dictionary csv file.",
              type=str,
              required=True)
@click.option("--first-lines",
              help="Applies an extra check to the first rows.",
              type=str,
              default="")
@click.option("--verbose",
              help="Increase output verbosity.",
              default=False,
              is_flag=True)
def validate(datadict, first_lines, verbose):
    rows = first_lines.split(",")

    validator = Validator()
    if verbose:
        validator.enable_verbose()
    validator.process(datadict, rows)


@cli.command()
@click.option("--datadict",
              help="The data dictionary csv file.",
              type=str)
@click.option("--mapping",
              help="The mapping file.",
              type=str)
@click.option("--metadata",
              help="Dataset metadata",
              type=str)
@click.option("--dimensions",
              help="Comma separated keys that should be treated as dimensions",
              type=str,
              default="")
@click.option("--slices",
              help="File with label and comments for slices",
              type=str,
              default="")
@click.option("--observations",
              help="The observations file.",
              type=str)
def create(datadict, mapping, metadata, dimensions, slices, observations):
    transformer = Transformer()
    transformer.build_graph(datadict, mapping)
    transformer.add_metadata(metadata)
    transformer.add_dsd(dimensions, slices)
    transformer.add_observations(observations)
    transformer.display_graph()

if __name__ == '__main__':
    sys.exit(cli())
