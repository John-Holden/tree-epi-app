import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, List
from py_src.params_and_config import GenericSimulationConfig, PATH_TO_TEMP
from py_src.back_end.epidemic_models.utils.common_helpers import get_env_var, logger
# Matplotlib style fixture
pltParams = {'figure.figsize': (7.5, 5.5),
             'axes.labelsize': 15,
             'ytick.labelsize': 20,
             'xtick.labelsize': 20,
             'legend.fontsize': 'x-large'}

plt.rcParams.update(pltParams)

# -------------------Simulation plotting methods-------------------#
def frame_label(step):
    if step < 10:
        return '000' + str(step)
    if step < 100:
        return '00' + str(step)
    if step < 1000:
        return '0' + str(step)
    if step < 10000:
        return str(step)


def SIR_frame(S: List[np.ndarray], I: List[np.ndarray], R: List[np.ndarray], t: int,
              sim_context: GenericSimulationConfig, save_frame: Optional[bool] = False,
              show_frame: Optional[bool] = True, ext: Optional[str] = 'png',
              Spx: Optional[int] = 30, Ipx: Optional[int] = 10, Rpx: Optional[int] = 10):
    """
    Plot a single time-step


    :param show_frame:
    :param S: susceptible trees
    :param I: infected trees
    :param R: removed trees
    :param t: current time-step
    :param sim_context:
    :param save_frame:
    :param ext: anim extension
    :param Spx: pixel size
    :param Ipx: pixel size
    :param Rpx: pixel size
    :param title: plot title
    :return:
    """
    rho = sim_context.domain_config.tree_density
    alpha = sim_context.domain_config.scale_constant
    _, ax = plt.subplots()

    plt.title(rf"T : {t} | $\rho$ = {rho}, $\alpha$ = {alpha}$m^2$")
    ax.scatter(S[1], S[0], s=Spx, c='green', label=r'$S$', alpha=0.30)
    ax.scatter(I[1], I[0], s=Ipx, c='red', label=r'$I$')
    ax.scatter(I[1], I[0], s=200, c='red', alpha=0.10)
    ax.scatter(R[1], R[0], s=Rpx, c='black', label=r'$R$')
    ax.scatter(R[1], R[0], s=200, c='black', alpha=0.10)

    # locs = plt.xticks()[0]
    # labels = [int(i*alpha) for i in locs if i not in [locs[0], locs[-1]]]
    # locs = [i for i in locs if i not in [locs[0], locs[-1]]]
    
    plt.axis('off')
    plt.tight_layout()

    if save_frame:
        frame_name = f'img_{frame_label(t)}.{ext}' 
        dest = f"{get_env_var('FRAME_SAVE_DEST')}/{frame_name}"

        if get_env_var('FLASK_ENV') == 'development':
            logger(f'[i] Frame plot saving to {dest} @ step {t}')
            
        plt.savefig(dest)

    if show_frame:
        plt.show()

    plt.close()
