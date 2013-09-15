#! /usr/bin/env python

import socket
import sys

DEFAULT_PORT   = 6789
DEFAULT_BUFFER = 4096

MODE_CONNECT = 0
MODE_LISTEN  = 1


def main():
    # Determine whether to connect to a client or wait for a connection
    mode = getChatMode()
    if mode == MODE_CONNECT:
        sock = connectToHost()
    else:
        sock = listenForConnection()

    # Start the message loop until EOF is reached
    enterMessageLoop(sock, mode)

    # Close the socket properly before exiting
    print "Ending chat"
    closeSocket(sock)


def getChatMode():
    while True:
        try:
            mode = int(raw_input("1. Connect to host\n2. Listen for connection\n> "))
            mode -= 1
            if mode == MODE_CONNECT or mode == MODE_LISTEN:
                return mode
        except (EOFError, KeyboardInterrupt):
            # If EOF or keyboard interrupt, exit program
            sys.exit(0)
        except ValueError:
            # If non-integer was given, prompt again
            pass
        print "Invalid option"


def connectToHost():
    # Get the host to connect to
    host = raw_input("Host: ")
    print "Connecting to %s..." % (host)

    # Create a new TCP socket to connect to the host with
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the given host on the default port
        sock.connect((host, DEFAULT_PORT))
    except socket.error as err:
        print "Error connecting to host: %s" % (str(err))
        sys.exit(1)

    print "Connected to %s" % (host)
    return sock


def listenForConnection():
    # Create a new TCP socket to accept connections on
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Allow the socket to be re-used without waiting for the timeout period to expire
        serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to all addresses on the default port
        serverSock.bind(('0.0.0.0', DEFAULT_PORT))

        # Listen on the default port with a max backlog of 10
        serverSock.listen(10)
    except socket.error as err:
        print "Failed to start server: %s" % (str(err))
        sys.exit(1)

    # Accept loop
    while True:
        # Wait for a client to connect
        print "Waiting for client..."
        (clientSock, clientAddr) = serverSock.accept()
        print "Got connection: " + str(clientAddr[0])
        
        # Once a client is connected, close the server socket since we only support one client
        closeSocket(serverSock)
        return clientSock


def enterMessageLoop(sock, mode):
    # The connecting client sends first so send/recv in the correct
    # order as determined by the selected mode
    while True:
        if mode == MODE_CONNECT:
            sendMessage(sock)
            recvMessage(sock)
        else:
            recvMessage(sock)
            sendMessage(sock)


def sendMessage(sock):
    try:
        message = raw_input("> ")
        sock.send(message)
    except (EOFError, KeyboardInterrupt):
        # Catch and ignore EOF and keyboard interrupts
        closeSocket(sock)
        sys.exit(0)


def recvMessage(sock):
    print "Waiting for response..."
    response = sock.recv(DEFAULT_BUFFER)

    # If the response is empty, the client closed the connection
    if response == "":
        print "Client closed connection."
        closeSocket(sock)
        sys.exit(0)

    print "Response: %s" % (response)


def closeSocket(sock):
    # Shutdown the socket from both reading and writing and then close the socket
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


if __name__ == '__main__':
    main()
