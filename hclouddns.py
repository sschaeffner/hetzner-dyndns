from hcloud import Client, APIException
from hcloud.zones import ZoneRecord, ZoneRRSet

from loguru import logger


class HcloudDns:
    def __init__(self, api_token: str):
        self.client = Client(token=api_token)
        logger.debug("HcloudNew initialised")

    def get_zone(self, zone_name):
        logger.debug("getting zone: {}", zone_name)
        self.client.zones.get(zone_name)

    def set_record(self, zone_name: str, name: str, a: str, ttl: int | None = None):
        logger.debug("setting record in zone={} for name={} to a={} (ttl={})", zone_name, name, a, ttl)
        zone = self.client.zones.get(zone_name)
        try:
            logger.debug("getting rrset for name={}", name)
            rrset = zone.get_rrset(name, "A")
            logger.debug("setting rrset records to a={}...", a)
            action = rrset.set_rrset_records([ZoneRecord(a)])
            action.wait_until_finished()
            logger.debug("...done setting rrset records")
        except APIException as e:
            logger.debug("got exception: {} ({})", e.message, e.code)
            if e.code == "not_found":
                # create new rrset in zone
                logger.debug("creating rrset in zone={} for name={} type=A a={} (ttl={})...", zone_name, name, a, ttl)
                zone.create_rrset(
                    name=name,
                    type='A',
                    ttl=ttl,
                    records=[ZoneRecord(a)]
                )
                logger.debug("...done creating rrset")
            else:
                raise e
