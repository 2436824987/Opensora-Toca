import torch
def fresh_ratio_scheduler(cache_dic, current):
    '''
    Return the fresh ratio for the current step.
    '''
    fresh_ratio = cache_dic['fresh_ratio']
    fresh_ratio_schedule = cache_dic['fresh_ratio_schedule']
    step = current['step']
    num_steps = current['num_steps']
    threshold = cache_dic['fresh_threshold']
    weight = 0.9
    if fresh_ratio_schedule == 'constant':
        return fresh_ratio
    elif fresh_ratio_schedule == 'linear':
        return fresh_ratio * (1 + weight - 2 * weight * step / num_steps)
    elif fresh_ratio_schedule == 'exp':
        #return 0.5 * (0.052 ** (step/num_steps))
        return fresh_ratio * (weight ** (step / num_steps))
    elif fresh_ratio_schedule == 'linear-mode':
        mode = (step % threshold)/threshold - 0.5
        mode_weight = 0.1
        return fresh_ratio * (1 + weight - 2 * weight * step / num_steps + mode_weight * mode)
    elif fresh_ratio_schedule == 'layerwise':
        return fresh_ratio * (1 + weight - 2 * weight * current['layer'] / 27)
    
    elif fresh_ratio_schedule == 'ToCa':
        '''
        Video cost too much to tune the parameters
        However, simply set these parameters have good enough performances and fast speed mentioned in our paper.
        We will search a better parameter setting for better in future.
        '''
        step_weight = 0.0
        step_factor = 1 + step_weight - 2 * step_weight * step / num_steps

        layer_weight = 0.0
        layer_factor = 1 + layer_weight - 2 * layer_weight * current['layer'] / 27

        module_weight = 1.5
        #0.85
        module_time_weight = 0.33
        #0.8
        # module_time_weight = 0.66
        module_factor = (1 - (1-module_time_weight) * module_weight) if current['module']=='cross-attn' else (1 + module_time_weight * module_weight)
        
        # set for temporal and spatial branch
        type_weight = 0.0
        type_factor = 1 + type_weight if current['flag'] == -1 else 1 - type_weight

        return fresh_ratio * layer_factor * step_factor * module_factor * type_factor

    else:
        raise ValueError("unrecognized fresh ratio schedule", fresh_ratio_schedule)
