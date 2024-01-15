import dns.resolver
from dns import rdatatype
from dns.rdatatype import RdataType

from loguru import logger


def get_soa_mname(qname: str, resolver: str = "8.8.8.8"):
    query = dns.message.make_query(qname, dns.rdatatype.SOA)
    response = dns.query.udp(query, resolver)

    logger.trace(f"response: {response}")
    logger.debug(f"response authority: {list(response.authority)}")

    soa = response.authority[0]
    mname = soa[0].mname.to_text()
    logger.debug(f"mname={mname}")

    return mname


def resolve(
        qname: str,
        resolver: str,
        r_data_type: RdataType = dns.rdatatype.A
) -> list[str] | None:
    query = dns.message.make_query(qname, r_data_type)
    response = dns.query.udp(query, resolver)

    rcode = response.rcode()
    if rcode != dns.rcode.NOERROR:
        if rcode == dns.rcode.NXDOMAIN:
            logger.warning(f"{qname} does not exist (NXDOMAIN).")
            return None
        else:
            raise Exception(f"Error: {dns.rcode.to_text(rcode)}")

    logger.debug(f"resolved qname={qname} type={rdatatype.to_text(r_data_type)} @{resolver} to {response.answer}")

    if len(response.answer) > 0:
        rrset = response.answer[0]
        return [rr.to_text() for rr in rrset]

    return None
