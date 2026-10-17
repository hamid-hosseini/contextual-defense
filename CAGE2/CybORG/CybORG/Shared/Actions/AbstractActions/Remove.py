from random import choice
from CybORG.Shared import Observation
from .Monitor import Monitor
from CybORG.Shared.Actions import Action
from CybORG.Shared.Actions.ConcreteActions.StopProcess import StopProcess
from CybORG.Simulator.Session import VelociraptorServer
from CybORG.Simulator.State import State

class Remove(Action):
    def __init__(self, session: int, agent: str, hostname: str):
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname

    def sim_execute(self, state: State) -> Observation:
        parent_session: VelociraptorServer = state.sessions[self.agent][self.session]
        obs = Observation(True)

        # Look through red agents for sessions on the target host
        sessions = []
        for agent_name, sess_dict in state.sessions.items():
            if agent_name.startswith('Red'):
                for s in list(sess_dict.values()):
                    if s.host == self.hostname:
                        sessions.append(s)

        if len(sessions) == 0:
            return Observation(False)

        if self.hostname in parent_session.sus_pids:
            for sus_pid in parent_session.sus_pids[self.hostname]:
                for target_session in sessions:
                    action = StopProcess(session=self.session, agent=self.agent, target_session=target_session.ident, pid=sus_pid)
                    action.sim_execute(state)

                    # ✅ Remove the Red session after stopping the process
                    agent = target_session.agent
                    sid = target_session.ident
                    host = target_session.host

                    # Remove from global session map
                    if sid in state.sessions[agent]:
                        del state.sessions[agent][sid]

                    # Remove from host session map
                    if agent in state.hosts[host].sessions and sid in state.hosts[host].sessions[agent]:
                        state.hosts[host].sessions[agent].remove(sid)

                        # Clean up if session list becomes empty
                        if not state.hosts[host].sessions[agent]:
                            del state.hosts[host].sessions[agent]

        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
