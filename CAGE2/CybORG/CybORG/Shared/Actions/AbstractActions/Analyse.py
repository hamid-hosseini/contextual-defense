from random import choice

from CybORG.Shared import Observation
from .Monitor import Monitor
from CybORG.Shared.Actions import Action
from CybORG.Shared.Actions.AbstractActions import Monitor
from CybORG.Shared.Actions.ConcreteActions.DensityScout import DensityScout
from CybORG.Shared.Actions.ConcreteActions.SigCheck import SigCheck


class Analyse(Action):
    def __init__(self, session: int, agent: str, hostname: str):
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname

    def sim_execute(self, state) -> Observation:
        sessions = [s for s in state.sessions[self.agent].values() if s.host == self.hostname]
        if len(sessions) > 0:
            session = choice(sessions)
            obs = Observation(True)
            
            # Only check for impact, no session/process detection
            host = state.hosts[self.hostname]
            for f in host.files:
                if 'impact' in f.name.lower() or 'ransom' in f.name.lower():
                    obs.data[self.hostname] = {'ImpactDetected': True}
                    break
    
            return obs
        else:
            return Observation(False)


    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
    
