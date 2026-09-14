from os.path import join
from pathlib import Path
from collections.abc import Mapping

from bsb import get_configuration_parser, parse_configuration_file

from cerebellar_models.cli import (
    CONFIGURATION_FOLDER,
    MicrozonesParams,
    _absolutize_morphology_paths,
    _clear_unnecessary_params,
    _configure_sim_params,
    _filter_simulations_devices,
    _update_cell_types,
)
from cerebellar_models.utils import deep_update, get_folders_in_folder, load_configs_in_folder


def plainify(value):
    if isinstance(value, Mapping):
        return {key: plainify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plainify(item) for item in value]
    return value


def main():
    species = "mouse"
    state = "awake"
    extra_cell_types = ["dcn", "io"]
    simulation_names = ["nest_basal_activity"]

    species_folder = join(CONFIGURATION_FOLDER, species)
    configuration = parse_configuration_file(
        join(species_folder, f"{species}_cerebellar_cortex.yaml")
    ).__tree__()

    config_cell_types = load_configs_in_folder(join(species_folder, "cell_types"))
    configuration = _update_cell_types(configuration, extra_cell_types, config_cell_types)

    state_folder = join(species_folder, state)
    config_simulations = {
        simulator: {
            "cell_models": load_configs_in_folder(join(state_folder, simulator, "cell_models")),
            "simulations": _filter_simulations_devices(
                load_configs_in_folder(join(state_folder, simulator), recursive=False),
                list(configuration["cell_types"].keys()),
            ),
        }
        for simulator in get_folders_in_folder(state_folder)
    }

    dict_sim, _ = _configure_sim_params(
        config_simulations,
        simulation_names,
        MicrozonesParams(),
        list(configuration["cell_types"].keys()),
        non_interactive=True,
    )
    deep_update(configuration, dict_sim)
    configuration = _clear_unnecessary_params(configuration)
    configuration = _absolutize_morphology_paths(configuration)
    configuration = plainify(configuration)

    out_dir = Path(__file__).resolve().parent
    full_path = out_dir / "circuit.yaml"
    full_path.write_text(
        get_configuration_parser("yaml").generate(configuration, pretty=True),
        encoding="utf-8",
    )

    reconstruction_only = dict(configuration)
    reconstruction_only.pop("components", None)
    reconstruction_only.pop("simulations", None)
    reconstruction_only.pop("packages", None)
    recon_path = out_dir / "circuit_reconstruction_only.yaml"
    recon_path.write_text(
        get_configuration_parser("yaml").generate(reconstruction_only, pretty=True),
        encoding="utf-8",
    )

    print(f"Wrote {full_path}")
    print(f"Wrote {recon_path}")


if __name__ == "__main__":
    main()
