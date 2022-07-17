"""
Simple flask app to handle incoming simulationrequests
"""
import os
import datetime as dt
from flask_cors import CORS
from flask import Flask, jsonify, make_response, request
from py_src.back_end.epidemic_models.utils.common_helpers import logger
from py_src.back_end.epidemic_models.executor import execute_cpp_SIR, get_simulation_config, generic_SIR
from py_src.params_and_config import (mkdir_tmp_store, GenericSimulationConfig, SaveOptions, RuntimeSettings)


app = Flask(__name__)
CORS(app)
port = int(os.environ.get('PORT', 5000))
app.run(debug=True, host='0.0.0.0', port=port)


def simulate(sim_config: GenericSimulationConfig, save_options: SaveOptions, rt_settings: RuntimeSettings):
    """
        Simulate the spread of disease
    """
    mkdir_tmp_store()
    # TODO execute compiled c++ version of the algorithm
    # execute_cpp_SIR(sim_config, save_options, rt_settings)
    generic_SIR(sim_config, save_options, rt_settings)


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
    rt_settings.frame_freq = 10
    save_options = SaveOptions()
    save_options.frame_save = True
    elapsed = dt.datetime.now() - start
    logger(f'[i] Configured & validated params in {elapsed } (s)...')
    try:
        simulate(sim_config, save_options, rt_settings)
        logger('[i] Finished succesful simulation')
        return make_response(jsonify(message=f'The backend is alive! This is what you gave me mofo {sim_config} '), 200)
    except Exception as e:
        logger(f'[e] Simulation failed: {e}')
        return make_response(jsonify(error=f'{e}'), 500)


@app.route("/test", methods=['GET'])
def test_route():
    return make_response(jsonify(message=f'Successful yo'), 200)


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found - homie!'), 404)
