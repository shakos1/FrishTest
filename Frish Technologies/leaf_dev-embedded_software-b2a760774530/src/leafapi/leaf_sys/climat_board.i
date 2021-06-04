%module climat_board

%include "stdint.i"

%include utils.h

%include slave_task/sensor_ctrl.h
%include slave_task/relay_ctrl.h
%include slave_task/pwm_ctrl.h

%include configs/climat_board_config.h

%{
#define SWIG
#include "mb_regs/mb_regs_configs.h"

#include "slave_task/sensor_ctrl.h"
#include "slave_task/relay_ctrl.h"
#include "slave_task/pwm_ctrl.h"

#include "configs/climat_board_config.h"
%}

%pythoncode %{
__locals = locals()
def get_locals():
    return __locals
%}

