from urllib.parse import urlparse
from uuid import uuid4


class Node(object):

    def __init__(self):
        self.nodes = set() # de no luon la unique values

    def register_node(self, ip_address):
       """
       To add a node to a set of nodes
       ip_address of node. ex. 'http://192.168.0.5:5000'

       """

       parsed_url = urlparse(ip_address); #print('parsed_url', parsed_url);
       print('parsed_url.netloc', parsed_url.netloc); # netloc =  192.168.0.5:5000
       print('parsed_url.path', parsed_url.path);
       if parsed_url.netloc:
           self.nodes.add(parsed_url.netloc)
       elif parsed_url.path:
           self.nodes.add(parsed_url.path)
       else:
           raise ValueError ("This is Invalid URL")

    @staticmethod
    def get_node_indentifier():
        #print('str(uuid4())', str(uuid4()))
        return str(uuid4()).replace('-','')


def test_class_Node():
    node = Node()
    node.register_node(ip_address='https://docs.python.org/3/tutorial/errors.html') #'http://192.168.0.5:5000')
    node.get_node_indentifier()


if __name__=="__main__":
    test_class_Node()
