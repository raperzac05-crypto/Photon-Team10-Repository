import socket

NETWORK_ADDRESS = "127.0.0.1"
BROADCAST_PORT = 7500
RECEIVE_PORT = 7501
BUFFER_SIZE = 1024


def set_network_address(new_address: str):
    """
    Update the network address used for outgoing UDP packets.
    """
    global NETWORK_ADDRESS
    NETWORK_ADDRESS = new_address.strip()


def create_udp_sockets():
    """
    Create transmit and receive UDP sockets.

    Transmit socket:
      sends packets to NETWORK_ADDRESS:BROADCAST_PORT

    Receive socket:
      listens on 0.0.0.0:RECEIVE_PORT
    """
    transmit_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    transmit_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    receive_socket.bind(("0.0.0.0", RECEIVE_PORT))

    return transmit_socket, receive_socket


def broadcast_message(transmit_socket: socket.socket, message: str):
    """
    Send one UDP message.
    """
    data = message.encode("utf-8")
    transmit_socket.sendto(data, (NETWORK_ADDRESS, BROADCAST_PORT))


def receive_message(receive_socket: socket.socket):
    """
    Block until one UDP message is received.
    Returns: (decoded_message, sender_address)
    """
    data, addr = receive_socket.recvfrom(BUFFER_SIZE)
    return data.decode("utf-8"), addr


def close_sockets(transmit_socket=None, receive_socket=None):
    """
    Close sockets safely.
    """
    if transmit_socket is not None:
        transmit_socket.close()
    if receive_socket is not None:
        receive_socket.close()
