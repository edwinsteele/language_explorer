import os


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise RuntimeError(error_msg)

# Defaults (note that they come before the import based
#  on deployment type
DEBUG = False
SECRET_KEY = None
DEBUG_TB_PANELS = []
TOOLBAR = None
WSGI_APP = None

deployment_type = get_env_variable("LANGUAGE_EXPLORER_DEPLOYMENT")
if deployment_type == "dev":
    from dev_settings import *  # flake8: noqa
elif deployment_type == "staging":
    from staging_settings import *  # flake8: noqa
elif deployment_type == "prod":
    from prod_settings import *  # flake8: noqa
else:
    raise RuntimeError("Invalid LANGUAGE_EXPLORER_DEPLOYMENT type"
                       " '%s'. Valid types are dev/staging/prod" %
                       (deployment_type,))
