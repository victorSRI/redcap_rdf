##
##  See COPYING file distributed along with the redcap_rdf package for the
##  copyright and license terms
##
""" Data Dictionary Transformer to Semantic

@author: Victor Meyerson
"""
import os
import csv
import sys
import argparse

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, FOAF, RDF, RDFS, OWL, SKOS, VOID, XSD

# Header columns for data dictionary
FIELD_NAME = "Variable / Field Name"
FORM = "Form Name"
FIELD_TYPE = "Field Type"
FIELD_LABEL = "Field Label"
CHOICES = "Choices, Calculations, OR Slider Labels"
TEXT_TYPE = "Text Validation Type OR Show Slider Number"
TEXT_MIN = "Text Validation Min"
TEXT_MAX = "Text Validation Max"

# Header columns for config file
DIMENSION = "dimension"
CONCEPT = "concept"
CATEGORIES = "categories"
UNITS = "units"


class Transformer:
    def __init__(self):
        # clear internal data structures
        self._g = Graph()
        self._ns_dict = {}
        self._config_dict = {}
        self._add_prefixes()

    def build_graph(self, dd, config):
        self._build_config_lookup(config)
        if not os.path.isfile(dd):
            print("{} file not found".format(dd))
            return
        print("Processing: {}".format(dd))

        # constants
        rdf_property = self._get_ns("rdf")["Property"]
        dimension_property = self._get_ns("qb")["DimensionProperty"]
        measure_property = self._get_ns("qb")["MeasureProperty"]
        concept = self._get_ns("qb")["concept"]
        rdfs_label = self._get_ns("rdfs")["label"]
        rdfs_subPropertyOf = self._get_ns("rdfs")["subPropertyOf"]
        rdfs_range = self._get_ns("rdfs")["range"]

        with open(dd) as f:
            reader = csv.DictReader(f)
            for row in reader:
                field_name = row[FIELD_NAME]
                # TODO: Use Field Label if available else field_name.split('_')
                # and capitalize and join with a space.
                node = self._get_ns("ncanda")[field_name]
                self._g.add((node, rdfs_label, Literal(field_name)))
                prop = measure_property
                if (field_name in self._config_dict and
                        DIMENSION in self._config_dict[field_name]):
                    if self._config_dict[field_name][DIMENSION] == "y":
                        prop = dimension_property
                self._g.add((node, rdf_property, prop))
                if (field_name in self._config_dict and
                        CONCEPT in self._config_dict[field_name]):
                    obj = self._get_term(self._config_dict[field_name][CONCEPT])
                    self._g.add((node, concept, obj))
                if (field_name in self._config_dict and
                        UNITS in self._config_dict[field_name]):
                    obj = self._get_term(self._config_dict[field_name][UNITS])
                    self._g.add((node, rdfs_range, obj))

        # self._display_raw_triples(self._g)

    def display_graph(self):
        print(self._g.serialize(format='n3'))

    def _display_raw_triples(self, g):
        # Iterate over triples in store and print them out.
        print("--- printing raw triples ---")
        for s, p, o in g:
            print(s, p, o)

    def _add_prefix(self, prefix, namespace):
        ns = Namespace(namespace)
        self._g.bind(prefix, ns)
        self._ns_dict[prefix] = ns

    def _add_prefixes(self):
        self._add_prefix("owl", OWL)
        self._add_prefix("void", VOID)
        self._add_prefix("skos", SKOS)

        self._add_prefix("ncanda", "http://ncanda.sri.com/terms.ttl#")
        self._add_prefix("fma", "http://purl.org/sig/fma#")
        self._add_prefix("prov", "http://w3c.org/ns/prov#")
        self._add_prefix("nidm", "http://purl.org/nidash/nidm#")
        self._add_prefix("fs", "http://www.incf.org/ns/nidash/fs#")

        # add in builtins
        self._add_prefix("rdf", RDF)
        self._add_prefix("rdfs", RDFS)
        self._add_prefix("xsd", XSD)
        self._add_prefix("dct", DCTERMS)
        self._add_prefix("foaf", FOAF)

        # placeholder
        self._add_prefix("ph", "file:///placeholder#")

    def _get_ns(self, prefix):
        if prefix in self._ns_dict:
            return self._ns_dict[prefix]
        return None

    def _get_term(self, term):
        parts = term.split(":")
        ns = parts[0]
        resource = parts[1]
        return self._get_ns(ns)[resource]

    def _build_config_lookup(self, config):
        if not os.path.isfile(config):
            print("{} file not found".format(config))
            return

        with open(config) as f:
            reader = csv.DictReader(f)
            for row in reader:
                # drop empty values
                res = dict((k, v) for k, v in row.iteritems() if v is not "")
                self._config_dict[row[FIELD_NAME]] = res

    # 'private' member data
    _g = Graph()
    _ns_dict = {}
    _config_dict = {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datadict",
                        help="the data dictionary csv file",
                        type=str)
    parser.add_argument("-c", "--config",
                        help="a json config file",
                        type=str)
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()

    transformer = Transformer()
    transformer.build_graph(args.datadict, args.config)
    transformer.display_graph()


if __name__ == "__main__":
    sys.exit(main())
