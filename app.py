from flask import Flask, jsonify, request

from blockchain import Blockchain, _index, _transactions, _proof, _previous_hash
from network import Node

app = Flask(__name__) # Instantiates a node

node = Node()
node_identifier = node.get_node_indentifier() # create a globally unique address for this node

blockchain = Blockchain() # instantiate a blockchain class


@app.route('/')   # create an endpoint for Welcome: A Simple Blockchain
def home():
    return "Welcome: A Simple Blockchain!"


@app.route('/chain', methods=['GET']) # Create an endpoint /chain with GET method
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length of chain': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST']) # Create an endpoint /transactions/new with POST method
def create_new_transaction():
    values = request.get_json(); print('values getting from Postman is: ', values)

    # The content of user sends to server as below. # can dau "" chu khong ''
    '''
    Put somethings like this into Postman
    {
         "sender": "sender's address",
         "recipient": "recipient's address",
         "amount": 9
    }
    '''

    # Check that the required fields is in the POST data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400 # Bad request error

    # Create a new Transaction
    index = blockchain.create_new_transaction(sender=values['sender'],
                                              recipient= values['recipient'],
                                              amount= values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201 # created after post command. (indicate sucess)


@app.route('/mine', methods=['GET']) # Create an endpoint /mine with GET method
def mine():

    # Run the PoW algorithm to get the next proof
    last_block = blockchain.last_block
    new_proof = blockchain.implement_proof_of_work(last_block=last_block)

    # We will have a reward to find the new proof
    # The sender is "0" to signify that this node has mined a new coin
    blockchain.create_new_transaction(sender='0',
                                      recipient=node_identifier,
                                      amount=1)


    # A new block by adding to the chain
    previous_hash = blockchain.generate_hash(last_block)
    block = blockchain.create_new_block(previous_hash=previous_hash,
                                        proof=new_proof)

    response = {"message": "New Block ",
                "index": block[_index],
                "transactions": block[_transactions],
                "proof": block[_proof],
                "previous_hash": block[_previous_hash]
                }
    # pass the summary data to the jsonify function, which returns a JSON response.
    # 200 means ok
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST']) # Create an endpoint /nodes/register with POST method
def register_nodes():
    values = request.get_json() # get list of node
    print("values of nodes from Postman is:  ", values)
    # # ex. values = { "nodes": ["http://127.0.0.1:5001"] }

    peer_nodes = values.get('nodes') # get list of nodes

    if peer_nodes is None:
        return "Error: Please supply a valid list of nodes", 400  # Bad request error

    for node_url in peer_nodes:
        node.register_node(node_url)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(node.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def make_consensus():

    print('nodes before consensus', node.nodes)
    bool_replaced_chain = blockchain.resolve_conflicts(node) # True or False

    if bool_replaced_chain:
        response = {'message': 'Our chain was replaced',
                    'new_chain': blockchain.chain
                    }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    print('response', response)

    return jsonify(response), 200


if __name__=="__main__":

    #app.run(host='127.0.0.1', port=5000)
    app.run(host='127.0.0.1', port=5001)

