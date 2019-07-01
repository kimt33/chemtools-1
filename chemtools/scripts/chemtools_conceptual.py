#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ChemTools is a collection of interpretive chemical tools for
# analyzing outputs of the quantum chemistry calculations.
#
# Copyright (C) 2016-2019 The ChemTools Development Team
#
# This file is part of ChemTools.
#
# ChemTools is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# ChemTools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --
# pragma pylint: disable=invalid-name
"""Conceptual Density Functional Theory Script."""


from chemtools import print_vmd_script_isosurface
from chemtools import GlobalConceptualDFT, LocalConceptualDFT, CondensedConceptualDFT
from chemtools.scripts.common import help_cube, load_molecule_and_grid


description_global = """
Print global conceptual density functional theory (DFT) reactivity descriptors.
"""



def parse_args_global(subparser):
    """Parse command-line arguments for computing global conceptual DFT indicators."""
    # required arguments
    subparser.add_argument("model", help="energy model.")
    subparser.add_argument(
        "fname",
        nargs="*",
        help="wave-function file(s). If more than one file is given, finite difference (FD) "
             "approach is invoked instead of frontier molecular orbital (FMO) approach.")


def parse_args_local(subparser):
    """Parse command-line arguments for computing local conceptual DFT indicators."""
    # description message
    # description = """ """

    # get property list from LocalConceptualDFT's parent class
    # property_list = [
    #     name for name, func in BaseLocalTool.__dict__.items()
    #     if isinstance(func, property)
    # ]
    property_list = [
        'ff_plus',
        'ff_minus',
        'ff_zero',
        'fukui_function',
        'dual_descriptor',
        # add more property
    ]

    # required arguments
    subparser.add_argument('model', help='Energy model.')
    subparser.add_argument(
        'prop',
        type=str,
        choices=property_list,
        metavar='property',
        help='The local property for plotting iso-surface. '
        'Choices: {{{}}}'.format(", ".join(property_list)))
    subparser.add_argument(
        'output', help='Name of generated cube files and vmd script.')
    subparser.add_argument(
        'fname',
        nargs='*',
        help='Wave-function file(s). Supported formats: fchk, mkl, molden.'
        'input, wfn. If one files is provided, the frontier moleculer orbital'
        '(FMO) approach is invoked, otherwise the finite difference (FD)'
        'approach is taken.')

    # optional arguments
    subparser.add_argument(
        '--cube',
        default='0.2,4.0',
        type=str,
        metavar='N',
        help=help_cube)
    subparser.add_argument(
        '--isosurface',
        default=0.005,
        type=float,
        help='iso-surface value of local property to visualize. '
        '[default=%(default)s]')
    # parser.add_argument('--color', default='b', type=str,
    #                     help='color of reduced density gradient vs. signed density scatter plot.'
    #                     '[default=%(default)s]')


def parse_args_condensed(subparser):
    """Parse command-line arguments for computing local conceptual DFT indicators."""
    # description message
    # description = """ """

    # get property list from LocalConceptualDFT's parent class
    # property_list = [
    #     name for name, func in BaseLocalTool.__dict__.items()
    #     if isinstance(func, property)
    # ]
    property_list = [
        'ff_plus',
        'ff_minus',
        'ff_zero',
        'fukui_function',
        'dual_descriptor',
        # add more property
    ]

    # required arguments
    subparser.add_argument('model', help='Energy model.')
    subparser.add_argument(
        'prop',
        type=str,
        choices=property_list,
        metavar='property',
        help='The local property for plotting iso-surface. '
        'Choices: {{{}}}'.format(", ".join(property_list)))
    subparser.add_argument(
        'fname',
        nargs='*',
        help='Wave-function file(s). Supported formats: fchk, mkl, molden.'
        'input, wfn. If one files is provided, the frontier moleculer orbital'
        '(FMO) approach is invoked, otherwise the finite difference (FD)'
        'approach is taken.')

    subparser.add_argument(
        '--approach',
        type=str,
        default='FMR',
        choices=['FMR', 'RMF'],
        metavar='property',
        help='choose between fragment of molecular response or response of molecular fragment.'
        'Choices: {{{}}}'.format(", ".join(property_list)) +
        '[default=%(default)s]')

    subparser.add_argument(
        '--scheme',
        type=str,
        default='h',
        choices=['h', 'hi', 'mbis'],
        metavar='property',
        help='partitioning scheme.'
        'Choices: {{{}}}'.format(", ".join(property_list)) +
             '[default=%(default)s]')


def main_conceptual_global(args):
    """Build GlobalConceptualDFT class and print global descriptors."""
    # build global tool
    model = GlobalConceptualDFT.from_file(args.fname, args.model)
    # print available descriptors
    print(model)


def main_conceptual_local(args):
    """Build LocalConceptualDFT class and dump a cube file of local descriptor."""
    # load molecule & cubic grid
    mol, cube = load_molecule_and_grid(args.fname, args.cube)

    # build global tool
    model = LocalConceptualDFT.from_file(args.fname, args.model, cube.points)
    # check whether local property exists
    if not hasattr(model, args.prop):
        raise ValueError('The {0} local conceptual DFT class does not contain '
                         '{1} attribute.'.format(args.model, args.prop))
    if callable(getattr(model, args.prop)):
        raise ValueError(
            'The {0} argument is a method, please provide an attribute of '
            '{1} local conceptual DFT.'.format(args.prop, args.model))

    # name of files
    cubfname = '{0}.cube'.format(args.output)
    vmdfname = '{0}.vmd'.format(args.output)
    # dump cube file of local property
    cube.generate_cube(cubfname, getattr(model, args.prop))
    # generate VMD scripts for visualizing iso-surface with VMD
    print_vmd_script_isosurface(vmdfname, cubfname, isosurf=args.isosurface, material='BlownGlass')


def main_conceptual_condensed(args):
    """Build LocalConceptualDFT class and dump a cube file of local descriptor."""

    # build condensed tool
    model = CondensedConceptualDFT.from_file(args.fname, model=args.model, scheme=args.scheme,
                                             approach=args.approach)
    # check whether local property exists
    if not hasattr(model, args.prop):
        raise ValueError('The {0} condensed conceptual DFT class does not contain '
                         '{1} attribute.'.format(args.model, args.prop))
    if callable(getattr(model, args.prop)):
        raise ValueError(
            'The {0} argument is a method, please provide an attribute of '
            '{1} local conceptual DFT.'.format(args.prop, args.model))

    prop = getattr(model, args.prop)

    print("")
    print('Atomic contribution of %s for scheme=%s & approach %s:' % (args.prop, args.scheme.upper(), args.approach))
    for index in range(len(model.numbers)):
        print('% 3i   % 3i   %10.6f' % (index, model.numbers[index], prop[index]))
    print("")
