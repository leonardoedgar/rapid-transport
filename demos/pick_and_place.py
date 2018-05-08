import openravepy as orpy
import toppra_app, time
import numpy as np
from toppra_app.utils import expand_and_join
import yaml, logging
import os
logger = logging.getLogger(__name__)
logging.basicConfig(level='DEBUG')


class PickAndPlaceDemo(object):
    def __init__(self, load_path=None):
        assert load_path is not None
        db = toppra_app.database.Database()
        _scenario_dir = expand_and_join(db.get_data_dir(), load_path)
        with open(_scenario_dir) as f:
            self._scenario = yaml.load(f.read())
        _env_dir = expand_and_join(db.get_model_dir(), self._scenario['env'])
        self._env = orpy.Environment()
        self._env.Load(_env_dir)
        self._robot = self._env.GetRobot(self._scenario['robot'])
        self._objects = []
        # Load all objects to openRave
        for obj_d in self._scenario['objects']:
            obj = toppra_app.SolidObject.init_from_dict(self._robot, obj_d)
            self._objects.append(obj)
            obj.load_to_env(obj_d['T_start'])
            self._robot.SetActiveManipulator(obj_d['object_attach_to'])
        # Generate IKFast if needed
        iktype = orpy.IkParameterization.Type.Transform6D
        ikmodel = orpy.databases.inversekinematics.InverseKinematicsModel(self._robot, iktype=iktype)
        if not ikmodel.load():
            print 'Generating IKFast {0}. It will take few minutes...'.format(iktype.name)
            ikmodel.autogenerate()
            print 'IKFast {0} has been successfully generated'.format(iktype.name)

    def view(self):
        res = self._env.SetViewer('qtosg')
        time.sleep(0.5)
        return res

    def get_env(self):
        return self._env

    def get_robot(self):
        return self._robot

    def get_object(self, name):
        obj = None
        for obj_ in self._objects:
            if obj_.get_name() == name:
                return obj_
        return obj

    def get_object_dict(self, name):
        for entry_ in self._scenario['objects']:
            if entry_['name'] == name:
                return entry_
        return None

    def get_qstart(self):
        return self._robot.GetActiveDOFValues()

    def run(self):
        """ Run the demo.
        """
        q_current = self.get_qstart()
        self.get_robot().SetActiveDOFValues(q_current)
        fail = False
        for obj_d in self._scenario['objects']:
            manip_name = obj_d["object_attach_to"]
            manip = self.get_robot().SetActiveManipulator(manip_name)
            basemanip = orpy.interfaces.BaseManipulation(self.get_robot())
            Tstart = obj_d['T_start']
            logger.debug(Tstart)
            Tgoal = obj_d['T_goal']

            # Check that the starting position can be reached
            T_ee_start = np.dot(Tstart, self.get_object(obj_d['name']).get_T_object_link())
            qstart_col = manip.FindIKSolution(T_ee_start, orpy.IkFilterOptions.CheckEnvCollisions)
            qstart_nocol = manip.FindIKSolution(T_ee_start, orpy.IkFilterOptions.IgnoreEndEffectorCollisions)
            if qstart_col is None:
                fail = True
                logger.warn("Unable to find a collision free solution.")
                if qstart_nocol is None:
                    logger.warn("Reason: unable to reach this pose.")
                else:
                    logger.warn("Reason: collision (able to reach).")
                    self._robot.SetActiveDOFValues(qstart_nocol)
            if fail:
                logger.warn("Breaking from planning loop.")
                break

            traj0 = basemanip.MoveToHandPosition(matrices=[T_ee_start], outputtrajobj=True)
            self.get_robot().WaitForController(0)
            self._robot.Grab(self.get_env().GetKinBody(obj_d['name']))

            T_ee_goal = np.dot(Tgoal, self.get_object(obj_d['name']).get_T_object_link())
            traj1 = basemanip.MoveToHandPosition(matrices=[T_ee_goal], outputtrajobj=True)
            self.get_robot().WaitForController(0)
            self._robot.Release(self.get_env().GetKinBody(obj_d['name']))

            time.sleep(2)

        return not fail


if __name__ == "__main__":
    demo = PickAndPlaceDemo("scenarios/test0.scenario.yaml")
    demo.view()
    demo.run()
    import IPython
    if IPython.get_ipython() is None:
        IPython.embed()
    
