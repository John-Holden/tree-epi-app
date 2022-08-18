"""
Simple flask app to handle incoming simulationrequests
"""
import os
import subprocess
import datetime as dt
from flask_cors import CORS
from flask import Flask, jsonify, make_response, request
from py_src.back_end.epidemic_models.utils.common_helpers import logger, get_env_var
from py_src.back_end.epidemic_models.executor import execute_cpp_SIR, get_simulation_config, generic_SIR, get_updates
from py_src.params_and_config import (mkdir_tmp_store, GenericSimulationConfig, SaveOptions, RuntimeSettings)


app = Flask(__name__)
CORS(app)
port = int(os.environ.get('PORT', 5000))
app.run(debug=True, host='0.0.0.0', port=port)


def simulate(sim_config: GenericSimulationConfig, save_options: SaveOptions, rt_settings: RuntimeSettings, pr_approx: bool=True) -> dict:
    """
        Simulate the spread of disease & return output SIR fields
    """
    mkdir_tmp_store(get_env_var('FRAME_SAVE_DEST'))
    if pr_approx:
        return execute_cpp_SIR(sim_config, save_options, rt_settings)

    return generic_SIR(sim_config, save_options, rt_settings)


def ffmegp_anim() -> str:
    """
        Execute a shell command to produce an mp4, then return the simulation location.
    """
    anim_path = get_env_var('ANIM_SAVE_DEST')
    frame_path = get_env_var('FRAME_SAVE_DEST')
    print(frame_path, '<=---- FRAME PATH')
    dtnow = dt.datetime.now().strftime('%Y%m%d%s')
    animate_cmd = f'{anim_path}/animate.sh {frame_path} {anim_path} {dtnow}'
    process = subprocess.Popen(animate_cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if get_env_var('FLASK_ENV') == 'development':
        logger(output)

    return dtnow


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
    save_options.save_field_time_series = True
    elapsed = dt.datetime.now() - start
    logger(f'[i] Configured & validated params in {elapsed } (s)...')
    try:
        SIR_fields = simulate(sim_config, save_options, rt_settings)
        sim_location = ffmegp_anim()
        logger('[i] Finished succesful simulation')

        return make_response(jsonify(video_ref=sim_location, 
                                     S=SIR_fields['S'], 
                                     I=SIR_fields['I'], 
                                     R=SIR_fields['R'],
                                     t=[i for i in range(len(SIR_fields['S']))]), 200)
    except Exception as e:
        logger(f'[e] Simulation failed: {e}')
        return make_response(jsonify(error=f'{e}'), 500)


@app.route("/stateupdate", methods=['POST'])
def get_R0():
    """
        Calcuate R0 based on input input parameters
    """
    start = dt.datetime.now()
    out = get_updates(request.get_json(force=True))
    if out is None:
        R0_estimated, density, beta_max = '', '', ''
    else:
        R0_estimated, density, beta_max = out

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
