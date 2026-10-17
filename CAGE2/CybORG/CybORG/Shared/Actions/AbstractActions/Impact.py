from random import choice

from CybORG.Shared import Observation
from CybORG.Shared.Actions import Action
from CybORG.Shared.Actions.ConcreteActions.StopService import StopService
from CybORG.Simulator.State import State
from CybORG.Shared.Enums import Path, FileType
from CybORG.Simulator.File import File




class Impact(Action):
    def __init__(self, session: int, agent: str, hostname: str):
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname

    def sim_execute(self, state: State) -> Observation:
        # find all Red sessions on the chosen host
        sessions = [s for s in state.sessions[self.agent].values() if s.host == self.hostname]
        if not sessions:
            return Observation(success=False)

        # if user didn’t pass a session, pick a SYSTEM/root or random one
        if self.session is None:
            for s in sessions:
                if s.username in ('root', 'SYSTEM'):
                    self.session = s.ident
                    break
            else:
                self.session = choice(sessions).ident

        # pick the OT service name (use discovered one or default)
        sess = state.sessions[self.agent][self.session]
        ot_service = getattr(sess, 'ot_service', None) or 'OTService'

        # attempt to stop that service
        sub_action = StopService(
            agent=self.agent,
            session=self.session,
            service=ot_service,
            target_session=self.session
        )
        obs = sub_action.sim_execute(state)

        if obs.success:
            host = state.hosts[self.hostname]
            f = File(name='ransom.txt', path='/root/', density=1.0, signed=False, user='root')
            f.known_path = Path.SYSTEM
            f.known_file_type = FileType.UNKNOWN
            host.files.append(f)

            
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
