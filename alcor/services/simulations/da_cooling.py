import csv
import os
from typing import (Iterator,
                    Dict,
                    Tuple,
                    List)

import numpy as np

from alcor.types import CoolingSequencesType


def initialize_sequences(rows_count: int = 650
                         ) -> CoolingSequencesType:
    # Metallicities were multiplied by 1000 in order to keep dict.keys as ints
    files_paths_by_metallicities = {1: ['wd0505_z0001.trk',
                                        'wd0553_z0001.trk',
                                        'wd0593_z0001.trk',
                                        'wd0627_z0001.trk',
                                        'wd0660_z0001.trk',
                                        'wd0692_z0001.trk',
                                        'wd0863_z0001.trk'],
                                    10: ['wd0524_z001.trk',
                                         'wd0570_z001.trk',
                                         'wd0593_z001.trk',
                                         'wd0609_z001.trk',
                                         'wd0632_z001.trk',
                                         'wd0659_z001.trk',
                                         'wd0705_z001.trk',
                                         'wd0767_z001.trk',
                                         'wd0837_z001.trk',
                                         'wd0877_z001.trk'],
                                    30: ['0524_003_sflhdiff.trk',
                                         '0570_003_sflhdiff.trk',
                                         '0593_003_sflhdiff.trk',
                                         '0610_003_sflhdiff.trk',
                                         '0632_003_sflhdiff.trk',
                                         '0659_003_sflhdiff.trk',
                                         '0705_003_sflhdiff.trk',
                                         '1000_003_sflhdiff.trk'],
                                    60: ['0524_006_sflhdiff.trk',
                                         '0570_006_sflhdiff.trk',
                                         '0593_006_sflhdiff.trk',
                                         '0610_006_sflhdiff.trk',
                                         '0632_006_sflhdiff.trk',
                                         '0659_006_sflhdiff.trk',
                                         '0705_006_sflhdiff.trk',
                                         '1000_006_sflhdiff.trk']}
    folders_paths_by_metallicities = {
        1:  './da_cooling_tables/Z0001',
        10: './da_cooling_tables/Z001',
        30: './da_cooling_tables/Z003',
        60: './da_cooling_tables/Z006'}

    base_dir = os.path.dirname(__file__)

    for metallicity, folder_path in folders_paths_by_metallicities.items():
        files_paths = files_paths_by_metallicities[metallicity]
        files_paths_by_metallicities[metallicity] = [
            os.path.join(base_dir, folder_path, file_path)
            for file_path in files_paths]

    metallicities_per_thousand = [1, 10, 30, 60]
    masses = [np.array([0.505, 0.553, 0.593, 0.627, 0.660, 0.692, 0.863]),
              np.array([0.524, 0.570, 0.593, 0.609, 0.632,
                        0.659, 0.705, 0.767, 0.837, 0.877]),
              np.array([0.524, 0.570, 0.593, 0.609,
                        0.632, 0.659, 0.705, 1.000]),
              np.array([0.524, 0.570, 0.593, 0.609,
                        0.632, 0.659, 0.705, 1.000])]
    pre_wd_lifetimes = [
        np.zeros(len(files_paths_by_metallicities[1])),
        np.zeros(len(files_paths_by_metallicities[10])),
        np.array([11.117, 2.7004, 1.699, 1.2114, 0.9892, 0.7422, 0.4431, 0.0]),
        np.array([11.117, 2.7004, 1.699, 1.2114, 0.9892, 0.7422, 0.4431, 0.0])]

    cooling_sequences_by_metallicities = dict(metallicities_cooling_sequences(
        metallicities_per_thousand,
        files_paths_by_metallicities,
        masses,
        pre_wd_lifetimes,
        rows_count))

    fill_types_by_metallicities = {1: 1,
                                   10: 1,
                                   30: 2,
                                   60: 2}

    for metallicity, fill_type in fill_types_by_metallicities.items():
        read_files(
            files_paths=files_paths_by_metallicities[metallicity],
            cooling_sequence=cooling_sequences_by_metallicities[metallicity],
            fill_type=fill_type,
            max_rows=rows_count)

    return cooling_sequences_by_metallicities


def metallicities_cooling_sequences(
        metallicities: List[int],
        files_paths_by_metallicities: Dict[int, List[str]],
        masses: List[np.ndarray],
        pre_wd_lifetimes: List[np.ndarray],
        rows_count: int
        ) -> Iterator[Tuple[int, Dict[str, np.ndarray]]]:
    for metallicity, mass, pre_wd_lifetime in zip(metallicities,
                                                  masses,
                                                  pre_wd_lifetimes):
        files_count = len(files_paths_by_metallicities[metallicity])
        shape = (files_count, rows_count)
        cooling_sequence = dict(mass=mass,
                                pre_wd_lifetime=pre_wd_lifetime,
                                cooling_time=nan_matrix(shape),
                                effective_temperature=nan_matrix(shape),
                                surface_gravity=nan_matrix(shape),
                                luminosity=nan_matrix(shape),
                                rows_counts=np.empty(files_count, dtype='i'))
        yield metallicity, cooling_sequence


def nan_matrix(shape: Tuple[int, ...]) -> np.ndarray:
    return np.full(shape, np.nan)


def read_files(files_paths: List[str],
               cooling_sequence: Dict[str, np.ndarray],
               fill_type: int,
               max_rows: int) -> None:
    cooling_time = cooling_sequence['cooling_time']
    effective_temperature = cooling_sequence['effective_temperature']
    surface_gravity = cooling_sequence['surface_gravity']
    luminosity = cooling_sequence['luminosity']
    pre_wd_lifetime = cooling_sequence['pre_wd_lifetime']
    rows_counts = cooling_sequence['rows_counts']

    for file_path_index, file_path in enumerate(files_paths):
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file,
                                    delimiter=' ',
                                    skipinitialspace=True)
            for row_index, row in enumerate(csv_reader):
                if row_index == max_rows:
                    break
                # In Fortran indexation starts from 1
                rows_counts[file_path_index] = row_index + 1
                luminosity[file_path_index, row_index] = float(row[0])
                effective_temperature[file_path_index, row_index] = (
                    10. ** float(row[1]))
                if fill_type == 1:
                    cooling_time[file_path_index, row_index] = (float(row[4])
                                                                / 1000.0)
                    surface_gravity[file_path_index, row_index] = float(
                        row[11])
                if fill_type == 2:
                    cooling_time[file_path_index, row_index] = (
                        10. ** float(row[8]) / 1000.
                        - pre_wd_lifetime[file_path_index])
                    surface_gravity[file_path_index, row_index] = float(
                        row[22])