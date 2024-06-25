#include <yarrp.h>

class Stats {
    public:
    Stats() : count(0), to_probe(0), nbr_skipped(0), bgp_skipped(0),
              ttl_outside(0), bgp_outside(0), adr_outside(0), baddst(0),
              fills(0) {
      gettimeofday(&start, NULL);
    };
    void terse() {
      terse(stderr);
    }
    void terse(FILE *out) {
      gettimeofday(&end, NULL);
      float t = (float) tsdiff(&end, &start) / 1000.0;
      fprintf(out, "# Pkts: %" PRId64 " Fill: %" PRId64,
        count, fills);    
      fprintf(out, " in: %2.1fs (%2.1f pps)\n",
        t, (float) count / t);
    };
    void dump(FILE *out) {
      gettimeofday(&end, NULL);
      float t = (float) tsdiff(&end, &start) / 1000.0;
      // RFC2822 timestring
      struct tm *p = localtime(&(end.tv_sec));
      char s[1000];
      strftime(s, 1000, "%a, %d %b %Y %T %z", p);
      fprintf(out, "# End: %s\n", s);
      fprintf(out, "# Bad_Resp: %" PRId64 "\n", baddst);
      fprintf(out, "# Fills: %" PRId64 "\n", fills);
      // fprintf(out, "# Outside_TTL: %" PRId64 "\n", ttl_outside);
      // fprintf(out, "# Outside_BGP: %" PRId64 "\n", bgp_outside);
      // fprintf(out, "# Outside_Addr: %" PRId64 "\n", adr_outside);
      // fprintf(out, "# Skipped_Nbr: %" PRId64 "\n", nbr_skipped);
      // fprintf(out, "# Skipped_BGP: %" PRId64 "\n", bgp_skipped);
      fprintf(out, "# Pkts: %" PRId64 "\n", count);
      fprintf(out, "# Elapsed: %2.2fs\n", t);
      fprintf(out, "# PPS: %2.2f\n", (float) count / t);
      fprintf(out, "#\n");
    };
    
    uint64_t count;       // number of probes sent
    uint64_t to_probe;
    uint64_t nbr_skipped; // b/c already in learned neighborhood 
    uint64_t bgp_skipped; // b/c BGP learned
    uint64_t ttl_outside; // b/c outside range of TTLs we want
    uint64_t bgp_outside; // b/c not in BGP table
    uint64_t adr_outside; // b/c address outside range we want
    uint64_t baddst;      // b/c checksum invalid on destination in reponse
    uint64_t fills;       // extra tail probes past maxttl
   
    struct timeval start;
    struct timeval end;
};
