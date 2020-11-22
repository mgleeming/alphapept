# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_fasta.ipynb (unless otherwise specified).

__all__ = ['get_missed_cleavages', 'cleave_sequence', 'count_missed_cleavages', 'count_internal_cleavages', 'parse',
           'list_to_numba', 'get_decoy_sequence', 'swap_KR', 'swap_AL', 'get_decoys', 'add_decoy_tag', 'add_fixed_mods',
           'get_mod_pos', 'get_isoforms', 'add_variable_mods', 'add_fixed_mod_terminal', 'add_fixed_mods_terminal',
           'add_variable_mods_terminal', 'get_unique_peptides', 'generate_peptides', 'get_precmass', 'get_fragmass',
           'get_frag_dict', 'get_spectrum', 'get_spectra', 'read_fasta_file', 'read_fasta_file_entries',
           'check_sequence', 'add_to_pept_dict', 'merge_pept_dicts', 'generate_fasta_list', 'generate_database',
           'generate_spectra', 'block_idx', 'blocks', 'digest_fasta_block', 'generate_database_parallel', 'mass_dict',
           'pept_dict_from_search', 'save_database', 'read_database']

# Cell
from alphapept import constants
import re

def get_missed_cleavages(sequences, n_missed_cleavages):
    """
    Combine cleaved sequences to get sequences with missed cleavages
    """
    missed = []
    for k in range(len(sequences)-n_missed_cleavages):
        missed.append(''.join(sequences[k-1:k+n_missed_cleavages]))

    return missed


def cleave_sequence(
    sequence="",
    num_missed_cleavages=0,
    protease="trypsin",
    min_length=6,
    max_length=65,
    **kwargs
):
    """
    Cleave a sequence with a given protease. Filters to have a minimum and maximum length.
    """

    proteases = constants.protease_dict
    pattern = proteases[protease]

    p = re.compile(pattern)

    cutpos = [m.start()+1 for m in p.finditer(sequence)]
    cutpos.insert(0,0)
    cutpos.append(len(sequence))

    base_sequences = [sequence[cutpos[i]:cutpos[i+1]] for i in range(len(cutpos)-1)]

    sequences = base_sequences.copy()

    for i in range(1, num_missed_cleavages+1):
        sequences.extend(get_missed_cleavages(base_sequences, i))

    sequences = [_ for _ in sequences if len(_)>=min_length and len(_)<=max_length]

    return sequences

# Cell
import re
from alphapept import constants

def count_missed_cleavages(sequence="", protease="trypsin", **kwargs):
    """
    Counts the number of missed cleavages for a given sequence and protease
    """
    proteases = constants.protease_dict
    protease = proteases[protease]
    p = re.compile(protease)
    n_missed = len(p.findall(sequence))
    return n_missed

def count_internal_cleavages(sequence="", protease="trypsin", **kwargs):
    """
    Counts the number of internal cleavage sites for a given sequence and protease
    """
    proteases = constants.protease_dict
    protease = proteases[protease]
    match = re.search(protease,sequence[-1]+'_')
    if match:
        n_internal = 0
    else:
        n_internal = 1
    return n_internal

# Cell
from numba import njit
from numba.typed import List

@njit
def parse(peptide):
    """
    Parser to parse peptide strings
    """
    if "_" in peptide:
        peptide = peptide.split("_")[0]
    parsed = List()
    string = ""

    for i in peptide:
        string += i
        if i.isupper():
            parsed.append(string)
            string = ""

    return parsed

def list_to_numba(a_list):
    numba_list = List()

    for element in a_list:
        numba_list.append(element)

    return numba_list

# Cell
@njit
def get_decoy_sequence(peptide, pseudo_reverse=False, AL_swap=False, KR_swap = False):
    """
    Reverses a sequence and adds the '_decoy' tag.

    """
    pep = parse(peptide)
    if pseudo_reverse:
        rev_pep = pep[:-1][::-1]
        rev_pep.append(pep[-1])
    else:
        rev_pep = pep[::-1]

    if AL_swap:
        rev_pep = swap_AL(rev_pep)

    if KR_swap:
        rev_pep = swap_KR(rev_pep)

    rev_pep = "".join(rev_pep)

    return rev_pep


@njit
def swap_KR(peptide):
    """
    Swaps a terminal K or R. Note: Only if AA is not modified.
    """
    if peptide[-1] == 'K':
        peptide[-1] = 'R'
    elif peptide[-1] == 'R':
        peptide[-1] = 'K'

    return peptide


@njit
def swap_AL(peptide):
    """
    Swaps a A with L. Note: Only if AA is not modified.
    """
    i = 0
    while i < len(range(len(peptide) - 1)):
        if peptide[i] == "A":
            peptide[i] = peptide[i + 1]
            peptide[i + 1] = "A"
            i += 1
        elif peptide[i] == "L":
            peptide[i] = peptide[i + 1]
            peptide[i + 1] = "L"
            i += 1
        i += 1

    #aa_table = "GAVLIFMPWSCTYHKRQEND"
    #DiaNN_table  = "LLLVVLLLLTSSSSLLNDQE"

    #idx = aa_table.find(peptide[-2])
    #peptide[-2] = decoy_table[idx]

    return peptide

def get_decoys(peptide_list, pseudo_reverse=False, AL_swap=False, KR_swap = False, **kwargs):
    """
    Wrapper to get decoys for lists of peptides
    """
    decoys = []
    decoys.extend([get_decoy_sequence(peptide, pseudo_reverse, AL_swap, KR_swap) for peptide in peptide_list])
    return decoys

def add_decoy_tag(peptides):
    """
    Adds a _decoy tag to a list of peptides
    """
    return [peptide + "_decoy" for peptide in peptides]

# Cell
def add_fixed_mods(seqs, mods_fixed, **kwargs):
    """
    Adds fixed modifications to sequences.
    """
    if not mods_fixed:
        return seqs
    else:
        for mod_aa in mods_fixed:
            seqs = [seq.replace(mod_aa[-1], mod_aa) for seq in seqs]
        return seqs

# Cell
def get_mod_pos(variable_mods_r, sequence):
    """
    Returns a list with of tuples with all possibilities for modified an unmodified AAs.
    """
    modvar = []
    for c in sequence:
        if c in variable_mods_r.keys():
            modvar.append((c, variable_mods_r[c]))
        else:
            modvar.append((c,))

    return modvar

# Cell

from itertools import product
def get_isoforms(variable_mods_r, sequence, max_isoforms):
    """
    Function to generate isoforms for a given peptide - returns a list of isoforms.
    The original sequence is included in the list
    """
    modvar = get_mod_pos(variable_mods_r, sequence)
    isoforms = []
    i = 0
    for o in product(*modvar):
        if i < max_isoforms:
            i += 1
            isoforms.append("".join(o))

        else:
            break

    return isoforms

# Cell
from itertools import chain

def add_variable_mods(peptide_list, mods_variable, max_isoforms, **kwargs):
    if not mods_variable:
        return peptide_list
    else:
        mods_variable_r = {}
        for _ in mods_variable:
            mods_variable_r[_[-1]] = _

        peptide_list = [get_isoforms(mods_variable_r, peptide, max_isoforms) for peptide in peptide_list]
        return list(chain.from_iterable(peptide_list))

# Cell
def add_fixed_mod_terminal(peptides, mod):
    """
    Adds fixed terminal modifications
    """
    # < for left side (N-Term), > for right side (C-Term)
    if "<^" in mod: #Any n-term, e.g. a<^
        peptides = [mod[:-2] + peptide for peptide in peptides]
    elif ">^" in mod: #Any c-term, e.g. a>^
        peptides = [peptide[:-1] + mod[:-2] + peptide[-1] for peptide in peptides]
    elif "<" in mod: #only if specific AA, e.g. ox<C
        peptides = [peptide[0].replace(mod[-1], mod[:-2]+mod[-1]) + peptide[1:] for peptide in peptides]
    elif ">" in mod:
        peptides = [peptide[:-1] + peptide[-1].replace(mod[-1], mod[:-2]+mod[-1]) for peptide in peptides]
    else:
        # This should not happen
        raise ("Invalid fixed terminal modification {}.".format(key))
    return peptides

def add_fixed_mods_terminal(peptides, mods_fixed_terminal, **kwargs):
    """
    Wrapper to add fixed mods on sequences and lists of mods
    """
    if mods_fixed_terminal == []:
        return peptides
    else:
        # < for left side (N-Term), > for right side (C-Term)
        for key in mods_fixed_terminal:
            peptides = add_fixed_mod_terminal(peptides, key)
        return peptides

# Cell
def add_variable_mods_terminal(peptides, mods_variable_terminal, **kwargs):
    "Function to add variable terminal modifications"
    if not mods_variable_terminal:
        return peptides
    else:
        new_peptides_n = peptides.copy()

        for key in mods_variable_terminal:
            if "<" in key:
                # Only allow one variable mod on one end
                new_peptides_n.extend(
                    add_fixed_mod_terminal(peptides, key)
                )
        new_peptides_n = get_unique_peptides(new_peptides_n)
        # N complete, let's go for c-terminal
        new_peptides_c = new_peptides_n
        for key in mods_variable_terminal:
            if ">" in key:
                # Only allow one variable mod on one end
                new_peptides_c.extend(
                    add_fixed_mod_terminal(new_peptides_n, key)
                )

        return get_unique_peptides(new_peptides_c)

def get_unique_peptides(peptides):
    return list(set(peptides))

# Cell
def generate_peptides(peptide, **kwargs):
    """
    Wrapper to get modified peptides from a peptide
    """
    mod_peptide = add_fixed_mods_terminal([peptide], kwargs['mods_fixed_terminal_prot'])
    mod_peptide = add_variable_mods_terminal(mod_peptide, kwargs['mods_variable_terminal_prot'])

    peptides = []
    [peptides.extend(cleave_sequence(_, **kwargs)) for _ in mod_peptide]

    #Regular peptides
    mod_peptides = add_fixed_mods(peptides, **kwargs)
    mod_peptides = add_fixed_mods_terminal(mod_peptides, **kwargs)
    mod_peptides = add_variable_mods_terminal(mod_peptides, **kwargs)
    mod_peptides = add_variable_mods(mod_peptides, **kwargs)

    #Decoys:
    decoy_peptides = get_decoys(peptides, **kwargs)

    mod_peptides_decoy = add_fixed_mods(decoy_peptides, **kwargs)
    mod_peptides_decoy = add_fixed_mods_terminal(mod_peptides_decoy, **kwargs)
    mod_peptides_decoy = add_variable_mods_terminal(mod_peptides_decoy, **kwargs)
    mod_peptides_decoy = add_variable_mods(mod_peptides_decoy, **kwargs)

    mod_peptides_decoy = add_decoy_tag(mod_peptides_decoy)

    mod_peptides.extend(mod_peptides_decoy)

    return mod_peptides

# Cell
from numba import njit
from numba.typed import List
import numpy as np

@njit
def get_precmass(parsed_pep, mass_dict):
    """
    Calculate the mass of the neutral precursor
    """
    tmass = mass_dict["H2O"]
    for _ in parsed_pep:
        tmass += mass_dict[_]

    return tmass

# Cell

@njit
def get_fragmass(parsed_pep, mass_dict):
    """
    Calculate the masses of the fragment ions
    """
    n_frags = (len(parsed_pep) - 1) * 2

    frag_masses = np.zeros(n_frags, dtype=np.float64)
    frag_type = np.zeros(n_frags, dtype=np.int8)

    # b-ions -> 0
    n_frag = 0
    frag_m = mass_dict["Proton"]
    for _ in parsed_pep[:-1]:
        frag_m += mass_dict[_]
        frag_masses[n_frag] = frag_m
        frag_type[n_frag] = 0
        n_frag += 1

    # y-ions -> 1
    frag_m = mass_dict["Proton"] + mass_dict["H2O"]
    for _ in parsed_pep[::-1][:-1]:
        frag_m += mass_dict[_]
        frag_masses[n_frag] = frag_m
        frag_type[n_frag] = 1
        n_frag += 1

    return frag_masses, frag_type

# Cell
def get_frag_dict(parsed_pep, mass_dict):
    """
    Calculate the masses of the fragment ions
    """
    n_frags = (len(parsed_pep) - 1) * 2

    frag_dict = {}

    # b-ions -> 0
    n_frag = 0
    frag_m = mass_dict["Proton"]

    for _ in parsed_pep[:-1]:
        frag_m += mass_dict[_]
        n_frag += 1

        frag_dict['b' + str(n_frag)] = frag_m

    # y-ions -> 1
    n_frag = 0
    frag_m = mass_dict["Proton"] + mass_dict["H2O"]
    for _ in parsed_pep[::-1][:-1]:
        frag_m += mass_dict[_]
        n_frag += 1
        frag_dict['y' + str(n_frag)] = frag_m

    return frag_dict

# Cell
@njit
def get_spectrum(peptide, mass_dict):
    parsed_peptide = parse(peptide)

    fragmasses, fragtypes = get_fragmass(parsed_peptide, mass_dict)
    sortindex = np.argsort(fragmasses)
    fragmasses = fragmasses[sortindex]
    fragtypes = fragtypes[sortindex]

    precmass = get_precmass(parsed_peptide, mass_dict)

    return (precmass, peptide, fragmasses, fragtypes)

@njit
def get_spectra(peptides, mass_dict):
    spectra = List()

    for i in range(len(peptides)):
        spectra.append(get_spectrum(peptides[i], mass_dict))

    return spectra

# Cell
from Bio import SeqIO
import os
from glob import glob
import logging

def read_fasta_file(fasta_filename=""):
    """
    Read a FASTA file line by line
    """
    with open(fasta_filename, "rt") as handle:
        iterator = SeqIO.parse(handle, "fasta")
        while iterator:
            try:
                record = next(iterator)
                parts = record.id.split("|")  # pipe char
                if len(parts) > 1:
                    id = parts[1]
                else:
                    id = record.name
                sequence = str(record.seq)
                entry = {
                    "id": id,
                    "name": record.name,
                    "description": record.description,
                    "sequence": sequence,
                }

                yield entry
            except StopIteration:
                break


def read_fasta_file_entries(fasta_filename=""):
    """
    Function to count entries in fasta file
    """
    with open(fasta_filename, "rt") as handle:
        iterator = SeqIO.parse(handle, "fasta")
        count = 0
        while iterator:
            try:
                record = next(iterator)
                count+=1
            except StopIteration:
                break

        return count


def check_sequence(element, AAs):
    """
    Checks wheter a sequence from a FASTA entry contains valid AAs
    """
    if not set(element['sequence']).issubset(AAs):
        logging.error('This FASTA entry contains unknown AAs and will be skipped: \n {}\n'.format(element))
        return False
    else:
        return True

# Cell
def add_to_pept_dict(pept_dict, new_peptides, i):
    """
    Add peptides to the peptide dictionary
    """
    added_peptides = List()
    for peptide in new_peptides:
        if peptide in pept_dict:
            pept_dict[peptide].append(i)
        else:
            pept_dict[peptide] = [i]
            added_peptides.append(peptide)

    return pept_dict, added_peptides

# Cell

def merge_pept_dicts(list_of_pept_dicts):

    if len(list_of_pept_dicts) == 0:
        raise ValueError('Need to pass at least 1 element.')

    new_pept_dict = list_of_pept_dicts[0]

    for pept_dict in list_of_pept_dicts[1:]:

        for key in pept_dict.keys():
            if key in new_pept_dict:
                for element in pept_dict[key]:
                    new_pept_dict[key].append(element)
            else:
                new_pept_dict[key] = pept_dict[key]

    return new_pept_dict

# Cell
from collections import OrderedDict

def generate_fasta_list(fasta_paths, callback = None, **kwargs):
    """
    Function to generate a database from a fasta file
    """
    fasta_list = []

    fasta_dict = OrderedDict()

    fasta_index = 0

    if type(fasta_paths) is str:
        fasta_paths = [fasta_paths]
        n_fastas = 1

    elif type(fasta_paths) is list:
        n_fastas = len(fasta_paths)

    for f_id, fasta_file in enumerate(fasta_paths):
        n_entries = read_fasta_file_entries(fasta_file)

        fasta_generator = read_fasta_file(fasta_file)

        for element in fasta_generator:
            if check_sequence(element, constants.AAs):
                fasta_list.append(element)
                fasta_dict[fasta_index] = element
                fasta_index += 1

    return fasta_list, fasta_dict


def generate_database(mass_dict, fasta_paths, callback = None, **kwargs):
    """
    Function to generate a database from a fasta file
    """
    to_add = List()
    fasta_dict = OrderedDict()
    fasta_index = 0

    pept_dict = {}

    if type(fasta_paths) is str:
        fasta_paths = [fasta_paths]
        n_fastas = 1

    elif type(fasta_paths) is list:
        n_fastas = len(fasta_paths)

    for f_id, fasta_file in enumerate(fasta_paths):
        n_entries = read_fasta_file_entries(fasta_file)

        fasta_generator = read_fasta_file(fasta_file)

        for element in fasta_generator:
            if check_sequence(element, constants.AAs):
                fasta_dict[fasta_index] = element
                mod_peptides = generate_peptides(element["sequence"], **kwargs)
                pept_dict, added_seqs = add_to_pept_dict(pept_dict, mod_peptides, fasta_index)
                if len(added_seqs) > 0:
                    to_add.extend(added_seqs)

            fasta_index += 1

            if callback:
                callback(fasta_index/n_entries/n_fastas+f_id)

    return to_add, pept_dict, fasta_dict


def generate_spectra(to_add, mass_dict, callback = None):
    """
    Function to generate a database from a fasta file
    """

    if len(to_add) > 0:

        if callback: #Chunk the spectra to get a progress_bar
            spectra = []

            stepsize = int(np.ceil(len(to_add)/1000))

            for i in range(0, len(to_add), stepsize):
                sub = to_add[i:i + stepsize]
                spectra.extend(get_spectra(sub, mass_dict))
                callback((i+1)/len(to_add))

        else:
            spectra = get_spectra(to_add, mass_dict)
    else:
        raise ValueError("No spectra to generate.")

    return spectra

# Cell
from multiprocessing import Pool
from alphapept import constants
mass_dict = constants.mass_dict

def block_idx(len_list, block_size = 1000):
    """
    Create indices for a list of length len_list
    """
    blocks = []
    start = 0
    end = 0

    while end <= len_list:
        end += block_size
        blocks.append((start, end))
        start = end

    return blocks

def blocks(l, n):
    """
    Create blocks from a given list
    """
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))

def digest_fasta_block(to_process):
    """
    Digest and create spectra for a whole fasta_block
    """

    fasta_index, fasta_block, settings = to_process

    to_add = List()

    f_index = 0

    pept_dict = {}
    for element in fasta_block:
        sequence = element["sequence"]
        mod_peptides = generate_peptides(sequence, **settings['fasta'])
        pept_dict, added_peptides = add_to_pept_dict(pept_dict, mod_peptides, fasta_index+f_index)

        if len(added_peptides) > 0:
            to_add.extend(added_peptides)
        f_index += 1

    spectra = []
    if len(to_add) > 0:
        for specta_block in blocks(to_add, settings['fasta']['spectra_block']):
            spectra.extend(generate_spectra(specta_block, mass_dict))

    return (spectra, pept_dict)

def generate_database_parallel(settings, callback = None):
    """
    Function to generate a database from a fasta file
    """
    n_processes = settings['general']['n_processes']

    fasta_list, fasta_dict = generate_fasta_list(**settings['fasta'])

    blocks = block_idx(len(fasta_list), settings['fasta']['fasta_block'])

    to_process = [(idx_start, fasta_list[idx_start:idx_end], settings) for idx_start, idx_end in  blocks]

    spectra = []
    pept_dicts = []
    with Pool(n_processes) as p:
        max_ = len(to_process)
        for i, _ in enumerate(p.imap_unordered(digest_fasta_block, to_process)):
            if callback:
                callback((i+1)/max_)
            spectra.extend(_[0])
            pept_dicts.append(_[1])

    spectra = sorted(spectra, key=lambda x: x[1])
    spectra_set = [spectra[idx] for idx in range(len(spectra)-1) if spectra[idx][1] != spectra[idx+1][1]]
    spectra_set.append(spectra[-1])

    pept_dict = merge_pept_dicts(pept_dicts)

    return spectra_set, pept_dict, fasta_dict

# Cell
def pept_dict_from_search(settings):
    """
    Generates a peptide dict from a large search
    """

    paths = settings['experiment']['files']

    bases = [os.path.splitext(_)[0]+'.hdf' for _ in paths]

    all_dfs = []
    for _ in bases:
        try:
            df = pd.read_hdf(_, key='peptide_fdr')
        except KeyError:
            df = pd.DataFrame()

        if df > 0:
            all_dfs.append(df)

    df = pd.concat(all_dfs)

    df['fasta_index'] = df['fasta_index'].str.split(',')

    lst_col = 'fasta_index'

    df_ = pd.DataFrame({
          col:np.repeat(df[col].values, df[lst_col].str.len())
          for col in df.columns.drop(lst_col)}
        ).assign(**{lst_col:np.concatenate(df[lst_col].values)})[df.columns]

    df_['fasta_index'] = df_['fasta_index'].astype('int')
    df_grouped = df_.groupby(['sequence'])['fasta_index'].unique()

    pept_dict = {}
    for keys, vals in zip(df_grouped.index, df_grouped.values):
        pept_dict[keys] = vals.tolist()

    return pept_dict

# Cell
import alphapept.io
import pandas as pd

def save_database(spectra, pept_dict, fasta_dict, database_path, **kwargs):
    """
    Function to save a database to the *.hdf format.
    """

    precmasses, seqs, fragmasses, fragtypes = zip(*spectra)
    sortindex = np.argsort(precmasses)

    to_save = {}

    to_save["precursors"] = np.array(precmasses)[sortindex]
    to_save["seqs"] = np.array(seqs, dtype=object)[sortindex]
    to_save["proteins"] = pd.DataFrame(fasta_dict).T

    to_save["fragmasses"] = alphapept.io.list_to_numpy_f32(np.array(fragmasses, dtype='object')[sortindex])
    to_save["fragtypes"] = alphapept.io.list_to_numpy_f32(np.array(fragtypes, dtype='object')[sortindex])

    to_save["bounds"] = np.sum(to_save['fragmasses']>=0,axis=0).astype(np.int64)

    db_file = alphapept.io.HDF_File(database_path, is_new_file=True)
    for key, value in to_save.items():
        db_file.write(value, dataset_name=key)

    peps = np.array(list(pept_dict), dtype=object)
    indices = np.empty(len(peps) + 1, dtype=np.int64)
    indices[0] = 0
    indices[1:] = np.cumsum([len(pept_dict[i]) for i in peps])
    proteins = np.concatenate([pept_dict[i] for i in peps])

    db_file.write("peptides")
    db_file.write(
        peps,
        dataset_name="sequences",
        group_name="peptides"
    )
    db_file.write(
        indices,
        dataset_name="protein_indptr",
        group_name="peptides"
    )
    db_file.write(
        proteins,
        dataset_name="protein_indices",
        group_name="peptides"
    )

# Cell
import collections

def read_database(database_path:str, array_name:str=None):
    db_file = alphapept.io.HDF_File(database_path)
    if array_name is None:
        db_data = {
            key: db_file.read(
                dataset_name=key
            ) for key in db_file.read() if key not in (
                "proteins",
                "peptides"
            )
        }
        db_data["fasta_dict"] = np.array(
            collections.OrderedDict(db_file.read(dataset_name="proteins").T)
        )
        peps = db_file.read(dataset_name="sequences", group_name="peptides")
        protein_indptr = db_file.read(
            dataset_name="protein_indptr",
            group_name="peptides"
        )
        protein_indices = db_file.read(
            dataset_name="protein_indices",
            group_name="peptides"
        )
        db_data["pept_dict"] = np.array(
            {
                pep: (protein_indices[s: e]).tolist() for pep, s, e in zip(
                    peps,
                    protein_indptr[:-1],
                    protein_indptr[1:],
                )
            }
        )
        db_data["seqs"] = db_data["seqs"].astype(str)
    else:
        db_data = db_file.read(dataset_name=array_name)
    return db_data