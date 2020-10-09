# Network-Protocols
Lab 4
A simple TCP server/client pair.
The application protocol is a simple format: For each file uploaded, the client
first sends four (big-endian) bytes indicating the number of lines as an unsigned binary number.
The client then sends each of the lines, terminated only by '\\n' (an ASCII LF byte).
The server responds with 'A' if it accepts the file, and 'R' if it rejects it.
Then the client can send the next file.
