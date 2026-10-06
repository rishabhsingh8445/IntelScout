"""Validate URLs before server-side HTTP fetches (SSRF mitigation)."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

ALLOWED_SCHEMES = frozenset({"http", "https"})
BLOCKED_HOSTNAMES = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "::1"})


def _is_blocked_ip(ip: ipaddress._BaseAddress) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _resolve_host_ips(hostname: str) -> list[ipaddress._BaseAddress]:
    try:
        infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return []
    ips: list[ipaddress._BaseAddress] = []
    for info in infos:
        sockaddr = info[4]
        if not sockaddr:
            continue
        ip_str = sockaddr[0]
        try:
            ips.append(ipaddress.ip_address(ip_str))
        except ValueError:
            continue
    return ips


def is_safe_http_url(url: str, *, resolve_dns: bool = True) -> bool:
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if len(url) > 2048:
        return False
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False
    if parsed.username or parsed.password:
        return False
    hostname = (parsed.hostname or "").lower().strip(".")
    if not hostname:
        return False
    if hostname in BLOCKED_HOSTNAMES:
        return False
    if hostname.endswith(".local") or hostname.endswith(".internal"):
        return False
    try:
        literal = ipaddress.ip_address(hostname)
        if _is_blocked_ip(literal):
            return False
    except ValueError:
        pass
    if resolve_dns:
        for ip in _resolve_host_ips(hostname):
            if _is_blocked_ip(ip):
                return False
    return True
