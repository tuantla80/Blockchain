"""
- It is a Python code to demonstrate some basic concepts of blockchain to understand some technical aspects internally.
  Therefore, it is far from a final product.

- Three main concepts of blockchain will be demonstrated in this Python code:
  (1) Blockchain itself
  (2) Peer to peer network
  (3) Consensus mechanism

- I used Anaconda3, which includes the following libraries that use in this Python code: hashlib, requests, flask.
  Anaconda3 also provides the Python 3.6 and many other useful libraries such as pandas, numpy, matplotlib.
  
  You may install any latest versions easily, such as for request library:   $pip install requests.

- I used Postman (https://www.getpostman.com/) for HTTP client.

- Furthermore, it is also worth to note that the Python code here is implemented by me after reviewing and
 making use of some open source codes. Thus this code is used for my learning purposes ONLY.

- Version: 0.0
- Date: 180322
"""

import requests
import hashlib
from time import time
import json

from network import Node

# The below global variables may be stored in a single file, such as "global.py"
# A block is implemented as a dictionary with a list of keys as below.
_index = 'index' # it is index of a block. In this code, the fist index is 1 (for genesis block)
_timestamp = 'timestamp' # a time stamp
_transactions = 'transactions' # in this example code is transaction. But generally it is any data included in the block.
_previous_hash = 'previous_hash' # a reference to the hash of previous block
_proof = 'proof' # proof is given by a proof of work algorithm

# A transaction as mentioned above is implemented as a dictionary with a list of keys as below.
_sender = 'sender' # a sender
_recipient = 'recipient' # a recipient
_amount = 'amount' # an amount of cryptocurrency


class Blockchain(Node):


    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_new_block(previous_hash='1', proof=999) # At the first time, it will generate a genesis block


    def create_new_block(self, previous_hash='1', proof=999):
        """
        To create a new block and append to chain

        Parameters:
        ----------
        previous_hash:
        proof

        Returns
        -------
        A new block: a dictionary

        Examples
        --------
        """
        block = {
            _index: len(self.chain) + 1, # in blockchain, each block is stored with a timestamp and an optional index
                                         # In this simple blockchain code, we store both
            _timestamp: time(),
            _transactions: self.current_transactions,
            _previous_hash: previous_hash or self.hash(self.chain[-1]),
            _proof: proof,
            }

        self.chain.append(block)  # add new block to chain
        self.current_transactions = [] # reset transaction list
        return block


    def create_new_transaction(self, sender, recipient, amount):
        '''
        To  create a new transaction for the next mined block
        '''

        new_transaction = {_sender: sender,
                           _recipient: recipient,
                           _amount: amount} # it is a JSON type to be used at POST request

        self.current_transactions.append(new_transaction)
        next_index = self.last_block[_index] + 1
        return next_index


    @property
    def last_block(self):
        return self.chain[-1]


    @staticmethod
    def generate_hash(block):
        """
        To generate a SHA-256 hash of a block
        print('hashlib.algorithms_available', hashlib.algorithms_available)
        print('hashlib.algorithms_guaranteed', hashlib.algorithms_guaranteed)

        Parameters:
        ----------
        block:

        Returns
        -------
        a hash:
        """

        # Need to sort key to make sure we have the consistent hash
        block_str = json.dumps(block, sort_keys=True).encode()  #print('block_str', block_str)
        hash_hex = hashlib.sha256(block_str).hexdigest()  # print('hash_hex', hash_hex)
        return hash_hex


    @staticmethod
    def check_valid_proof(last_proof, proof, last_hash, leading_zeros='0000'):
        """
        To check valid proof.
        In this case, we assumed hash has a series of four 0 at the beginning.
        """
        # str.encode() Return an encoded version of the string as a bytes object. Default encoding is 'utf-8'
        # https://docs.python.org/3/library/stdtypes.html#str.encode
        # a new kind of string literals in Python 3.6: f-strings, or formatted string literals.
        # name = "Fred"
        # f"He said his name is {name}."  --> 'He said his name is Fred.'

        predict = f'{last_proof}{proof}{last_hash}'.encode()  # print('predict', predict)
        predict_hash = hashlib.sha256(predict).hexdigest()  # print('predict_hash', predict_hash)

        if predict_hash.startswith(leading_zeros):
            print('\n At check_valid_proof(): ')
            print('last_proof=%s, proof=%s, last_hash=%s' % (last_proof, proof, last_hash))
            print('predict_hash', predict_hash)
        return predict_hash.startswith(leading_zeros)


    def implement_proof_of_work(self, last_block, leading_zeros='0000'):

        """
        In this code, we use a Proof of Work Algorithm as below:
        - Find a number P' such that hash(PP'Previous_hash) contains leading 4 zeroes
        - Where P is the previous proof, P' is the new proof and Previous_hash is a previous hash
        """
        last_proof = last_block[_proof]; print('last_proof', last_proof)
        last_hash = self.generate_hash(last_block); print('last_hash', last_hash)

        proof = 0
        while self.check_valid_proof(last_proof=last_proof,
                                     proof=proof, # mean new proof
                                     last_hash=last_hash,
                                     leading_zeros=leading_zeros) is False:
            proof +=1
        # End of while
        print('last_proof=%s, proof=%s' %(last_proof, proof))
        return proof


    def check_valid_chain(self, chain, leading_zeros='0000'):
        """
        To check whether a chain is valid or not

        Return: True or False
        """

        last_block = chain[0] # here is genesis block. print('last_block', last_block)
        current_index = last_block[_index]  # print('current_index', current_index)
        if current_index != 1:
            raise ValueError ('The index of genesis block need to be 1')

        while current_index < len(chain):
            block = chain[current_index] # Since the index of chain begins from 0
            print('at check_valid_chain(), last block = ', f'{last_block}')
            print('at check_valid_chain(), block = ', f'{block}')

            # Check if the hash of the block is correct
            if block[_previous_hash] != self.generate_hash(last_block):
                print('\n ----- Error at check_valid_chain(): Checking hash condition -----')
                return False

            # Check if the proof of work is correct
            print('at check_valid_chain(), proof of last_block: ', last_block[_proof])
            print('at check_valid_chain(), proof of this block: ', block[_proof])  #
            print('at check_valid_chain(), previous_hash of last block: ', last_block[_previous_hash])
            print('at check_valid_chain(), leading_zeros: ', leading_zeros)
            if not self.check_valid_proof(last_proof=last_block[_proof],
                                          proof=block[_proof],
                                          last_hash=block[_previous_hash],
                                          leading_zeros = leading_zeros):
                print('\n ----- Error at check_valid_chain(): Checking valid proof condition -----')
                return False

            last_block = block
            current_index += 1
        # End of while
        return True


    def resolve_conflicts(self, node):
        """
        In this code, the consensus algorithm to resolves conflicts is to replace our chain with the longest one
        in the network.

        Example. peer_nodes = ["http://127.0.0.1:5000", "http://127.0.0.1:5001", "http://127.0.0.1:5002"]

        return: if our chain was replaced: True
                else: False
        """
        nodes_in_network = node.nodes; print('nodes_in_network', nodes_in_network)
        chosen_chain = None

        max_length_chain = len(self.chain); print('length_chain of current node = ', max_length_chain)

        for _node in nodes_in_network:
            print('_node here', f'http://{_node}/chain')
            response = requests.get(f'http://{_node}/chain')
            print('response', response)
            if response.status_code == 200: # normal
                length_chain = response.json()['length of chain']; print('length_chain at node ban be =',length_chain )
                chain = response.json()['chain']

                if (length_chain > max_length_chain) and self.check_valid_chain(chain):# (test 1 and test 2)
                    max_length_chain = length_chain
                    chosen_chain = chain
                else: pass
            else: pass
        # End of for

        if chosen_chain:
            self.chain = chosen_chain
            return True # conflict and then update longest chain
        else:
            return False


def test_class_Blockchain():
    '''
    This function is to test class Blockchain
    '''
    blockchain = Blockchain()

    print('\n ----- The chain at the beginning -----')
    print('The genisis of blockchain = ', blockchain.chain)
    print('The fist transaction of blockchain = ', blockchain.current_transactions)

    print('\n ----- The chain after creating new block  -----')
    previous_hash = blockchain.generate_hash(block=blockchain.chain[0])
    proof = blockchain.implement_proof_of_work(last_block=blockchain.last_block)
    block = blockchain.create_new_block(previous_hash= previous_hash, proof=proof)
    next_index = blockchain.create_new_transaction(sender='AA', recipient='BB', amount=10.0)
    hash_key = blockchain.generate_hash(block)
    print('The second block of blockchain = ', block)
    print('The chain after adding new block = ', blockchain.chain)
    print('The transaction at second block of blockchain = ', blockchain.current_transactions)
    print('hash key of the second block', hash_key)
    print('next_index = ', next_index)

    # Test implement_proof_of_work
    last_block = blockchain.last_block
    proof = blockchain.implement_proof_of_work(last_block=last_block)
    print('\n proof', proof)

    # test check_valid_chain()
    print('\n blockchain.check_valid_chain', blockchain.check_valid_chain(chain=blockchain.chain))

    # Test resolve conflict
    node = Node()
    print('\n blockchain.resolve_conflicts()', blockchain.resolve_conflicts(node=node))
    #blockchain.resolve_conflicts()


if __name__=='__main__':
    test_class_Blockchain()