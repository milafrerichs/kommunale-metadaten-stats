import argparse
import csv

from SPARQLWrapper import SPARQLWrapper, JSON


def get_first_row_for_csv(csv_filename):
    # Load the list of identifiers to filter out from a CSV file
    data = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row[0])
    return data


def filter_from_csv(csv_filename):
    # Format the list of as a comma-separated string for the SPARQL query
    return ', '.join(['"%s"' % p for p in get_first_row_for_csv(csv_filename)])


def main(field):
    sparql = SPARQLWrapper("https://govdata.de/SPARQL")

    publisher_filter = filter_from_csv('data/publishers.csv')
    contact_filter = filter_from_csv('data/contact_names.csv')

    query = (
        "PREFIX dcat: <http://www.w3.org/ns/dcat#>"
        "PREFIX dct: <http://purl.org/dc/terms/>"
        "PREFIX foaf: <http://xmlns.com/foaf/0.1/>"
        "PREFIX vCard: <http://www.w3.org/2006/vcard/ns#>"
        "SELECT (COUNT(DISTINCT ?dataset) AS ?count)"
        "WHERE {"
        "?dataset a dcat:Dataset ;"
        f"        {field} ?key ;"
        "        dct:publisher ?publisher ."
        "?publisher foaf:name ?pub_name ."
        "OPTIONAL {"
        "    ?dataset dcat:contactPoint ?contact ."
        "    ?contact vCard:fn ?contact_name ."
        "}"
        "FILTER ("
        f"    ?pub_name IN ({publisher_filter}) ||"
        f"    ?contact_name IN ({contact_filter})"
        ")"
        "}"
    )
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    count = results['results']['bindings'][0]['count']['value']
    print("Number of datasets with dct:spatial property, excluding selected publishers:", count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get Count of datasets using a specific metadata field")
    parser.add_argument("field", type=str, help="Name of the field including namespace, e.g. dct:spatial")
    args = parser.parse_args()

    main(args.field)
