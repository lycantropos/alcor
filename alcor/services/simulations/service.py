import logging
import uuid
from decimal import Decimal
from subprocess import check_call
from typing import (Any,
                    Dict)

from cassandra.cluster import Session

from alcor.models import Star
from alcor.models.simulation import Parameter
from alcor.services.data_access import (insert,
                                        model_insert_statement)
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
    precision = settings['precision']
    parameters_info = settings['parameters']
    for parameters_values in generate_parameters_values(
            parameters_info=parameters_info,
            precision=precision):
        group_id = uuid.uuid4()
        save_parameters(values=parameters_values,
                        group_id=group_id,
                        session=session)

        output_file_name = generate_output_file_name(group_id=str(group_id))

        run_simulation(parameters_values=parameters_values,
                       model_type=model_type,
                       output_file_name=output_file_name)

        with open(output_file_name) as output_file:
            stars = parse_stars(output_file,
                                group_id=group_id)

        insert_statement = model_insert_statement(Star)
        insert(instances=stars,
               statement=insert_statement,
               session=session)


def save_parameters(*,
                    values: Dict[str, Decimal],
                    group_id: uuid.UUID,
                    session: Session) -> None:
    parameters = [Parameter(group_id=group_id,
                            name=parameter_name,
                            value=parameter_value)
                  for parameter_name, parameter_value in values.items()]

    statement = model_insert_statement(Parameter)
    insert(instances=parameters,
           statement=statement,
           session=session)


def run_simulation(*,
                   parameters_values: Dict[str, NumericType],
                   model_type: int,
                   output_file_name: str) -> None:
    args = ['./main.e',
            '-db', parameters_values['DB_fraction'],
            '-g', parameters_values['galaxy_age'],
            '-mf', parameters_values['initial_mass_function_exponent'],
            '-ifr', parameters_values['lifetime_mass_ratio'],
            '-bt', parameters_values['burst_time'],
            '-mr', parameters_values['mass_reduction_factor'],
            '-km', model_type,
            '-o', output_file_name]
    args = list(map(str, args))
    args_str = ' '.join(args)
    logger.info(f'Invoking simulation with command "{args_str}".')
    check_call(args)


def generate_output_file_name(group_id: str) -> str:
    base_name = group_id[:MAX_OUTPUT_FILE_NAME_LENGTH]
    return ''.join([base_name, OUTPUT_FILE_EXTENSION])