"""
- CS2911 - 021
- Fall 2020
- Lab 4 - TCP
- Names:
  - Collin Quinn
  - Nigel Nelson

A simple TCP server/client pair.

The application protocol is a simple format: For each file uploaded, the client
first sends four (big-endian) bytes indicating the number of lines as an unsigned binary number.

The client then sends each of the lines, terminated only by '\\n' (an ASCII LF byte).

The server responds with 'A' if it accepts the file, and 'R' if it rejects it.

Then the client can send the next file.
"""
"""
Introduction:
=============
This lab is a TCP server/client pair; see description above

What we learned:
================
- Linking client to a server  
- Hands-on principles for TCP connections
- Running Python 'in parallel'
- Refactoring code to align with updated requirements

Things that could be improved or that we liked: (Required)
==========================================================
- Improve 'Procedure - At home Testing' part of lab description
- Ensure class understands functionality of a socket is before starting lab
"""

# import the 'socket' module -- not using 'from socket import *' in order to selectively use items
# with 'socket.' prefix
import socket
import sys
import time

# Port number definitions
# (May have to be adjusted if they collide with ports in use by other programs/services.)
TCP_PORT = 12100

# Address to listen on when acting as server.
# The address '' means accept any connection for our 'receive' port from any network interface
# on this system (including 'localhost' loopback connection).
LISTEN_ON_INTERFACE = ''

# Address of the 'other' ('server') host that should be connected to for 'send' operations.
# When connecting on one system, use 'localhost'
# When 'sending' to another system, use its IP address (or DNS name if it has one)
# OTHER_HOST = '155.92.x.x'
OTHER_HOST = 'localhost'


def main():
    """
    Allows user to either send or receive bytes
    """
    # Get chosen operation from the user.
    action = input('Select "(1-TS) tcpsend", or "(2-TR) tcpreceive":')
    # Execute the chosen operation.
    if action in ['1', 'TS', 'ts', 'tcpsend']:
        tcp_send(OTHER_HOST, TCP_PORT)
    elif action in ['2', 'TR', 'tr', 'tcpreceive']:
        tcp_receive(TCP_PORT)
    else:
        print('Unknown action: "{0}"'.format(action))


def tcp_send(server_host, server_port):
    """
    - Send multiple messages over a TCP connection to a designated host/port
    - Receive a one-character response from the 'server'
    - Print the received response
    - Close the socket

    :param str server_host: name of the server host machine
    :param int server_port: port number on server to send to
    """
    print('tcp_send: dst_host="{0}", dst_port={1}'
          .format(server_host, server_port))
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((server_host, server_port))

    num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    while num_lines != 0:
        print('Now enter all the lines of your message')
        # This client code does not completely conform to the specification.
        #
        # In it, I only pack one byte of the range, limiting the number of lines this
        # client can send.
        #
        # While writing tcp_receive, you will need to use a different approach to unpack
        # to meet the specification.
        #
        # Feel free to upgrade this code to handle a higher number of lines, too.
        tcp_socket.sendall(b'\x00\x00')
        time.sleep(1)  # Just to mess with your servers. :-)
        tcp_socket.sendall(b'\x00' + bytes((num_lines,)))

        # Enter the lines of the message. Each line will be sent as it is entered.
        for line_num in range(0, num_lines):
            line = input('')
            tcp_socket.sendall(line.encode() + b'\n')

        print('Done sending. Awaiting reply.')
        response = tcp_socket.recv(1)
        if response == b'A':  # Note: == in Python is like .equals in Java
            print('File accepted.')
        else:
            print('Unexpected response:', response)

        num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    tcp_socket.sendall(b'\x00\x00')
    time.sleep(1)  # Just to mess with your servers. :-)  Your code should work with this line here.
    tcp_socket.sendall(b'\x00\x00')
    response = tcp_socket.recv(1)
    if response == b'Q':  # Reminder: == in Python is like .equals in Java
        print('Server closing connection, as expected.')
    else:
        print('Unexpected response:', response)

    tcp_socket.close()


def read_line(data_socket):
    """
    parses out one line from the message
    :param: data_socket: The socket to read from
    :return: decoded line as a bytes object
    :author: Collin Quinn
    """

    character = next_byte(data_socket)
    line = character
    while not (character.decode('ASCII') == '\n'):
        character = next_byte(data_socket)
        line += character
    return line


def server_respond(data_socket, single_letter):
    data_socket.send(single_letter.encode("ASCII"))


def tcp_receive(listen_port):
    """
    - Listen for a TCP connection on a designated "listening" port
    - Accept the connection, creating a connection socket
    - Print the address and port of the sender
    - Repeat until a zero-length message is received:
      - Receive a message, saving it to a text-file (1.txt for first file,
      2.txt for second file, etc.)
      - Send a single-character response 'A' to indicate that the upload was accepted.
    - Send a 'Q' to indicate a zero-length message was received.
    - Close data connection.

    :param int listen_port: Port number on the server to listen on
    :author: Collin Quinn and Nigel Nelson
    """

    print('tcp_receive (server): listen_port={0}'.format(listen_port))
    data_socket, sender_address, listen_socket = make_connection(listen_port)
    file_number = 0
    num_of_lines = read_header(data_socket)
    while not num_of_lines == 0:
        message = read_text(data_socket, num_of_lines)
        server_respond(data_socket, 'A')
        file_number += 1
        write_message(message, str(file_number))
        num_of_lines = read_header(data_socket)
    server_respond(data_socket, 'Q')
    data_socket.close()
    listen_socket.close()


def read_text(data_socket, number_of_lines):
    """
    Reads text of entire message and writes it to a .txt file
    :return: Bytes message: message from the socket
    :param: data_socket: The socket to read from
    :param: number_of_lines: number of lines in the message
    :author: Collin Quinn
    """

    message = b''
    for x in range(number_of_lines):
        message += read_line(data_socket)
    return message


def read_header(data_socket):
    """
      This method reads the header to return an int representing the length of the body
      :param: data_socket: the socket to read from
      :return: int representing the number of lines in a message
      :author: Collin Quinn
      """

    header_contents = b''
    for x in range(0, 4):
        header_contents += next_byte(data_socket)

    return int.from_bytes(header_contents, 'big')


def write_message(message, file_number):
    """
     This method takes the message body as a bytes object as an argument,
     and saves it to a file
     :param: Bytes  message: entire message as a bytes object
     :param: str file_number: file number i.e. '1', '2', etc.
     :return: void
     :author: Nigel Nelson
     """

    with open(file_number + '.txt', 'wb') as output_file:
        output_file.write(message)

    output_file.close()


def next_byte(data_socket):
    """
    Read the next byte from the socket data_socket.

    Read the next byte from the sender, received over the network.
    If the byte has not yet arrived, this method blocks (waits)
      until the byte arrives.
    If the sender is done sending and is waiting for your response, this method blocks indefinitely.

    :param data_socket: The socket to read from. The data_socket argument should be an open tcp
                        data connection (either a client socket or a server data socket), not a tcp
                        server's listening socket.
    :return: the next byte, as a bytes object with a single byte in it
    :author: provided in lab
    """
    return data_socket.recv(1)


def make_connection(listen_port):
    """
      This method takes the complete message in hexadecimal shorthand as an argument,
       and only reads the header to return an int representing the length
       of the body
      :param listen_port: The receiving port number
      :return: data_socket: the connection socket object
      :return: sender_address: address of socket on the other end of the connection
      :return: listen_socket: socket waiting for incoming connection attempts
      :author: Nigel Nelson
      """

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind((LISTEN_ON_INTERFACE, listen_port))
    listen_socket.listen(1)  # Num of conn. to accept
    data_socket, sender_address = listen_socket.accept()
    return data_socket, sender_address, listen_socket


# Invoke the main method to run the program.
main()
