import csv
import logging
import uuid
from decimal import Decimal
from subprocess import check_call
from typing import (Any,
                    Iterable,
                    Dict)

from sqlalchemy.orm.session import Session

from alcor.models import Group
from alcor.models.simulation import Parameter
from alcor.services.parameters import generate_parameters_values
from alcor.services.restrictions import (OUTPUT_FILE_EXTENSION,
                                         MAX_OUTPUT_FILE_NAME_LENGTH)
from alcor.types import NumericType
from alcor.utils import parse_stars

logger = logging.getLogger(__name__)


def run_simulations(*,
                    settings: Dict[str, Any],
                    session: Session) -> None:
    model_type = settings['model_type']
    geometry = settings['geometry']
    precision = settings['precision']
    parameters_info = settings['parameters']

    if geometry == 'sphere':
        for parameters_values in generate_parameters_values(
                parameters_info=parameters_info,
                precision=precision):
            group_id = uuid.uuid4()
            group = Group(id=group_id)

            parameters = generate_parameters(values=parameters_values,
                                             group=group)

            output_file_name = generate_output_file_name(group_id=str(group_id))

            run_simulation(parameters_values=parameters_values,
                           model_type=model_type,
                           geometry=geometry,
                           output_file_name=output_file_name)

            with open(output_file_name) as output_file:
                stars = list(parse_stars(output_file,
                                         group=group))

    elif geometry == 'cone':
        with open('../plates_info_arebassa_0.csv', 'r') as angles_file:
            angles_reader = csv.reader(angles_file,
                                       delimiter=' ',
                                       skipinitialspace=True)
            used_plates = []
            prev_plate_number = 0
            for row in angles_reader:
                plate_number = row[1]
                if plate_number == prev_plate_number:
                    continue
                else:
                    prev_plate_number = plate_number
                longitude = row[7]
                latitude = row[8]
                plate_angles = (longitude, latitude)
                if plate_angles in used_plates:
                    continue
                else:
                    used_plates.append(plate_angles)
                logger.info(f'Generating stars for values of the plate Nº '
                            f'{plate_number}')
                # No need to walk through parameters here. We only need to
                # run simulations for all angles in the file with the same
                # standard parameters. How do we do it?
                # TODO: delete this loop, use only run_simulation
                for parameters_values in generate_parameters_values(
                        parameters_info=parameters_info,
                        precision=precision):
                    group_id = uuid.uuid4()
                    group = Group(id=group_id)

                    parameters = generate_parameters(values=parameters_values,
                                                     group=group)

                    output_file_name = generate_output_file_name(
                        group_id=str(group_id))

                    run_simulation(parameters_values=parameters_values,
                                   model_type=model_type,
                                   geometry=geometry,
                                   cone_longitude=longitude,
                                   cone_latitude=latitude,
                                   output_file_name=output_file_name)

                    # TODO: uncomment this after I figure out what to do
                    # with cone output data
                    with open(output_file_name) as output_file:
                        stars = list(parse_stars(output_file,
                                                 group=group))

    session.add(group)
    session.add_all(parameters)
    session.add_all(stars)
    session.commit()


def generate_parameters(*,
                        values: Dict[str, Decimal],
                        group: Group) -> Iterable[Parameter]:
    for parameter_name, parameter_value in values.items():
        yield Parameter(group_id=group.id,
                        name=parameter_name,
                        value=parameter_value)


def run_simulation(*,
                   parameters_values: Dict[str, NumericType],
                   model_type: int,
                   geometry: str,
                   cone_longitude: float = 0.,
                   cone_latitude: float = 0.,
                   output_file_name: str) -> None:
    args = ['./main.e',
            '-db', parameters_values['DB_fraction'],
            '-g', parameters_values['galaxy_age'],
            '-mf', parameters_values['initial_mass_function_exponent'],
            '-ifr', parameters_values['lifetime_mass_ratio'],
            '-bt', parameters_values['burst_time'],
            '-mr', parameters_values['mass_reduction_factor'],
            '-km', model_type,
            '-o', output_file_name,
            '-geom', geometry,
            '-cl', cone_longitude,
            '-cb', cone_latitude]
    args = list(map(str, args))
    args_str = ' '.join(args)
    logger.info(f'Invoking simulation with command "{args_str}".')
    check_call(args)


def generate_output_file_name(group_id: str) -> str:
    base_name = group_id[:MAX_OUTPUT_FILE_NAME_LENGTH]
    return ''.join([base_name, OUTPUT_FILE_EXTENSION])
