# @info: requests must be in a maximum of 5 threads

# class to save clients numbers
@dataclass
class Numbers:
    id: str
    number: str

# Delay in seconds to send message to client
def random_delay():
    # @todo: create a number randomizer between 1 and 20

# Add a tag to client number
def add_tag(str num):
    # @todo: create a function to add tags called 'Jhony' to numbers

# Get number of current client id
def get_number(str id):
    # @todo: create a function to requests numbers of current id

# search clients and save their numbers in a simple database
def get_clients():
    get_number("")
    # @todo: this should get id of clients
    # @todo: and get numbers of ids

# send messages to all users in the database
# database with numbers should exist
def send_messages():
    add_tag("")
    # @todo: create a function to send messages
    # @> messages need be send in random times between 1s and 20s

def main():
    # @info: should send messages from json database
    get_clients()
    send_messages()

if '__name__' == __main__:
    main()
