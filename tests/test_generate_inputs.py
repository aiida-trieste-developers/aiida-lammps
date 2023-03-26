"""Functions to tests the input file generation"""
import os

import pytest
import yaml

from aiida_lammps.common import input_generator
from aiida_lammps.data.lammps_potential import LammpsPotentialData
from aiida_lammps.fixtures.inputs import parameters_md  # noqa: F401
from aiida_lammps.fixtures.inputs import parameters_minimize  # noqa: F401
from aiida_lammps.fixtures.inputs import restart_data  # noqa: F401
from .utils import TEST_DIR


@pytest.mark.parametrize(
    "potential_type",
    ["eam_alloy"],
)
def test_input_generate_minimize(
    db_test_app,  # pylint: disable=unused-argument
    parameters_minimize,  # pylint: disable=redefined-outer-name  # noqa: F811
    get_lammps_potential_data,
    potential_type,
):
    """Test the generation of the input file for minimize calculations"""
    # pylint: disable=too-many-locals

    input_generator.validate_input_parameters(parameters_minimize)
    # Generate the potential
    potential_information = get_lammps_potential_data(potential_type)
    potential = LammpsPotentialData.get_or_create(
        source=potential_information["filename"],
        filename=potential_information["filename"],
        **potential_information["parameters"],
    )
    # Generating the structure
    structure = potential_information["structure"]
    # Generating the input file
    input_file = input_generator.generate_input_file(
        parameters=parameters_minimize,
        potential=potential,
        structure=structure,
        trajectory_filename="temp.dump",
        restart_filename="restart.aiida",
        potential_filename="potential.dat",
        structure_filename="structure.dat",
    )
    reference_file = os.path.join(
        TEST_DIR,
        "test_generate_inputs",
        f"test_generate_input_{potential_type}_minimize.txt",
    )

    with open(reference_file) as handler:
        reference_value = handler.read()

    assert input_file == reference_value, "the content of the files differ"


@pytest.mark.parametrize(
    "potential_type",
    ["eam_alloy"],
)
def test_input_generate_md(
    db_test_app,  # pylint: disable=unused-argument
    parameters_md,  # pylint: disable=redefined-outer-name  # noqa: F811
    get_lammps_potential_data,
    potential_type,
):
    """Test the generation of the input file for MD calculations"""
    # pylint: disable=too-many-locals

    input_generator.validate_input_parameters(parameters_md)
    # Generate the potential
    potential_information = get_lammps_potential_data(potential_type)
    potential = LammpsPotentialData.get_or_create(
        source=potential_information["filename"],
        filename=potential_information["filename"],
        **potential_information["parameters"],
    )
    # Generating the structure
    structure = potential_information["structure"]
    # Generating the input file
    input_file = input_generator.generate_input_file(
        parameters=parameters_md,
        potential=potential,
        structure=structure,
        trajectory_filename="temp.dump",
        restart_filename="restart.aiida",
        potential_filename="potential.dat",
        structure_filename="structure.dat",
    )

    reference_file = os.path.join(
        TEST_DIR,
        "test_generate_inputs",
        f"test_generate_input_{potential_type}_md.txt",
    )
    with open(reference_file) as handler:
        reference_value = handler.read()

    assert input_file == reference_value, "the content of the files differ"


@pytest.mark.parametrize(
    "print_final,print_intermediate,num_steps",
    [
        (True, False, None),
        (True, True, 100),
        (True, True, None),
        (False, True, None),
        (False, True, 100),
    ],
)
def test_input_generate_restart(
    db_test_app,  # pylint: disable=unused-argument
    restart_data,  # pylint: disable=redefined-outer-name  # noqa: F811
    print_final,
    print_intermediate,
    num_steps,
):
    """Test the generation of the input file for MD calculations"""
    # pylint: disable=too-many-locals

    parameters_file = os.path.join(
        TEST_DIR,
        "test_generate_inputs",
        "parameters_md.yaml",
    )
    # Dictionary with parameters for controlling aiida-lammps
    with open(parameters_file) as handler:
        parameters = yaml.load(handler, yaml.SafeLoader)

    parameters["restart"]["print_final"] = print_final
    parameters["restart"]["print_intermediate"] = print_intermediate
    if num_steps:
        parameters["restart"]["num_steps"] = num_steps

    input_generator.validate_input_parameters(parameters)

    # Generating the input file
    input_file = input_generator.write_restart_block(
        parameters_restart=parameters["restart"],
        restart_filename="restart.aiida",
        max_number_steps=1000,
    )

    if print_final:
        assert "final" in input_file, "no final restart information generated"
        _msg = "reference value for the final restart does not match"
        assert input_file["final"] == restart_data["final"], _msg
    else:
        assert input_file["final"] == ""

    if print_intermediate:
        assert (
            "intermediate" in input_file
        ), "no intermediate restart information generated"
        _msg = "reference value for the intermediate restart does not match"
        assert input_file["intermediate"] == restart_data["intermediate"], _msg
    else:
        assert input_file["intermediate"] == ""
