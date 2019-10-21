import operator
import random

import dns.name
import dns.exception
import dns.resolver
import dns.rdataclass
import dns.rdatatype

try:
    from ipapython.dnsutil import query_srv
except ImportError:
    def _mix_weight(records):
        """Weighted population sorting for records with same priority
        """
        # trivial case
        if len(records) <= 1:
            return records

        # Optimization for common case: If all weights are the same (e.g. 0),
        # just shuffle the records, which is about four times faster.
        if all(rr.weight == records[0].weight for rr in records):
            random.shuffle(records)
            return records

        noweight = 0.01  # give records with 0 weight a small chance
        result = []
        records = set(records)
        while len(records) > 1:
            # Compute the sum of the weights of those RRs. Then choose a
            # uniform random number between 0 and the sum computed
            # (inclusive).
            urn = random.uniform(0, sum(rr.weight or noweight
                                 for rr in records))
            # Select the RR whose running sum value is the first in the
            # selected order which is greater than or equal to the random
            # number selected.
            acc = 0.
            for rr in records.copy():
                acc += rr.weight or noweight
                if acc >= urn:
                    records.remove(rr)
                    result.append(rr)
        if records:
            result.append(records.pop())
        return result

    def sort_prio_weight(records):
        """RFC 2782 sorting algorithm for SRV and URI records

        RFC 2782 defines a sorting algorithms for SRV records, that is also
        used for sorting URI records. Records are sorted by priority and
        than randomly shuffled according to weight.

        This implementation also removes duplicate entries.
        """
        # order records by priority
        records = sorted(records, key=operator.attrgetter("priority"))

        # remove duplicate entries
        uniquerecords = []
        seen = set()
        for rr in records:
            # A SRV record has target and port, URI just has target.
            target = (rr.target, getattr(rr, "port", None))
            if target not in seen:
                uniquerecords.append(rr)
                seen.add(target)

        # weighted randomization of entries with same priority
        result = []
        sameprio = []
        for rr in uniquerecords:
            # add all items with same priority in a bucket
            if not sameprio or sameprio[0].priority == rr.priority:
                sameprio.append(rr)
            else:
                # got different priority, shuffle bucket
                result.extend(_mix_weight(sameprio))
                # start a new priority list
                sameprio = [rr]
        # add last batch of records with same priority
        if sameprio:
            result.extend(_mix_weight(sameprio))
        return result

    def query_srv(qname, resolver=None, **kwargs):
        """Query SRV records and sort reply according to RFC 2782

        :param qname: query name, _service._proto.domain.
        :return: list of dns.rdtypes.IN.SRV.SRV instances
        """
        if resolver is None:
            resolver = dns.resolver
        answer = resolver.query(qname, rdtype=dns.rdatatype.SRV, **kwargs)
        return sort_prio_weight(answer)
