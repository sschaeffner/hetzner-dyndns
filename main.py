#!/usr/bin/env python3

import json
import os
import sys
import time

import dns
from loguru import logger

from dns_query import get_soa_mname, resolve
from hetzner import HetznerIp
from hclouddns import HcloudDns


def find_or_none(iterable):
    for element in iterable:
        return element
    return None


def set_a(zone_name: str, domain: str, a: str, ttl: int | None = None):
    name = domain.split(zone_name)[0][:-1]
    logger.debug(f"calculated name: {name}")

    hc = HcloudDns(token)
    hc.set_record(zone_name, name, a, ttl)


def get_current(qname: str) -> tuple[str | None, str | None]:
    soa_mname = get_soa_mname(qname)

    authoritative_ip4 = resolve(soa_mname, "8.8.8.8")[0]
    logger.debug(f"authoritative ip4: {authoritative_ip4}")

    current_a = resolve(qname, authoritative_ip4)
    current_aaaa = resolve(qname, authoritative_ip4, dns.rdatatype.AAAA)

    if current_a:
        if len(current_a) > 1:
            raise ValueError(
                f"Has multiple existing A records: {current_a}."
            )
        else:
            current_a = current_a[0]

    if current_aaaa:
        if len(current_aaaa) > 1:
            raise ValueError(
                f"Has multiple existing AAAA records: {current_aaaa}."
            )
        else:
            current_aaaa = current_aaaa[0]

    return current_a, current_aaaa


def get_actual_a():
    return HetznerIp().get_ip4()


def get_actual_aaaa():
    return HetznerIp().get_ip6()


def _get_env(name: str, default: str | None = None) -> str:
    var = os.environ.get(name)

    if not var:
        if default is not None:
            return default
        else:
            logger.error(f"{name} environment variable not set. Exiting.")
            sys.exit(2)

    return var


if __name__ == '__main__':
    logger.info("hello, world")

    token = _get_env("TOKEN")
    zone_name = _get_env("ZONE_NAME")
    domain = _get_env("DOMAIN")
    ttl = _get_env("TTL", default="")

    # TTL is optional, default is the zone TTL
    if ttl == "":
        ttl = None
    else:
        ttl = int(ttl)

    current_a, current_aaaa = get_current(domain)
    logger.debug(f"current A: {current_a}")
    logger.debug(f"current AAAA: {current_aaaa}")

    actual_a = None
    try_nr = 0
    while actual_a is None and try_nr < 5:
        try_nr += 1
        try:
            actual_a = get_actual_a()
            logger.debug(f"actual IPv4: {actual_a}")
        except RuntimeError as e:
            logger.warning(f"error while getting IPv4: {e}")
            time.sleep(1)

    # actual_aaaa = None
    # try_nr = 0
    # while actual_aaaa is None and try_nr < 5:
    #     try_nr += 1
    #     try:
    #         actual_aaaa = get_actual_aaaa()
    #         logger.debug(f"actual IPv6: {actual_aaaa}")
    #     except RuntimeError as e:
    #         logger.warning(f"error while getting IPv6: {e}")
    #         time.sleep(1)

    logger.info(f"current A (from DNS) is {current_a}, actual A is {actual_a}")

    if current_a != actual_a:
        logger.info(f"updating DNS A to {actual_a}...")
        set_a(zone_name, domain, actual_a, ttl)
    else:
        logger.info("DNS up to date")
