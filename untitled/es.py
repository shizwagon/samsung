import os, re
from elasticsearch import Elasticsearch
# from elasticsearch_dsl import Search
# from elasticsearch_dsl.query import MultiMatch, Match

elasticSearchIndex = 'datacenter'
os.environ['BONSAI_URL'] = 'https://zo9my8o81w:vmt07570ju@first-cluster-9289434500.us-west-2.bonsaisearch.net'
bonsai = os.environ['BONSAI_URL']
auth = re.search('https\:\/\/(.*)\@', bonsai).group(1).split(':')
host = bonsai.replace('https://%s:%s@' % (auth[0], auth[1]), '')

# Connect to cluster over SSL using auth for best security:
es_header = [{
  'host': host,
  'port': 443,
  'use_ssl': True,
  'http_auth': (auth[0], auth[1])
}]

# Instantiate the new Elasticsearch connection:
client = Elasticsearch(es_header)


def get_mappings():
    response = []
    mapping = client.indices.get_mapping()
    fields = mapping['datacenter']['mappings']['provider']['properties']
    for field in fields:
        if len(fields[field]) == 1:
            temp = []
            for subfield in fields[field]['properties']:
                temp.append(subfield)
            temp_dict = {field: temp}
            response.append(temp_dict)
        else:
            response.append(field)
    return response


def add_entry(json, id):
    client.create(index=elasticSearchIndex, doc_type="provider", id=id, body=json)


def get_all():
    response = client.search(index=elasticSearchIndex, size=1000)
    hits = response["hits"]["hits"]
    return hits


def delete(doc_id):
    client.delete_by_query(index=elasticSearchIndex, body={"query": {"match": {"_id": doc_id}}})


def search(doc_id):
    return client.search(index=elasticSearchIndex, body={"query": {"match": {"_id": doc_id}}})
