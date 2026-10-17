from ipaddress import IPv4Address

from CybORG.Shared import Observation
from CybORG.Shared.Actions import Action
from CybORG.Shared.Actions.ConcreteActions.Portscan import Portscan


class DiscoverNetworkServices(Action):
    """
    High Level Action that allows an agent to identify services on a host as a prerequisite for running an exploit.

    Calls the low level action Portscan then modifies the observation. Must be used on a host to
    successfully run the high level action ExploitRemoteService.
    """
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        super().__init__()
        self.ip_address = ip_address
        self.agent = agent
        self.session = session

    def sim_execute(self, state) -> Observation:
        # run a Portscan from our session against the target IP
        sub_action = Portscan(
            session=self.session,
            agent=self.agent,
            ip_address=self.ip_address,
            target_session=self.session
        )
        obs = sub_action.sim_execute(state)

        key = str(self.ip_address)
        if key in obs.data:
            sess = state.sessions[self.agent][self.session]

            # defensive: ensure .ports exists on this session
            if not hasattr(sess, 'ports'):
                sess.ports = {}

            sess.clearports(self.ip_address)

            for proc in obs.data[key].get("Processes", []):
                for conn in proc.get('Connections', []):
                    port = conn.get("local_port")
                    if port is not None:
                        # defensive: ensure addport method exists
                        if not hasattr(sess, 'addport'):
                            sess.ports[self.ip_address] = []
                        sess.addport(self.ip_address, port)

        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.ip_address}"
