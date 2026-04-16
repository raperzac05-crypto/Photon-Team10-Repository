import socket
import threading


# Default network address (can be changed via set_network_address())
network_address = "127.0.0.1"
broadcast_port = 7500   # Port used to broadcast/transmit data to players
receive_port = 7501     # Port used to receive data from players
buffer_size = 1024

transmit_socket = None
receive_socket = None

def set_network_address(new_address):
    """Change the network address used for broadcasting."""
    global network_address
    network_address = new_address
    print(f"Network address updated to {network_address}")

def create_udp_sockets():
    """Create and return the broadcast and receive UDP sockets."""
    # Transmit socket – sends data to players on broadcast_port
    global transmit_socket, receive_socket
    transmit_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    transmit_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Receive socket listens on receive_port, bound to all interfaces (0.0.0.0)
    receive_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    receive_socket.bind(("0.0.0.0", receive_port))

    print(f"Transmit socket ready  -> {network_address}:{broadcast_port}")
    print(f"Receive  socket ready  -> 0.0.0.0:{receive_port}")
    return transmit_socket, receive_socket

def broadcast_message(message):
    """Send a message to all players via the broadcast socket."""
    data = message.encode('utf-8')
    transmit_socket.sendto(data, (network_address, broadcast_port))

def receive_message():
    """Block until a message arrives on the receive socket and return (data, address)."""
    data, addr = receive_socket.recvfrom(buffer_size)
    return data.decode('utf-8'), addr

def udp_listener():
	"""Background thread that continuously listens for incoming UDP messages."""
	print("UPD listener started")
	while True:
		try:
			message, addr = receive_message()
			print(f"Received: {message} from {addr}")
		except Exception as e:
			print(f"UDP error: {e}")
			break
			
def close_sockets():
	global transmit_socket, receive_socket
	if transmit_socket:
		transmit_socket.close()
	if receive_socket:
		receive_socket.close()

# Create the two UDP sockets
create_udp_sockets()

listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()
