

class conda_envs():
    '''
    Class for conda environment
    '''
    def __init__(self, path, env):
        '''
        path: path to installed miniconda
        env : name of conda environment

        Note, all environments (except base) must be installed in envs subdirectory
        '''
        self.conda_location = path
        if env == "base":
            self.env_location = self.conda_location
        else:
            self.env_location = "{0}/envs/{1}".format(path, env)
        self.conda = "{0}/bin/conda".format(self.conda_location)
        self.activate_cmd = "source {0}/bin/activate {1}".format(path, self.env_location)
        self.deactivate_cmd = "source {0}/bin/deactivate".format(path)