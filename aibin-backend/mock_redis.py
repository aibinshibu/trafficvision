"""
Lightweight in-memory Redis mock server for local development.
Speaks enough RESP to handle GET, SET, SETEX, PING, EXPIRE, DEL without requiring Docker or a native Redis installation.
"""

import socket
import threading
import time

store = {}
expiries = {}

def handle_client(sock):
    buf = b""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            buf += data
            while b"\r\n" in buf:
                lines = buf.split(b"\r\n")
                if buf.startswith(b"*"):
                    # RESP Array
                    try:
                        num_args = int(lines[0][1:])
                        # Need 1 + num_args * 2 lines in total
                        needed = 1 + num_args * 2
                        if len(lines) <= needed:
                            break  # wait for more data
                        args = []
                        for i in range(num_args):
                            args.append(lines[2 + i * 2].decode("utf-8", errors="ignore"))
                        # Consume from buf
                        consumed = sum(len(lines[i]) + 2 for i in range(needed))
                        buf = buf[consumed:]
                        
                        cmd = args[0].upper() if args else ""
                        now = time.time()
                        
                        if cmd == "PING":
                            sock.sendall(b"+PONG\r\n")
                        elif cmd == "GET":
                            key = args[1] if len(args) > 1 else ""
                            if key in expiries and expiries[key] < now:
                                store.pop(key, None)
                                expiries.pop(key, None)
                            val = store.get(key)
                            if val is None:
                                sock.sendall(b"$-1\r\n")
                            else:
                                val_b = val.encode("utf-8") if isinstance(val, str) else val
                                sock.sendall(f"${len(val_b)}\r\n".encode() + val_b + b"\r\n")
                        elif cmd == "SET":
                            key = args[1]
                            val = args[2]
                            store[key] = val
                            sock.sendall(b"+OK\r\n")
                        elif cmd == "SETEX":
                            key = args[1]
                            seconds = float(args[2])
                            val = args[3]
                            store[key] = val
                            expiries[key] = now + seconds
                            sock.sendall(b"+OK\r\n")
                        elif cmd == "DEL":
                            for k in args[1:]:
                                store.pop(k, None)
                                expiries.pop(k, None)
                            sock.sendall(b":1\r\n")
                        else:
                            sock.sendall(b"+OK\r\n")
                    except Exception as e:
                        sock.sendall(b"+OK\r\n")
                        buf = b""
                else:
                    # Inline command
                    line = lines[0].decode("utf-8", errors="ignore").strip()
                    buf = b"\r\n".join(lines[1:])
                    parts = line.split()
                    if not parts:
                        continue
                    cmd = parts[0].upper()
                    if cmd == "PING":
                        sock.sendall(b"+PONG\r\n")
                    else:
                        sock.sendall(b"+OK\r\n")
        except Exception:
            break
    try:
        sock.close()
    except Exception:
        pass

def run_server(port=6379):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port))
    s.listen(128)
    print(f"Mock Redis cache listening on 127.0.0.1:{port}...", flush=True)
    while True:
        client_sock, _ = s.accept()
        t = threading.Thread(target=handle_client, args=(client_sock,), daemon=True)
        t.start()

if __name__ == "__main__":
    run_server()
