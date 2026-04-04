#!/usr/bin/env python3
"""Minimal HTTP proxy that logs request/response headers and forwards to upstream proxy."""
import socket
import threading
import selectors
import struct
import gzip
import io

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 8080
UPSTREAM_HOST = "127.0.0.1"
UPSTREAM_PORT = 12334

LOG_CONNECT = True
LOG_REQUEST_LINES = ["patch", "open.apis.im.v1", "content-type", "authorization", "x-lark", "x-funnel"]
LOG_RESPONSE_CODES = ["200", "400", "401", "403", "404", "500"]

def is_target_host(port, host):
    """Check if connection is to Feishu API."""
    if port in [443, 8443]:
        return True
    return False

def handle_client(client_sock, client_addr):
    try:
        request = b""
        while b"\r\n\r\n" not in request:
            data = client_sock.recv(4096)
            if not data:
                return
            request += data

        request_str = request.decode('utf-8', errors='replace')
        lines = request_str.split('\r\n')
        first_line = lines[0] if lines else ""

        # Check if CONNECT (HTTPS tunnel)
        if first_line.startswith("CONNECT "):
            # Extract host:port
            host_port = first_line.split(" ")[1] if len(first_line.split(" ")) > 1 else ""
            host = host_port.split(":")[0] if ":" in host_port else host_port
            port = int(host_port.split(":")[1]) if ":" in host_port else 443

            log_key = f"CONNECT {host}:{port}"
            if LOG_CONNECT:
                print(f"\n{'='*60}")
                print(f"[CONNECT TUNNEL] {host}:{port}")
                print(f"  Client: {client_addr}")
                print(f"{'='*60}")

            # Connect to upstream proxy
            try:
                upstream = socket.create_connection((UPSTREAM_HOST, UPSTREAM_PORT), timeout=10)
                # Send 200 Connection Established to client
                client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

                # Bidirectional pipe with logging
                def pipe_and_log(src, dst, direction, label):
                    buf = b""
                    while True:
                        try:
                            data = src.recv(8192)
                            if not data:
                                break
                            buf += data
                            dst.sendall(data)

                            # Log if it looks like HTTP or headers
                            if len(buf) < 50000 and direction == ">>>":
                                try:
                                    text = buf.decode('utf-8', errors='replace')
                                    if any(k.lower() in text.lower() for k in LOG_REQUEST_LINES):
                                        print(f"\n[{label}] {direction} [{len(data)} bytes]")
                                        for ln in text.split('\r\n')[:50]:
                                            print(f"  {ln}")
                                        # Check for HTTP response
                                        if 'HTTP/1' in text[:20]:
                                            status_line = text.split('\r\n')[0]
                                            print(f"  >>> STATUS: {status_line}")
                                except:
                                    pass
                        except Exception as e:
                            if e.args and e.args[0] not in [104, 32]:
                                pass
                            break
                    try:
                        src.close()
                        dst.close()
                    except:
                        pass

                t1 = threading.Thread(target=pipe_and_log, args=(client_sock, upstream, ">>>", log_key), daemon=True)
                t2 = threading.Thread(target=pipe_and_log, args=(upstream, client_sock, "<<<", log_key), daemon=True)
                t1.start()
                t2.start()
                t1.join()
                t2.join()
            except Exception as e:
                print(f"[-] Upstream connect failed: {e}")
                client_sock.close()
            return

        # Regular HTTP request - log it
        if any(k.lower() in first_line.lower() for k in LOG_REQUEST_LINES):
            print(f"\n{'='*60}")
            print(f"[HTTP REQUEST] {first_line[:100]}")
            for ln in lines[:30]:
                if ln:
                    print(f"  {ln}")
            print(f"{'='*60}")

        # Forward to upstream
        upstream = socket.create_connection((UPSTREAM_HOST, UPSTREAM_PORT), timeout=10)
        upstream.sendall(request)

        # Receive response
        response = b""
        upstream.settimeout(5)
        while True:
            try:
                data = upstream.recv(8192)
                if not data:
                    break
                response += data
            except socket.timeout:
                break

        # Log response
        if response:
            resp_lines = response.decode('utf-8', errors='replace').split('\r\n')[:20]
            if any(s in resp_lines[0] for s in LOG_RESPONSE_CODES if resp_lines):
                print(f"[HTTP RESPONSE] {resp_lines[0][:100]}")
            client_sock.sendall(response)
        upstream.close()
        client_sock.close()

    except Exception as e:
        print(f"[-] Error: {e}")
        try:
            client_sock.close()
        except:
            pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(50)
    print(f"[*] HTTP Proxy listening on {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"[*] Forwarding to upstream {UPSTREAM_HOST}:{UPSTREAM_PORT}")
    print(f"[*] Run: openclaw with HTTP_PROXY=http://127.0.0.1:{LISTEN_PORT}")
    print(f"[*] Press Ctrl+C to stop")

    try:
        while True:
            client_sock, client_addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[*] Stopping...")
    finally:
        server.close()

if __name__ == "__main__":
    main()
