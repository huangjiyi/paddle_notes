import os
import re


def extract_ops_from_yaml(file_path, backward=False):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    ops = []
    ops_info = {}
    if backward:
        op_pattern = re.compile(r'- backward_op\s*:\s*(\S+)')
    else:
        op_pattern = re.compile(r'- op\s*:\s*(\S+)')

    current_info = []
    for line in lines:
        match = op_pattern.match(line)
        if match:
            if current_info and ops:
                ops_info[ops[-1]] = current_info
            current_info = []
            ops.append(match.group(1))
        if line.strip() and not line.startswith('#'):
            current_info.append(line)
    # last op
    if current_info:
        ops_info[ops[-1]] = current_info

    assert len(ops) == len(
        ops_info
    ), f'Ops number mismatch: {len(ops)} vs {len(ops_info)}'
    return ops, ops_info


def save_ops_to_file(ops, output_file):
    with open(output_file, 'w') as f:
        for op in ops:
            f.write(f'- {op}\n')


def save_ops_info_to_file(ops, ops_info, output_file):
    with open(output_file, 'w') as f:
        for op in ops:
            for line in ops_info[op]:
                f.write(f'{line}')
            f.write('\n')


def split_shared_and_unique(dygraph_ops, static_ops):
    shared_ops = []
    dygraph_unique_ops = []
    static_unique_ops = []
    for op in dygraph_ops:
        if op in static_ops:
            shared_ops.append(op)
        else:
            dygraph_unique_ops.append(op)
    for op in static_ops:
        if op not in dygraph_ops:
            static_unique_ops.append(op)
    return shared_ops, dygraph_unique_ops, static_unique_ops


def verify_shared_ops_consistency(
    shared_ops, dygraph_ops_info, static_ops_info
):
    consistent_ops = []
    inconsistent_ops = []
    for op in shared_ops:
        dy_info = dygraph_ops_info[op]
        st_info = static_ops_info[op]
        if dy_info == st_info:
            consistent_ops.append(op)
        else:
            inconsistent_ops.append(op)
    return consistent_ops, inconsistent_ops


def verify_consistency(
    dygraph_yaml_file, static_yaml_file, save_dir, backward=False
):
    # os.makedirs(save_dir, exist_ok=True)
    print(
        "Verify consistency for "
        + ("forward" if not backward else "backward")
        + " ops yaml:"
    )

    dygraph_ops, dygraph_ops_info = extract_ops_from_yaml(
        dygraph_yaml_file, backward
    )
    static_ops, static_ops_info = extract_ops_from_yaml(
        static_yaml_file, backward
    )
    print(f"ops num in dygraph_ops: {len(dygraph_ops)}")
    print(f"ops num in static_ops: {len(static_ops)}")

    shared_ops, dygraph_unique_ops, static_unique_ops = split_shared_and_unique(
        dygraph_ops, static_ops
    )
    # save_ops_to_file(shared_ops, save_dir + 'shared_ops.yaml')
    # save_ops_to_file(dygraph_unique_ops, save_dir + 'dygraph_unique_ops.yaml')
    # save_ops_to_file(static_unique_ops, save_dir + 'static_unique_ops.yaml')
    print(f"shared ops num: {len(shared_ops)}")
    print(f"dygraph unique ops num: {len(dygraph_unique_ops)}")
    print(f"static unique ops num: {len(static_unique_ops)}")

    consistent_ops, inconsistent_ops = verify_shared_ops_consistency(
        shared_ops, dygraph_ops_info, static_ops_info
    )
    # save_ops_to_file(consistent_ops, save_dir + 'consistent_ops.yaml')
    # save_ops_to_file(inconsistent_ops, save_dir + 'inconsistent_ops.yaml')
    print(f"consistent ops num: {len(consistent_ops)}")
    print(f"inconsistent ops num: {len(inconsistent_ops)}\n")

    # save_ops_info_to_file(
    #     inconsistent_ops,
    #     dygraph_ops_info,
    #     save_dir + 'inconsistent_dygraph_ops.yaml',
    # )
    # save_ops_info_to_file(
    #     inconsistent_ops,
    #     static_ops_info,
    #     save_dir + 'inconsistent_static_ops.yaml',
    # )

    return consistent_ops, inconsistent_ops, dygraph_ops_info, static_ops_info


def verify_both_consistency(
    consistent_ops, bw_consistent_ops, bw_inconsistent_ops
):
    both_consistent_ops = []
    both_consistent_ops_bw = []
    for op in consistent_ops:
        both_consistent = True
        ops_bw = []
        for grad_suffix in ['_grad', '_double_grad', '_triple_grad']:
            bw_op = op.rstrip('_') + grad_suffix
            if bw_op in bw_consistent_ops:
                ops_bw.append(bw_op)
            if bw_op in bw_inconsistent_ops:
                both_consistent = False
                break
        if both_consistent:
            both_consistent_ops.append(op)
            both_consistent_ops_bw.extend(ops_bw)

    return both_consistent_ops, both_consistent_ops_bw


def remove_ops_and_save(remove_ops: list, ops_info: dict, output_file):
    ops_info = ops_info.copy()
    for op in remove_ops:
        assert op in ops_info, f'Op {op} not found in ops_info'
        del ops_info[op]
    ops = list(ops_info.keys())
    save_ops_info_to_file(ops, ops_info, output_file)


def add_ops_and_save(add_ops: list, source_ops_info: dict, target_ops_info: dict, output_file):
    target_ops_info = target_ops_info.copy()
    for op in add_ops:
        assert op in source_ops_info, f'Op {op} not found in source_ops_info'
        assert op not in target_ops_info, f'Op {op} already exists in target_ops_info'
        target_ops_info[op] = source_ops_info[op]
    ops = sorted(list(target_ops_info.keys()))
    save_ops_info_to_file(ops, target_ops_info, output_file)


if __name__ == "__main__":
    ops_yaml_dir = '/Paddle/paddle/phi/ops/yaml'

    dygraph_yaml_file = f'{ops_yaml_dir}/inconsistent/dygraph_ops.yaml'
    static_yaml_file = f'{ops_yaml_dir}/inconsistent/static_ops.yaml'
    bw_dygraph_yaml_file = f'{ops_yaml_dir}/inconsistent/dygraph_backward.yaml'
    bw_static_yaml_file = f'{ops_yaml_dir}/inconsistent/static_backward.yaml'

    forward_verify_path = f'{ops_yaml_dir}/inconsistent/verify_forward/'
    backward_verify_path = f'{ops_yaml_dir}/inconsistent/verify_backward/'

    consistent_ops, inconsistent_ops, dygraph_ops_info, static_ops_info = verify_consistency(
        dygraph_yaml_file, static_yaml_file, forward_verify_path, backward=False
    )
    bw_consistent_ops, bw_inconsistent_ops, bw_dygraph_ops_info, bw_static_ops_info = verify_consistency(
        bw_dygraph_yaml_file,
        bw_static_yaml_file,
        backward_verify_path,
        backward=True,
    )
    both_consistent_ops, both_consistent_ops_bw = verify_both_consistency(
        consistent_ops, bw_consistent_ops, bw_inconsistent_ops
    )
    print(f"both consistent ops num: {len(both_consistent_ops)}")
    print(f"both consistent ops backward num: {len(both_consistent_ops_bw)}")

    save_ops_to_file(both_consistent_ops, f'{ops_yaml_dir}/legacy/ops_exclude.yaml')
    save_ops_to_file(both_consistent_ops_bw, f'{ops_yaml_dir}/legacy/backward_exclude.yaml')
    
    remove_ops_and_save(both_consistent_ops, dygraph_ops_info, dygraph_yaml_file)
    remove_ops_and_save(both_consistent_ops, static_ops_info, static_yaml_file)
    remove_ops_and_save(both_consistent_ops_bw, bw_dygraph_ops_info, bw_dygraph_yaml_file)
    remove_ops_and_save(both_consistent_ops_bw, bw_static_ops_info, bw_static_yaml_file)
    
    ops_yaml_file = f'{ops_yaml_dir}/ops.yaml'
    backward_yaml_file = f'{ops_yaml_dir}/backward.yaml'
    
    ops, ops_info = extract_ops_from_yaml(ops_yaml_file)
    bw_ops, bw_ops_info = extract_ops_from_yaml(backward_yaml_file, backward=True)
    
    add_ops_and_save(both_consistent_ops, dygraph_ops_info, ops_info, ops_yaml_file)
    add_ops_and_save(both_consistent_ops_bw, bw_dygraph_ops_info, bw_ops_info, backward_yaml_file)