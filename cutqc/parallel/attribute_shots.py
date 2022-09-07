import argparse
import os
import pickle


def run_attribute_shots(rank: int, subcircuit_idx: int, data_folder: str) -> None:
    meta_info = pickle.load(open("%s/meta_info.pckl" % (data_folder), "rb"))
    rank_jobs = pickle.load(open("%s/rank_%d.pckl" % (data_folder, rank), "rb"))

    subcircuit = meta_info["subcircuits"][subcircuit_idx]
    eval_mode = meta_info["eval_mode"]
    instance_init_meas_ids = meta_info["instance_init_meas_ids"]
    entry_init_meas_ids = meta_info["entry_init_meas_ids"][subcircuit_idx]

    uniform_p = 1 / 2**subcircuit.num_qubits

    for subcircuit_entry_init_meas in rank_jobs:
        if eval_mode != "runtime":
            subcircuit_entry_term = rank_jobs[subcircuit_entry_init_meas]
            subcircuit_entry_prob = None
            for term in subcircuit_entry_term:
                coefficient, subcircuit_instance_init_meas = term
                subcircuit_instance_init_meas_id = instance_init_meas_ids[
                    subcircuit_idx
                ][subcircuit_instance_init_meas]
                subcircuit_instance_prob = pickle.load(
                    open(
                        "%s/subcircuit_%d_instance_%d.pckl"
                        % (
                            data_folder,
                            subcircuit_idx,
                            subcircuit_instance_init_meas_id,
                        ),
                        "rb",
                    )
                )
                if subcircuit_entry_prob is None:
                    subcircuit_entry_prob = coefficient * subcircuit_instance_prob
                else:
                    subcircuit_entry_prob += coefficient * subcircuit_instance_prob
        else:
            subcircuit_entry_prob = uniform_p
        entry_init_meas_id = entry_init_meas_ids[subcircuit_entry_init_meas]
        # print('%s --> rank %d writing subcircuit_%d_entry_%d'%(args.data_folder,args.rank,subcircuit_idx,entry_init_meas_id))
        pickle.dump(
            subcircuit_entry_prob,
            open(
                "%s/subcircuit_%d_entry_%d.pckl"
                % (data_folder, subcircuit_idx, entry_init_meas_id),
                "wb",
            ),
        )
    os.remove(f"{data_folder}/rank_{rank}.pckl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--data_folder", metavar="S", type=str)
    parser.add_argument("--subcircuit_idx", metavar="N", type=int)
    parser.add_argument("--rank", metavar="N", type=int)
    args = parser.parse_args()

    run_attribute_shots(args.rank, args.subcircuit_idx, args.data_folder)
