# Copyright DST Group. Licensed under the MIT license.
import copy
import inspect
from ipaddress import IPv4Network
from math import log2
from random import sample, choice
import yaml

from CybORG import CybORG
from CybORG.Shared.Actions import FindFlag, ShellSleep, SambaUsermapScript, UpgradeToMeterpreter, MSFEternalBlue, GetShell, \
    PingSweep
from CybORG.Shared.Actions.Action import Action
from CybORG.Shared.Enums import FileType, TrinaryEnum, OperatingSystemType, SessionType
from CybORG.Shared.EnvironmentController import EnvironmentController
from CybORG.Shared.Observation import Observation
from CybORG.Shared.Results import Results
from CybORG.Simulator.State import State
from CybORG.Shared.Actions.ConcreteActions.ExploitAction import ExploitAction
from CybORG.Shared.Actions.ConcreteActions.ExploitAction import ExploitAction
from CybORG.Shared.Actions.ConcreteActions.ExploitAction import ExploitAction
from CybORG.Shared.Actions.MSFActionsFolder.MSFAction import MSFAction
from CybORG.Shared.Actions.AbstractActions.PrivilegeEscalate import PrivilegeEscalate
from CybORG.Simulator.Session import RedAbstractSession
from CybORG.Shared.Actions import ExploitRemoteService

class SimulationController(EnvironmentController):
    """The class that controls the Simulation environment.

    Inherits from Environment Controller then implements simulation-specific functionality.
    Most methods are either disabled or delegate their functionality to the State attribute.
    The main thing this class currently does is parse the scenario file.
    """
    def __init__(self, scenario_filepath: str = None, scenario_mod: dict = None, agents: dict = None, verbose=True):
        self.state = None
        super().__init__(scenario_filepath, scenario_mod=scenario_mod, agents=agents)

    def reset(self, agent=None):
        self.state.reset()
        self.hostname_ip_map = {h: ip for ip, h in self.state.ip_addresses.items()}
        self.subnet_cidr_map = self.state.subnet_name_to_cidr
        return super(SimulationController, self).reset(agent)

    def pause(self):
        pass

    def execute_action(self, action: Action) -> Observation:

        for sess in self.state.sessions.get('Red', {}).values():
            if not hasattr(sess, 'ot_service'):
                sess.ot_service = None
                
        # 1) perform the action
        obs = action.sim_execute(self.state)
    
        # 2) if it was a successful Red exploit, upgrade the session and seed OS info
        if isinstance(action, ExploitRemoteService) and obs.data.get('success') is True:
            red_sessions = self.state.sessions.get('Red', {})
            if red_sessions:
                # Grab the newest session
                new_id = max(red_sessions.keys())
                sess = red_sessions[new_id]

                # Force it to be an AbstractSession and init all fields
                sess.session_type = SessionType.RED_ABSTRACT_SESSION
                sess.__class__ = RedAbstractSession
                # ensure all attributes exist
                if not hasattr(sess, 'ports'):
                    sess.ports = {}
                if not hasattr(sess, 'operating_system'):
                    sess.operating_system = {}
                # this was missing before
                sess.ot_service = getattr(sess, 'ot_service', None)

                # Populate the OS mapping so PrivilegeEscalate can find it
                ip_str = str(action.ip_address)
                host_obs = obs.data.get(ip_str, {})
                sysinfo = host_obs.get('System info', {})
                hostname = sysinfo.get('Hostname')
                os_type = sysinfo.get('OSType', OperatingSystemType.LINUX)
                if hostname:
                    sess.operating_system[hostname] = os_type
    
        return obs


    def restore(self, file: str):
        pass

    def save(self, file: str):
        pass

    def get_true_state(self, info: dict) -> Observation:
        output = self.state.get_true_state(info)
        return output

    def shutdown(self, **kwargs):
        pass

    def _parse_scenario(self, scenario_filepath: str, scenario_mod: dict = None):
        scenario_dict = super()._parse_scenario(scenario_filepath, scenario_mod=scenario_mod)
        images_file_path = str(inspect.getfile(CybORG))
        images_file_path = images_file_path[:-10] + '/Shared/Scenarios/images/'
        with open(images_file_path + 'images.yaml') as fIn:
            images_dict = yaml.load(fIn, Loader=yaml.FullLoader)
        if scenario_dict is not None:
            for hostname, image in scenario_dict["Hosts"].items():
                if 'path' in images_dict[image["image"]]:
                    with open(images_file_path + images_dict[image["image"]]['path'] + '.yaml') as fIn2:
                        scenario_dict["Hosts"][hostname].update(
                            yaml.load(fIn2, Loader=yaml.FullLoader).pop('Test_Host'))
                    image.pop('image')
                else:
                    scenario_dict["Hosts"][hostname] = copy.deepcopy(images_dict[image["image"]])
        return scenario_dict

    def _create_environment(self):
        self.state = State(self.scenario)
        self.hostname_ip_map = {h: ip for ip, h in self.state.ip_addresses.items()}
        self.subnet_cidr_map = self.state.subnet_name_to_cidr

    def run_schtasks(self):
        for host in self.hosts:
            host.run_scheduled_tasks(self.step)

    def get_last_observation(self, agent):
        return self.observation[agent]
