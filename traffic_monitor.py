from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet
from ryu.lib import hub
import datetime, json

MONITOR_INTERVAL = 3
REPORT_FILE = "/home/harshith-s-b/sdn_project/traffic_report.json"

class TrafficMonitor(app_manager.RyuApp):
OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

```
def __init__(self, *args, **kwargs):
    super(TrafficMonitor, self).__init__(*args, **kwargs)
    self.mac_to_port = {}
    self.datapaths = {}
    self.flow_stats = {}
    self.port_stats = {}
    self.monitor_thread = hub.spawn(self._monitor_loop)

@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
def switch_features_handler(self, ev):
    datapath = ev.msg.datapath
    self.datapaths[datapath.id] = datapath
    self.mac_to_port.setdefault(datapath.id, {})
    self._install_table_miss(datapath)

@set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
def state_change_handler(self, ev):
    datapath = ev.datapath
    if ev.state == MAIN_DISPATCHER:
        self.datapaths[datapath.id] = datapath
    elif ev.state == DEAD_DISPATCHER:
        self.datapaths.pop(datapath.id, None)

def _install_table_miss(self, datapath):
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    match = parser.OFPMatch()
    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
    self._add_flow(datapath, 0, match, actions)

@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def packet_in_handler(self, ev):
    msg = ev.msg
    datapath = msg.datapath
    parser = datapath.ofproto_parser
    ofproto = datapath.ofproto

    in_port = msg.match["in_port"]
    pkt = packet.Packet(msg.data)
    eth = pkt.get_protocol(ethernet.ethernet)

    if eth is None:
        return

    dst = eth.dst
    src = eth.src
    dpid = datapath.id

    self.mac_to_port.setdefault(dpid, {})
    self.mac_to_port[dpid][src] = in_port

    if dst in self.mac_to_port[dpid]:
        out_port = self.mac_to_port[dpid][dst]
    else:
        out_port = ofproto.OFPP_FLOOD

    actions = [parser.OFPActionOutput(out_port)]

    if out_port != ofproto.OFPP_FLOOD:
        match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
        self._add_flow(datapath, 1, match, actions)

    out = parser.OFPPacketOut(
        datapath=datapath,
        buffer_id=msg.buffer_id,
        in_port=in_port,
        actions=actions,
        data=msg.data
    )
    datapath.send_msg(out)

def _add_flow(self, datapath, priority, match, actions):
    parser = datapath.ofproto_parser
    ofproto = datapath.ofproto

    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
    mod = parser.OFPFlowMod(
        datapath=datapath,
        priority=priority,
        match=match,
        instructions=inst,
        idle_timeout=0,
        hard_timeout=0
    )
    datapath.send_msg(mod)

def _monitor_loop(self):
    while True:
        hub.sleep(MONITOR_INTERVAL)
        for dp in list(self.datapaths.values()):
            self._request_flow_stats(dp)
            self._request_port_stats(dp)

        self._write_report()

def _request_flow_stats(self, datapath):
    parser = datapath.ofproto_parser
    req = parser.OFPFlowStatsRequest(datapath)
    datapath.send_msg(req)

def _request_port_stats(self, datapath):
    parser = datapath.ofproto_parser
    ofproto = datapath.ofproto
    req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
    datapath.send_msg(req)

@set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
def flow_stats_reply_handler(self, ev):
    dpid = ev.msg.datapath.id
    body = ev.msg.body
    self.flow_stats[dpid] = [
        {
            "priority": stat.priority,
            "packet_count": stat.packet_count,
            "byte_count": stat.byte_count,
            "duration_sec": stat.duration_sec,
            "match": str(stat.match)
        }
        for stat in body
    ]

@set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
def port_stats_reply_handler(self, ev):
    dpid = ev.msg.datapath.id
    body = ev.msg.body
    self.port_stats[dpid] = [
        {
            "port_no": stat.port_no,
            "rx_packets": stat.rx_packets,
            "tx_packets": stat.tx_packets,
            "rx_bytes": stat.rx_bytes,
            "tx_bytes": stat.tx_bytes
        }
        for stat in body
    ]

def _write_report(self):
    report = {
        "generated_at": datetime.datetime.now().isoformat(),
        "switches": []
    }

    for dpid in self.datapaths:
        flows = self.flow_stats.get(dpid, [])
        ports = self.port_stats.get(dpid, [])

        report["switches"].append({
            "dpid": "%016x" % dpid,
            "flow_count": len(flows),
            "total_packets": sum(f["packet_count"] for f in flows),
            "total_bytes": sum(f["byte_count"] for f in flows),
            "flows": flows,
            "ports": ports
        })

    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
```
