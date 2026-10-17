from CybORG.Shared import Observation
from CybORG.Shared.Actions import Action
from CybORG.Simulator.Session import VelociraptorServer, Session
from CybORG.Simulator.State import State


class Monitor(Action):
    def __init__(self, session: int, agent: str):
        super().__init__()
        self.agent = agent
        self.session = session

    def sim_execute(self, state: State) -> Observation:
        obs = Observation(True)
        session: VelociraptorServer = state.sessions[self.agent][self.session]

        for child in session.children.values():
            host_obj = state.hosts[child.host]
            obs.add_system_info(hostid=child.host, **host_obj.get_state())

            for agent_name, sessions in state.sessions.items():
                if agent_name.startswith('Red'):
                    for sess in sessions.values():
                        if sess.host == child.host and isinstance(sess, Session):
                            obs.add_process(hostid=sess.host, pid=sess.pid, username=sess.username)
                    
                            if sess.host not in session.sus_pids:
                                session.sus_pids[sess.host] = []
                            if sess.pid not in session.sus_pids[sess.host]:
                                session.sus_pids[sess.host].append(sess.pid)



        return obs

    def __str__(self):
        return f"{self.__class__.__name__}"