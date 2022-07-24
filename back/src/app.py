"""
Simple flask app to handle incoming simulationrequests
"""
import os
import subprocess
import datetime as dt
from flask_cors import CORS
from flask import Flask, jsonify, make_response, request
from matplotlib.ft2font import LOAD_TARGET_LIGHT
from py_src.back_end.epidemic_models.utils.common_helpers import logger, get_env_var
from py_src.back_end.epidemic_models.executor import execute_cpp_SIR, get_simulation_config, generic_SIR, get_updates
from py_src.params_and_config import (mkdir_tmp_store, GenericSimulationConfig, SaveOptions, RuntimeSettings)


app = Flask(__name__)
CORS(app)
port = int(os.environ.get('PORT', 5000))
app.run(debug=True, host='0.0.0.0', port=port)


def simulate(sim_config: GenericSimulationConfig, save_options: SaveOptions, rt_settings: RuntimeSettings):
    """
        Simulate the spread of disease
    """
    mkdir_tmp_store(get_env_var('FRAME_SAVE_DEST'))
    ## TODO execute compiled c++ version of the algorithm
    # execute_cpp_SIR(sim_config, save_options, rt_settings)
    generic_SIR(sim_config, save_options, rt_settings)


def ffmegp_anim():
    anim_path = get_env_var('ANIM_SAVE_DEST')
    frame_path = get_env_var('FRAME_SAVE_DEST')
    animate_cmd = f'{anim_path}/animate.sh {frame_path} {anim_path}'
    process = subprocess.Popen(animate_cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if get_env_var('FLASK_ENV') == 'development':
        logger(output), 
    
    logger(error)


@app.route("/", methods=['POST'])
def simulation_request_handler():
    """
        Handel input requests and validate input parameters
    """
    start = dt.datetime.now()
    sim_config = get_simulation_config(request.get_json(force=True))
    rt_settings = RuntimeSettings()
    rt_settings.verbosity = 0
    rt_settings.frame_plot = True
    rt_settings.frame_show = False
    rt_settings.frame_freq = 1
    save_options = SaveOptions()
    save_options.frame_save = True
    elapsed = dt.datetime.now() - start
    logger(f'[i] Configured & validated params in {elapsed } (s)...')
    try:
        simulate(sim_config, save_options, rt_settings)
        logger('[i] Finished succesful simulation')
        ffmegp_anim()
        return make_response(jsonify(message=f'The backend is alive! This is what you gave me mofo {sim_config} '), 200)
    except Exception as e:
        logger(f'[e] Simulation failed: {e}')
        return make_response(jsonify(error=f'{e}'), 500)



@app.route("/stateupdate", methods=['POST'])
def get_R0():
    """
        Calcuate R0 based on input input parameters
    """
    start = dt.datetime.now()
    R0_estimated, density, beta_max = get_updates(request.get_json(force=True))
    elapsed = dt.datetime.now() - start
    logger(f'[i] Got R0 IN {elapsed} (s)...')
    try:
        return make_response(jsonify(R0=R0_estimated,
                                     density=density,
                                     beta_max=beta_max), 200)
    except Exception as e:
        logger(f'[e] R0 calculation failed: {e}')
        return make_response(jsonify(error=f'{e}'), 500)


@app.errorhandler(404)
def resource_not_found():
    return make_response(jsonify(error='Not found - homie!'), 404)
